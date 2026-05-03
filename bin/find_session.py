"""Resolve the current Claude Code session_id by finding the Claude main
process in our ancestor chain.

A SessionStart hook stores session_id keyed by the Claude main process PID
(the ancestor whose process name is `claude`). Any subprocess in the same
session — bash tool, skill invocation — finds that PID by walking its own
ancestors and matching on `comm`.
"""
from __future__ import annotations

import os
import subprocess
import sys

from registry import SESSIONS_DIR


def parent_of(pid: int) -> int | None:
    try:
        out = subprocess.check_output(
            ["ps", "-o", "ppid=", "-p", str(pid)],
            stderr=subprocess.DEVNULL,
        ).strip()
        return int(out) if out else None
    except (subprocess.CalledProcessError, ValueError):
        return None


def comm_of(pid: int) -> str:
    try:
        out = subprocess.check_output(
            ["ps", "-o", "comm=", "-p", str(pid)],
            stderr=subprocess.DEVNULL,
        ).decode(errors="replace").strip()
        # `comm` may be a path on macOS; we want the basename.
        return os.path.basename(out)
    except (subprocess.CalledProcessError, ValueError):
        return ""


def find_claude_pid(start: int | None = None) -> int | None:
    """Walk ancestors and return the first PID whose comm is 'claude'."""
    pid = start if start is not None else os.getpid()
    for _ in range(40):
        if pid <= 1:
            return None
        if comm_of(pid) == "claude":
            return pid
        ppid = parent_of(pid)
        if ppid is None or ppid == pid:
            return None
        pid = ppid
    return None


def find_session_id() -> str | None:
    cpid = find_claude_pid()
    if cpid is None:
        return None
    marker = SESSIONS_DIR / str(cpid)
    if marker.exists():
        sid = marker.read_text().strip()
        if sid:
            return sid
    return None


if __name__ == "__main__":
    sid = find_session_id()
    if sid:
        print(sid)
    else:
        sys.exit(1)
