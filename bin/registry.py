"""Shared filesystem layout + atomic registry I/O."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = ROOT / "state"
SESSIONS_DIR = STATE_DIR / "sessions"     # <claude_pid> -> session_id
CACHE_DIR = STATE_DIR / "cache"           # rendered .wav files
REGISTRY_PATH = STATE_DIR / "registry.json"
FALLBACKS_PATH = STATE_DIR / "fallbacks.json"

# System sounds used when no chord is assigned and no user fallback is set.
SYSTEM_FALLBACK = {
    "UserPromptSubmit": "/System/Library/Sounds/Pop.aiff",
    "Stop": "/System/Library/Sounds/Hero.aiff",
    "Notification": "/System/Library/Sounds/Glass.aiff",
}


def load_fallbacks() -> dict:
    """User-configured fallback sounds. Set by install.py from the user's
    pre-existing hook commands, or hand-edited later. Falls back to system
    sounds when the file is missing or doesn't cover an event.
    """
    if not FALLBACKS_PATH.exists():
        return dict(SYSTEM_FALLBACK)
    try:
        data = json.loads(FALLBACKS_PATH.read_text())
    except (json.JSONDecodeError, OSError):
        return dict(SYSTEM_FALLBACK)
    merged = dict(SYSTEM_FALLBACK)
    merged.update({k: v for k, v in data.items() if isinstance(v, str)})
    return merged


# Backwards-compat name; consumers call load_fallbacks() now for a fresh read.
FALLBACK_SOUNDS = load_fallbacks()


def ensure_dirs() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def load_registry() -> dict:
    if not REGISTRY_PATH.exists():
        return {}
    try:
        return json.loads(REGISTRY_PATH.read_text())
    except json.JSONDecodeError:
        return {}


def save_registry(reg: dict) -> None:
    ensure_dirs()
    # Atomic write via tempfile + rename.
    fd, tmp = tempfile.mkstemp(prefix=".registry-", dir=str(STATE_DIR))
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(reg, f, indent=2)
        os.replace(tmp, REGISTRY_PATH)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def chord_cache_key(notes: list[int], variant: str) -> str:
    """Stable hash for caching rendered audio."""
    s = ",".join(str(n) for n in notes) + "|" + variant
    return hashlib.sha1(s.encode()).hexdigest()[:16]


def cache_path(notes: list[int], variant: str) -> Path:
    return CACHE_DIR / f"{chord_cache_key(notes, variant)}_{variant}.wav"
