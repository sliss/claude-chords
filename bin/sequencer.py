"""Tiny rendering helper for compositions.

Each composition file builds an `events` list of (start_beat, midi_note,
dur_beats, gain) tuples and calls `render(events, name, bpm, ...)`. We write
both:
  - <name>[_<instrument>].mid  — Standard MIDI File, editable in any DAW
  - <name>[_<instrument>].wav  — preview rendered with the chosen synth voice

The instrument suffix is omitted for piano (the default) so existing piano
renderings keep their original filenames.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from midi import events_to_midi
from synth import DEFAULT_GAIN, GM_PROGRAM, INSTRUMENTS, SR, voice, write_wav

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "compositions" / "output"

# Per-event tail beyond nominal note end so notes ring naturally.
RING_S = 0.6


def render_wav(
    events: list[tuple[float, int, float, float]],
    bpm: float,
    total_beats: float,
    instrument: str = "piano",
    tail_s: float = 2.5,
    target_peak: float = 0.93,
) -> np.ndarray:
    """Mix events into a mono float buffer at SR. Each event's gain is
    multiplied by the instrument's default loudness so balance is preserved
    across instruments."""
    Q = 60.0 / bpm
    base_gain = DEFAULT_GAIN.get(instrument, 0.35)
    total_samples = int(total_beats * Q * SR) + int(tail_s * SR)
    master = np.zeros(total_samples, dtype=np.float64)

    for start_beat, midi, dur_beats, gain in events:
        if gain <= 0 or dur_beats <= 0:
            continue
        note_dur_s = max(0.06, dur_beats * Q + RING_S)
        sig = voice(midi, duration=note_dur_s, instrument=instrument,
                    gain=base_gain * gain)
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
    instrument: str = "piano",
    play: bool = False,
) -> tuple[Path, Path]:
    if instrument not in INSTRUMENTS:
        raise ValueError(
            f"Unknown instrument {instrument!r}. Choose one of: "
            f"{', '.join(INSTRUMENTS.keys())}"
        )
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    suffix = "" if instrument == "piano" else f"_{instrument}"
    wav_path = OUTPUT_DIR / f"{name}{suffix}.wav"
    mid_path = OUTPUT_DIR / f"{name}{suffix}.mid"

    audio = render_wav(events, bpm=bpm, total_beats=total_beats, instrument=instrument)
    write_wav(wav_path, audio)
    events_to_midi(events, mid_path, bpm=bpm, time_sig=time_sig,
                   program=GM_PROGRAM.get(instrument, 0))

    n_events = sum(1 for *_, g in events if g > 0)
    print(f"{name}{suffix}: {n_events} events, {instrument} -> "
          f"{wav_path.name} ({len(audio)/SR:.1f}s) and {mid_path.name} "
          f"({mid_path.stat().st_size} bytes)")

    if play:
        import subprocess
        subprocess.run(["afplay", str(wav_path)], check=False)

    return wav_path, mid_path


def cli_instrument() -> str:
    """Helper for composition main blocks: parse `--instrument <name>` from
    sys.argv. Returns 'piano' if not given."""
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--instrument", "-i", default="piano",
                        choices=list(INSTRUMENTS.keys()))
    parser.add_argument("--play", action="store_true",
                        help="Play the rendered WAV after writing")
    args, _ = parser.parse_known_args()
    return args
