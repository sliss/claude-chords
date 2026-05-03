"""Tiny rendering helper for compositions.

Each composition file builds an `events` list of (start_beat, midi_note,
dur_beats, gain) tuples and calls `render(events, name, bpm, ...)`. We write
both:
  - <name>.mid  — the canonical "score", editable in any DAW
  - <name>.wav  — preview rendered with our piano synth
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

from midi import events_to_midi
from synth import SR, piano_note, write_wav

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "compositions" / "output"

# Per-event tail beyond nominal note end so notes ring naturally.
RING_S = 0.6


def render_wav(
    events: list[tuple[float, int, float, float]],
    bpm: float,
    total_beats: float,
    tail_s: float = 2.5,
    target_peak: float = 0.93,
) -> np.ndarray:
    """Mix events into a mono float buffer at SR. Each event is rendered with
    `piano_note` at its midi note for `dur_beats * Q + RING_S` seconds, scaled
    by its gain, and summed into the master at its start beat. Final buffer
    is normalized to `target_peak`.
    """
    Q = 60.0 / bpm
    total_samples = int(total_beats * Q * SR) + int(tail_s * SR)
    master = np.zeros(total_samples, dtype=np.float64)

    for start_beat, midi, dur_beats, gain in events:
        if gain <= 0 or dur_beats <= 0:
            continue
        note_dur_s = max(0.06, dur_beats * Q + RING_S)
        sig = piano_note(midi, duration=note_dur_s) * gain
        start = int(start_beat * Q * SR)
        end = start + len(sig)
        if end > len(master):
            sig = sig[: len(master) - start]
            end = start + len(sig)
        master[start:end] += sig

    peak = float(np.max(np.abs(master)))
    if peak > 0:
        master = master * (target_peak / peak)
    return master


def render(
    events: list[tuple[float, int, float, float]],
    name: str,
    bpm: float,
    total_beats: float,
    time_sig: tuple[int, int] = (3, 4),
    play: bool = False,
) -> tuple[Path, Path]:
    """Render `events` to both <name>.wav and <name>.mid under
    compositions/output/. Returns the two paths.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    wav_path = OUTPUT_DIR / f"{name}.wav"
    mid_path = OUTPUT_DIR / f"{name}.mid"

    audio = render_wav(events, bpm=bpm, total_beats=total_beats)
    write_wav(wav_path, audio)
    events_to_midi(events, mid_path, bpm=bpm, time_sig=time_sig)

    n_events = sum(1 for *_, g in events if g > 0)
    print(f"{name}: {n_events} events -> {wav_path.name} ({len(audio)/SR:.1f}s) "
          f"and {mid_path.name} ({mid_path.stat().st_size} bytes)")

    if play:
        import subprocess
        subprocess.run(["afplay", str(wav_path)], check=False)

    return wav_path, mid_path
