"""Hook playback dispatcher.

Called by UserPromptSubmit / Stop / Notification hooks. Reads the hook JSON
from stdin to get session_id, looks up the assigned chord in the registry,
and plays the appropriate variant via afplay. Falls back to a default sound
when no chord is assigned for this session.

Event -> variant mapping:
  UserPromptSubmit -> arpeggio up
  Stop             -> block chord
  Notification     -> arpeggio down
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from registry import (
    SYSTEM_FALLBACK,
    cache_path,
    load_fallbacks,
    load_registry,
)

EVENT_VARIANT = {
    "UserPromptSubmit": "arp_up",
    "Stop": "block",
    "Notification": "arp_down",
}


def play_async(path: str) -> None:
    """Spawn afplay and detach. Hooks shouldn't block on audio."""
    try:
        subprocess.Popen(
            ["afplay", path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )
    except (FileNotFoundError, OSError):
        pass


def play_fallback(event: str) -> None:
    fallbacks = load_fallbacks()
    candidate = fallbacks.get(event)
    if candidate and Path(candidate).exists():
        play_async(candidate)
        return
    sysf = SYSTEM_FALLBACK.get(event)
    if sysf and Path(sysf).exists():
        play_async(sysf)


def main() -> int:
    # Event name comes from argv[1] (set in the hook command).
    if len(sys.argv) < 2:
        return 0
    event = sys.argv[1]
    variant = EVENT_VARIANT.get(event)
    if variant is None:
        return 0

    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        payload = {}
    sid = payload.get("session_id")

    if sid:
        reg = load_registry()
        entry = reg.get(sid)
        if entry:
            notes = entry.get("notes")
            instrument = entry.get("instrument", "piano")
            if notes:
                wav = cache_path(notes, variant, instrument)
                if wav.exists():
                    play_async(str(wav))
                    return 0

    play_fallback(event)
    return 0


if __name__ == "__main__":
    sys.exit(main())
