"""/leitmotif skill backend.

Reads a JSON payload from stdin describing a short motif composed by the
LLM, renders it via the sequencer, caches the WAV, and stores a pointer
in the per-session registry so the Stop hook plays it.

Stdin schema:
    {
      "events":     [[start_beat, midi, dur_beats, gain], ...],   # required
      "bpm":        100,                                          # optional, default 100
      "instrument": "piano",                                      # optional, default piano
      "label":      "Cathedral Bells",                            # optional, short title
      "description": "celebrating shipped feature"                # optional, free text
    }

Co-exists with /tone: the registry entry for a session can hold BOTH a
chord assignment (used by UserPromptSubmit/Notification arpeggios) AND a
leitmotif (used by Stop). The dispatcher checks leitmotif first on Stop.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from find_session import find_session_id
from registry import (
    CACHE_DIR,
    ensure_dirs,
    load_registry,
    save_registry,
)
from sequencer import render_wav
from synth import INSTRUMENTS, write_wav

MAX_DURATION_S = 5.0   # safety cap; the skill says <= 3.5s but allow some slack
MAX_NOTE_COUNT = 64
MIN_MIDI = 21          # A0
MAX_MIDI = 108         # C8


def leitmotif_hash(events: list, instrument: str, bpm: float) -> str:
    payload = {"events": events, "instrument": instrument, "bpm": bpm}
    s = json.dumps(payload, sort_keys=True)
    return hashlib.sha1(s.encode()).hexdigest()[:16]


def leitmotif_path(h: str) -> Path:
    return CACHE_DIR / f"leitmotif_{h}.wav"


def validate_events(events) -> list[tuple[float, int, float, float]]:
    if not isinstance(events, list) or not events:
        raise ValueError("`events` must be a non-empty list")
    if len(events) > MAX_NOTE_COUNT:
        raise ValueError(f"too many events ({len(events)} > {MAX_NOTE_COUNT})")
    cleaned: list[tuple[float, int, float, float]] = []
    for i, e in enumerate(events):
        if not isinstance(e, (list, tuple)) or len(e) != 4:
            raise ValueError(f"event {i}: expected [start_beat, midi, dur, gain]")
        start, midi, dur, gain = e
        start = float(start)
        midi = int(midi)
        dur = float(dur)
        gain = float(gain)
        if start < 0:
            raise ValueError(f"event {i}: start_beat < 0")
        if not (MIN_MIDI <= midi <= MAX_MIDI):
            raise ValueError(f"event {i}: midi {midi} out of range "
                             f"[{MIN_MIDI},{MAX_MIDI}]")
        if dur <= 0:
            raise ValueError(f"event {i}: dur must be > 0")
        if not (0 < gain <= 1):
            raise ValueError(f"event {i}: gain must be in (0, 1]")
        cleaned.append((start, midi, dur, gain))
    return cleaned


def main() -> int:
    ensure_dirs()
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            print("ERROR: empty stdin. Pipe a JSON payload (see SKILL.md).",
                  file=sys.stderr)
            return 2
        payload = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: invalid JSON: {e}", file=sys.stderr)
        return 2

    try:
        events = validate_events(payload.get("events"))
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    bpm = float(payload.get("bpm", 100.0))
    if not (40.0 <= bpm <= 240.0):
        print(f"ERROR: bpm {bpm} out of sensible range [40, 240]", file=sys.stderr)
        return 2

    instrument = str(payload.get("instrument", "piano"))
    if instrument not in INSTRUMENTS:
        print(f"ERROR: unknown instrument {instrument!r}. "
              f"Known: {', '.join(INSTRUMENTS.keys())}", file=sys.stderr)
        return 2

    label = str(payload.get("label", "")).strip() or "Untitled"
    description = str(payload.get("description", "")).strip()

    # Total duration (in beats) for the renderer.
    total_beats = max(e[0] + e[2] for e in events)
    duration_s = total_beats * (60.0 / bpm)
    if duration_s > MAX_DURATION_S:
        print(f"ERROR: motif is {duration_s:.1f}s; max allowed is "
              f"{MAX_DURATION_S}s. Tighten the events.", file=sys.stderr)
        return 2

    sid = find_session_id()
    if not sid:
        print("ERROR: could not resolve current session_id (is the SessionStart "
              "hook installed? Try restarting the Claude session).", file=sys.stderr)
        return 2

    h = leitmotif_hash(events, instrument, bpm)
    wav = leitmotif_path(h)
    if not wav.exists():
        audio = render_wav(events, bpm=bpm, total_beats=total_beats,
                           instrument=instrument)
        write_wav(wav, audio)

    reg = load_registry()
    entry = reg.get(sid, {})
    entry["leitmotif"] = {
        "hash": h,
        "label": label,
        "description": description,
        "instrument": instrument,
        "bpm": bpm,
        "events": events,
        "duration_s": round(duration_s, 2),
    }
    reg[sid] = entry
    save_registry(reg)

    # Output: the path on its own line so the skill can afplay it for preview.
    print(f"Leitmotif assigned: {label!r}")
    if description:
        print(f"  {description}")
    print(f"  {len(events)} notes, {duration_s:.2f}s, {instrument}, {bpm:g} BPM")
    print(f"  cache: {wav}")
    print(f"  Stop hook will play this for session {sid[:8]}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
