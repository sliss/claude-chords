"""SessionStart hook: write session_id to a file keyed by the Claude main
process PID (the ancestor whose process name is `claude`).

The hook command is invoked via `sh -c`, so this script's direct parent is
the wrapping shell — not Claude. We walk the ancestor chain to find the
real Claude PID, then key the marker file on that.

Also opportunistically cleans up stale marker files (PIDs that no longer
correspond to a live Claude process) and their registry entries.
"""
from __future__ import annotations

import json
import os
import sys

from find_session import find_claude_pid
from registry import SESSIONS_DIR, ensure_dirs, load_registry, save_registry


def alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def cleanup_stale() -> None:
    if not SESSIONS_DIR.exists():
        return
    for f in SESSIONS_DIR.iterdir():
        try:
            pid = int(f.name)
        except ValueError:
            continue
        if not alive(pid):
            try:
                sid = f.read_text().strip()
            except OSError:
                sid = None
            try:
                f.unlink()
            except OSError:
                pass
            if sid:
                reg = load_registry()
                if sid in reg:
                    reg.pop(sid, None)
                    save_registry(reg)


def main() -> int:
    ensure_dirs()
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    sid = payload.get("session_id")
    if not sid:
        return 0

    cpid = find_claude_pid()
    if cpid is None:
        # Last-resort fallback: use direct parent. /tone may still find it
        # if the wrapping shell hasn't exited yet, though normally it has.
        cpid = os.getppid()

    (SESSIONS_DIR / str(cpid)).write_text(sid)
    cleanup_stale()
    return 0


if __name__ == "__main__":
    sys.exit(main())
