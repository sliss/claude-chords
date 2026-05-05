"""/push-fanfare backend: toggle the post-push victory fanfare.

State is a marker file at state/push_fanfare.enabled. The shell function
in ~/.bash_profile (installed by install.py) checks for this file
synchronously after every successful `git push`; presence = play, absence
= silent. No JSON parsing in the hot path so push completion is fast.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKER = ROOT / "state" / "push_fanfare.enabled"

USAGE = (
    "Usage: push_fanfare.py [on|off|toggle|status]\n"
    "  on / enable     — fanfare plays after successful git push\n"
    "  off / disable   — pushes are silent\n"
    "  toggle (default)— flip the current state\n"
    "  status          — print current state without changing it"
)


def is_enabled() -> bool:
    return MARKER.exists()


def enable() -> None:
    MARKER.parent.mkdir(parents=True, exist_ok=True)
    MARKER.touch()


def disable() -> None:
    if MARKER.exists():
        MARKER.unlink()


def main() -> int:
    args = sys.argv[1:]
    cmd = (args[0] if args else "toggle").strip().lower()

    aliases = {
        "on": "on", "enable": "on", "yes": "on", "true": "on", "1": "on",
        "off": "off", "disable": "off", "no": "off", "false": "off", "0": "off",
        "quiet": "off", "mute": "off",
        "toggle": "toggle", "swap": "toggle", "flip": "toggle", "": "toggle",
        "status": "status", "state": "status",
    }
    action = aliases.get(cmd)
    if action is None:
        print(f"ERROR: unknown command {cmd!r}\n\n{USAGE}", file=sys.stderr)
        return 2

    if action == "on":
        enable()
    elif action == "off":
        disable()
    elif action == "toggle":
        (disable() if is_enabled() else enable())
    # status: no-op, just report below

    state = "ON" if is_enabled() else "OFF"
    print(f"Push fanfare: {state}")
    if action == "on" or (action == "toggle" and state == "ON"):
        print("  Plays after every successful `git push`. Open a new shell")
        print("  tab if the function isn't active yet (it lives in ~/.bash_profile).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
