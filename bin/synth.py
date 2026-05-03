"""Piano-ish synthesis. Renders WAV files for chords (block) and arpeggios.

Approach: additive synthesis with mildly inharmonic partials, fast attack,
exponentially decaying per-harmonic envelopes (higher harmonics decay faster).
Not Steinway-quality, but unambiguous pitch and a recognizable hammered-string
character.
"""
from __future__ import annotations

import wave
from pathlib import Path

import numpy as np

SR = 44100


def midi_to_freq(midi: int) -> float:
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)


def piano_note(midi: int, duration: float = 2.5, gain: float = 0.35) -> np.ndarray:
    freq = midi_to_freq(midi)
    n = int(SR * duration)
    t = np.arange(n) / SR

    # Per-harmonic amplitudes (rough piano-ish spectrum).
    harm_amps = [1.00, 0.55, 0.32, 0.20, 0.14, 0.10, 0.07, 0.05, 0.04, 0.03]

    sig = np.zeros(n, dtype=np.float64)
    for h, amp in enumerate(harm_amps, start=1):
        # Slight inharmonicity (real piano strings have stiffness).
        f = freq * h * np.sqrt(1.0 + 0.0007 * h * h)
        if f >= SR / 2.0:
            break
        # Higher harmonics decay faster.
        decay = 1.4 + 0.65 * h
        env = np.exp(-decay * t)
        sig += amp * env * np.sin(2.0 * np.pi * f * t)

    # Brief "hammer" click: short bandlimited noise burst at attack.
    click_len = int(0.006 * SR)
    click = np.random.uniform(-1.0, 1.0, click_len) * np.linspace(1.0, 0.0, click_len)
    sig[:click_len] += 0.18 * click

    # Quick attack ramp to avoid pop.
    attack = int(0.0025 * SR)
    sig[:attack] *= np.linspace(0.0, 1.0, attack)

    # Normalize per-note then apply gain. We normalize so chords sum cleanly.
    peak = float(np.max(np.abs(sig)))
    if peak > 0:
        sig = sig / peak
    return (gain * sig).astype(np.float64)


def render_block_chord(notes: list[int], duration: float = 2.5) -> np.ndarray:
    """All notes struck simultaneously."""
    if not notes:
        return np.zeros(int(SR * duration), dtype=np.float64)
    layers = [piano_note(m, duration=duration) for m in notes]
    n = max(len(x) for x in layers)
    mix = np.zeros(n, dtype=np.float64)
    for x in layers:
        mix[: len(x)] += x
    # Headroom: scale by 1/sqrt(N) so 3-note chord and 2-note dyad sit at similar loudness.
    mix /= max(np.sqrt(len(notes)), 1.0)
    return _safe_normalize(mix, target=0.85)


def render_arpeggio(notes: list[int], stagger: float = 0.11, tail: float = 1.6,
                    direction: str = "up") -> np.ndarray:
    """Notes struck in sequence with `stagger` seconds between onsets.

    direction: "up" (low->high) or "down" (high->low).
    """
    if not notes:
        return np.zeros(int(SR * tail), dtype=np.float64)
    seq = sorted(notes) if direction == "up" else sorted(notes, reverse=True)
    note_dur = stagger * len(seq) + tail
    layers = []
    for i, m in enumerate(seq):
        delay_samples = int(i * stagger * SR)
        body = piano_note(m, duration=note_dur - i * stagger)
        layers.append((delay_samples, body))
    total = max(off + len(b) for off, b in layers)
    mix = np.zeros(total, dtype=np.float64)
    for off, body in layers:
        mix[off : off + len(body)] += body
    return _safe_normalize(mix, target=0.85)


def _safe_normalize(sig: np.ndarray, target: float = 0.9) -> np.ndarray:
    peak = float(np.max(np.abs(sig)))
    if peak <= 0:
        return sig
    return sig * (target / peak)


def write_wav(path: Path, sig: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pcm = np.clip(sig, -1.0, 1.0)
    pcm16 = (pcm * 32767.0).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm16.tobytes())
