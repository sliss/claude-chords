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
SKILL_TMPL = ROOT / "skill" / "SKILL.md.tmpl"
SKILL_DST_DIR = Path.home() / ".claude" / "skills" / "tone"
SKILL_DST = SKILL_DST_DIR / "SKILL.md"
SETTINGS = Path.home() / ".claude" / "settings.json"
FALLBACKS_PATH = ROOT / "state" / "fallbacks.json"

# Each hook command is wrapped to background and silence output.
def hook_cmd(event: str) -> str:
    # No shell backgrounding here: `( cmd ) &` breaks stdin propagation, so
    # the python script never sees the session_id JSON. The script itself
    # detaches afplay via Popen(start_new_session=True), which keeps the
    # audio non-blocking. The python process exits in well under a second.
    return f"python3 {BIN / 'play_event.py'} {event}"

def session_start_cmd() -> str:
    return f"python3 {BIN / 'register_session.py'}"


def install_skill() -> None:
    SKILL_DST_DIR.mkdir(parents=True, exist_ok=True)
    rendered = SKILL_TMPL.read_text().replace("{{PROJECT_ROOT}}", str(ROOT))
    if SKILL_DST.is_symlink() or SKILL_DST.exists():
        SKILL_DST.unlink()
    SKILL_DST.write_text(rendered)
    print(f"  skill: rendered {SKILL_TMPL.name} -> {SKILL_DST}")


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
    install_skill()
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
    if SKILL_DST.exists() or SKILL_DST.is_symlink():
        SKILL_DST.unlink()
        print(f"Removed skill symlink {SKILL_DST}")
    print("Done.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--uninstall":
        sys.exit(uninstall())
    sys.exit(install())
