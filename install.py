#!/usr/bin/env python3
"""Install hooks + skill for claude-chords.

What it does:
  1. Symlinks  skill/SKILL.md  ->  ~/.claude/skills/tone/SKILL.md
  2. Backs up  ~/.claude/settings.json  to  settings.json.bak.<timestamp>
  3. Adds a SessionStart hook running register_session.py.
  4. Replaces UserPromptSubmit / Stop / Notification audio hooks with calls
     to play_event.py. The dispatcher itself falls back to your existing
     wav files when no chord is assigned, so unassigned sessions sound
     identical to before.

Run:  python3 install.py            # installs
      python3 install.py --uninstall  # restores most-recent backup
"""
from __future__ import annotations

import json
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BIN = ROOT / "bin"
SETTINGS = Path.home() / ".claude" / "settings.json"
FALLBACKS_PATH = ROOT / "state" / "fallbacks.json"

# Skills installed by this project: (template_name, install_subdir).
SKILLS: list[tuple[str, str]] = [
    ("SKILL.md.tmpl",         "tone"),          # /tone — chord assignment
    ("LEITMOTIF.md.tmpl",     "leitmotif"),     # /leitmotif — composed motif
    ("PUSH_FANFARE.md.tmpl",  "push-fanfare"),  # /push-fanfare — toggle
]

# Shell function appended to ~/.bash_profile. Wraps git, plays the victory
# fanfare wav after a successful `git push` IF the marker file exists.
BASH_PROFILE = Path.home() / ".bash_profile"
SHELL_BLOCK_BEGIN = "# >>> claude-chords push fanfare >>>"
SHELL_BLOCK_END   = "# <<< claude-chords push fanfare <<<"


def shell_block(project_root: Path) -> str:
    marker = project_root / "state" / "push_fanfare.enabled"
    wav = project_root / "compositions" / "output" / "victory_fanfare.wav"
    return (
        f"{SHELL_BLOCK_BEGIN}\n"
        f"# Plays a victory fanfare after a successful `git push`, IF\n"
        f"# the marker file is present. Toggle via `/push-fanfare on|off`.\n"
        f"git() {{\n"
        f'  if [ "$1" = "push" ]; then\n'
        f'    command git "$@"\n'
        f'    local rc=$?\n'
        f'    if [ $rc -eq 0 ] && [ -f "{marker}" ] && [ -f "{wav}" ]; then\n'
        f'      (afplay "{wav}" >/dev/null 2>&1 &)\n'
        f"    fi\n"
        f"    return $rc\n"
        f"  fi\n"
        f'  command git "$@"\n'
        f"}}\n"
        f"{SHELL_BLOCK_END}\n"
    )


def install_shell_block() -> None:
    """Idempotent append to ~/.bash_profile. Replaces an existing block if
    one is present (so paths get refreshed if the user moves the project)."""
    block = shell_block(ROOT)
    if BASH_PROFILE.exists():
        existing = BASH_PROFILE.read_text()
    else:
        existing = ""
    # Strip any prior block
    if SHELL_BLOCK_BEGIN in existing and SHELL_BLOCK_END in existing:
        before, _, rest = existing.partition(SHELL_BLOCK_BEGIN)
        _, _, after = rest.partition(SHELL_BLOCK_END)
        # Preserve a single trailing newline at the seam.
        existing = before.rstrip() + "\n" + after.lstrip()
    new = existing.rstrip() + "\n\n" + block
    BASH_PROFILE.write_text(new)
    print(f"  shell: appended push-fanfare function to {BASH_PROFILE}")
    print(f"         (open a new shell tab or `source {BASH_PROFILE}` to activate)")


def remove_shell_block() -> None:
    if not BASH_PROFILE.exists():
        return
    existing = BASH_PROFILE.read_text()
    if SHELL_BLOCK_BEGIN not in existing:
        return
    before, _, rest = existing.partition(SHELL_BLOCK_BEGIN)
    _, _, after = rest.partition(SHELL_BLOCK_END)
    new = before.rstrip() + "\n" + after.lstrip()
    BASH_PROFILE.write_text(new.rstrip() + "\n")
    print(f"  shell: removed push-fanfare function from {BASH_PROFILE}")

# Each hook command is wrapped to background and silence output.
def hook_cmd(event: str) -> str:
    # No shell backgrounding here: `( cmd ) &` breaks stdin propagation, so
    # the python script never sees the session_id JSON. The script itself
    # detaches afplay via Popen(start_new_session=True), which keeps the
    # audio non-blocking. The python process exits in well under a second.
    return f"python3 {BIN / 'play_event.py'} {event}"

def session_start_cmd() -> str:
    return f"python3 {BIN / 'register_session.py'}"


def install_skills() -> None:
    """Render every (template, subdir) pair in SKILLS to ~/.claude/skills/<subdir>/SKILL.md."""
    for tmpl_name, subdir in SKILLS:
        tmpl_path = ROOT / "skill" / tmpl_name
        dst_dir = Path.home() / ".claude" / "skills" / subdir
        dst = dst_dir / "SKILL.md"
        dst_dir.mkdir(parents=True, exist_ok=True)
        rendered = tmpl_path.read_text().replace("{{PROJECT_ROOT}}", str(ROOT))
        if dst.is_symlink() or dst.exists():
            dst.unlink()
        dst.write_text(rendered)
        print(f"  skill: rendered {tmpl_name} -> {dst}")


def extract_fallbacks_from_settings(settings: dict) -> dict:
    """Pull `afplay <wav>` paths out of existing event hook commands so we
    can preserve the user's prior default sounds when no chord is assigned."""
    found: dict[str, str] = {}
    hooks = settings.get("hooks", {})
    for event in ("UserPromptSubmit", "Stop", "Notification"):
        for entry in hooks.get(event, []):
            for h in entry.get("hooks", []):
                cmd = h.get("command", "")
                # Match the first afplay-with-path occurrence.
                import re
                m = re.search(r"afplay\s+(\S+\.(?:wav|aiff|mp3|m4a))", cmd)
                if m:
                    found[event] = m.group(1)
                    break
            if event in found:
                break
    return found


def maybe_seed_fallbacks(prev_settings: dict) -> None:
    """If state/fallbacks.json doesn't exist yet, seed it from any afplay paths
    in the user's previous hook commands. Skips creation if no paths found."""
    if FALLBACKS_PATH.exists():
        return
    extracted = extract_fallbacks_from_settings(prev_settings)
    if not extracted:
        return
    FALLBACKS_PATH.parent.mkdir(parents=True, exist_ok=True)
    FALLBACKS_PATH.write_text(json.dumps(extracted, indent=2) + "\n")
    print(f"  fallbacks: seeded {FALLBACKS_PATH} from prior hooks")


def backup_settings() -> Path:
    ts = time.strftime("%Y%m%d-%H%M%S")
    bak = SETTINGS.with_name(f"settings.json.bak.{ts}")
    shutil.copy2(SETTINGS, bak)
    print(f"  backup: {bak}")
    return bak


def latest_backup() -> Path | None:
    parent = SETTINGS.parent
    backups = sorted(parent.glob("settings.json.bak.*"))
    return backups[-1] if backups else None


def replace_event_hooks(settings: dict, event: str, command: str) -> None:
    """Replace any existing hooks for `event` with a single command hook."""
    settings.setdefault("hooks", {})
    settings["hooks"][event] = [
        {
            "hooks": [
                {"type": "command", "command": command}
            ]
        }
    ]


def add_session_start(settings: dict, command: str) -> None:
    """Add SessionStart hook without clobbering any existing matchers."""
    hooks = settings.setdefault("hooks", {})
    arr = hooks.setdefault("SessionStart", [])
    # If we already added ours, leave it alone.
    for entry in arr:
        for h in entry.get("hooks", []):
            if h.get("type") == "command" and "register_session.py" in h.get("command", ""):
                return
    arr.append({"hooks": [{"type": "command", "command": command}]})


def install() -> int:
    if not SETTINGS.exists():
        print(f"ERROR: {SETTINGS} does not exist", file=sys.stderr)
        return 1
    print("Installing claude-chords...")
    install_skills()
    install_shell_block()
    backup_settings()
    prev_settings = json.loads(SETTINGS.read_text())
    maybe_seed_fallbacks(prev_settings)
    settings = json.loads(json.dumps(prev_settings))  # deep copy
    replace_event_hooks(settings, "UserPromptSubmit", hook_cmd("UserPromptSubmit"))
    replace_event_hooks(settings, "Stop", hook_cmd("Stop"))
    replace_event_hooks(settings, "Notification", hook_cmd("Notification"))
    add_session_start(settings, session_start_cmd())
    SETTINGS.write_text(json.dumps(settings, indent=2) + "\n")
    print(f"  settings: updated {SETTINGS}")
    print()
    print("Done. Restart any running Claude Code sessions for the SessionStart")
    print("hook to register them. Then run /tone to assign a chord.")
    return 0


def uninstall() -> int:
    bak = latest_backup()
    if not bak:
        print("ERROR: no backup found to restore from", file=sys.stderr)
        return 1
    shutil.copy2(bak, SETTINGS)
    print(f"Restored settings from {bak}")
    for _, subdir in SKILLS:
        dst = Path.home() / ".claude" / "skills" / subdir / "SKILL.md"
        if dst.exists() or dst.is_symlink():
            dst.unlink()
            print(f"Removed skill {dst}")
    remove_shell_block()
    print("Done.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--uninstall":
        sys.exit(uninstall())
    sys.exit(install())
