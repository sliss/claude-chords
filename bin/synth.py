"""Multi-instrument synthesis. Each `<name>_note(midi, duration, gain)`
returns a mono float64 numpy array sampled at SR. Use `voice(midi, duration,
instrument)` to dispatch by name.

Approaches per instrument:
  piano    — additive synthesis with mildly inharmonic partials, percussive attack
  pizz     — Karplus-Strong via scipy.signal.lfilter, with outer envelope
  marimba  — wood-bar partials at 1:4:10 ratios, very fast decay
  organ    — harmonic stack, instant attack, sustained, no decay
  bell     — inharmonic bell partials, long decay, attack click
  strings  — detuned sawtooth × 2, lowpass, vibrato, slow attack/release

All deps are stdlib + numpy + scipy (no soundfont, no fluidsynth).
"""
from __future__ import annotations

import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, lfilter, sosfilt

SR = 44100


def midi_to_freq(midi: int) -> float:
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)


def _normalize(sig: np.ndarray) -> np.ndarray:
    peak = float(np.max(np.abs(sig)))
    return sig / peak if peak > 0 else sig


# ─── Piano ──────────────────────────────────────────────────────────
def piano_note(midi: int, duration: float = 2.5, gain: float = 0.35) -> np.ndarray:
    freq = midi_to_freq(midi)
    n = int(SR * duration)
    t = np.arange(n) / SR
    harm_amps = [1.00, 0.55, 0.32, 0.20, 0.14, 0.10, 0.07, 0.05, 0.04, 0.03]
    sig = np.zeros(n, dtype=np.float64)
    for h, amp in enumerate(harm_amps, start=1):
        f = freq * h * np.sqrt(1.0 + 0.0007 * h * h)  # mild inharmonicity
        if f >= SR / 2.0:
            break
        decay = 1.4 + 0.65 * h
        env = np.exp(-decay * t)
        sig += amp * env * np.sin(2.0 * np.pi * f * t)
    # Hammer click
    click_len = int(0.006 * SR)
    click = np.random.uniform(-1.0, 1.0, click_len) * np.linspace(1.0, 0.0, click_len)
    sig[:click_len] += 0.18 * click
    # Attack ramp
    attack = int(0.0025 * SR)
    sig[:attack] *= np.linspace(0.0, 1.0, attack)
    return (gain * _normalize(sig)).astype(np.float64)


# ─── Pizzicato strings ─────────────────────────────────────────────
def pizz_note(midi: int, duration: float = 1.6, gain: float = 0.55) -> np.ndarray:
    """Plucked-string via Karplus-Strong (delay line + averaging lowpass).
    Implemented via `scipy.signal.lfilter` for speed.
    """
    freq = midi_to_freq(midi)
    N = max(2, int(round(SR / freq)))   # delay-line length ≈ one period
    n = int(SR * duration)
    # Excitation: short noise burst (one period).
    x = np.zeros(n, dtype=np.float64)
    x[:N] = np.random.uniform(-1.0, 1.0, N)
    # Karplus-Strong recurrence: y[i] = x[i] + half*(y[i-N] + y[i-N+1])
    half = 0.498
    a = np.zeros(N + 1)
    a[0] = 1.0
    a[N - 1] = -half
    a[N] = -half
    out = lfilter([1.0], a, x)
    # Outer envelope so it dies quickly (pizzicato character).
    env = np.exp(-2.5 * np.linspace(0.0, 1.0, n))
    out *= env
    return (gain * _normalize(out)).astype(np.float64)


# ─── Marimba / xylophone ───────────────────────────────────────────
def marimba_note(midi: int, duration: float = 1.0, gain: float = 0.50) -> np.ndarray:
    """Wood-bar mallet sound. Real marimba bars vibrate at ~1:4:10 frequency
    ratios (stiffness modes), and the upper partials decay much faster than
    the fundamental.
    """
    freq = midi_to_freq(midi)
    n = int(SR * duration)
    t = np.arange(n) / SR
    sig = np.zeros(n, dtype=np.float64)
    # (frequency_ratio, amplitude, decay_rate)
    partials = [(1.0, 1.0, 6.5), (4.0, 0.35, 13.0), (10.0, 0.10, 18.0)]
    for ratio, amp, decay in partials:
        f = freq * ratio
        if f >= SR / 2.0:
            continue
        sig += amp * np.exp(-decay * t) * np.sin(2.0 * np.pi * f * t)
    # Ultra-short attack — mallet impact.
    attack = max(2, int(0.0008 * SR))
    sig[:attack] *= np.linspace(0.0, 1.0, attack)
    return (gain * _normalize(sig)).astype(np.float64)


# ─── Organ ─────────────────────────────────────────────────────────
def organ_note(midi: int, duration: float = 2.0, gain: float = 0.30) -> np.ndarray:
    """Sustained organ tone: harmonic stack, fast attack, fast release, no decay."""
    freq = midi_to_freq(midi)
    n = int(SR * duration)
    t = np.arange(n) / SR
    sig = np.zeros(n, dtype=np.float64)
    # Drawbar-ish harmonic mix.
    partials = [(1, 1.00), (2, 0.55), (3, 0.35), (4, 0.30),
                (5, 0.20), (6, 0.15), (8, 0.12)]
    for h, amp in partials:
        f = freq * h
        if f >= SR / 2.0:
            break
        sig += amp * np.sin(2.0 * np.pi * f * t)
    # Quick attack, sustain, gentle release (ASR).
    attack = int(0.008 * SR)
    release = int(0.10 * SR)
    env = np.ones(n)
    env[:attack] = np.linspace(0.0, 1.0, attack)
    if release < n:
        env[-release:] = np.linspace(1.0, 0.0, release)
    sig *= env
    return (gain * _normalize(sig)).astype(np.float64)


# ─── Bell / glockenspiel ───────────────────────────────────────────
def bell_note(midi: int, duration: float = 3.8, gain: float = 0.35) -> np.ndarray:
    """Bell tone with characteristic inharmonic partials (hum, prime, tierce,
    quint, nominal, etc.) and long decay. The minor third above the strike
    tone (ratio ~1.18) gives the classic bell colour.
    """
    freq = midi_to_freq(midi)
    n = int(SR * duration)
    t = np.arange(n) / SR
    # (ratio, amp, decay)
    partials = [
        (0.50, 0.30, 0.6),   # hum
        (1.00, 0.70, 1.1),   # strike
        (1.18, 0.50, 1.4),   # tierce (minor 3rd above)
        (1.50, 0.40, 1.5),   # quint
        (2.00, 0.55, 1.7),   # nominal (octave)
        (2.50, 0.30, 2.2),
        (2.66, 0.25, 2.4),
        (3.00, 0.20, 2.6),
        (4.00, 0.15, 3.0),
        (5.43, 0.10, 3.6),
    ]
    sig = np.zeros(n, dtype=np.float64)
    for ratio, amp, decay in partials:
        f = freq * ratio
        if f >= SR / 2.0:
            continue
        sig += amp * np.exp(-decay * t) * np.sin(2.0 * np.pi * f * t)
    # Sharp attack click.
    click = max(2, int(0.0025 * SR))
    sig[:click] += 0.4 * np.random.uniform(-1.0, 1.0, click) * np.linspace(1.0, 0.0, click)
    return (gain * _normalize(sig)).astype(np.float64)


# ─── Strings (sustained, arco) ─────────────────────────────────────
def strings_note(midi: int, duration: float = 2.2, gain: float = 0.32) -> np.ndarray:
    """Sustained strings: two slightly-detuned sawtooth oscillators, lowpass-filtered,
    with vibrato and a slow attack."""
    freq = midi_to_freq(midi)
    n = int(SR * duration)
    t = np.arange(n) / SR
    # Vibrato: ~5.5 Hz, ±0.3% pitch deviation
    vib = 0.003 * np.sin(2.0 * np.pi * 5.5 * t)

    def saw(f0: float, vib_depth: float = 1.0) -> np.ndarray:
        phase = 2.0 * np.pi * f0 * (1.0 + vib * vib_depth) * t
        s = np.zeros(n, dtype=np.float64)
        for h in range(1, 17):
            if f0 * h >= SR / 2.0:
                break
            s += (1.0 / h) * np.sin(h * phase)
        return s

    sig = 0.6 * saw(freq) + 0.4 * saw(freq * 0.997, vib_depth=0.7)
    # Lowpass to take the edge off.
    sos = butter(4, 4500.0 / (SR / 2.0), output="sos")
    sig = sosfilt(sos, sig)
    # Slow attack, gentle release.
    attack = int(0.07 * SR)
    release = int(0.18 * SR)
    env = np.ones(n)
    env[:attack] = np.linspace(0.0, 1.0, attack) ** 2
    if release < n:
        env[-release:] = np.linspace(1.0, 0.0, release) ** 2
    sig *= env
    return (gain * _normalize(sig)).astype(np.float64)


# ─── Dispatcher ────────────────────────────────────────────────────
INSTRUMENTS: dict[str, callable] = {
    "piano":   piano_note,
    "pizz":    pizz_note,
    "marimba": marimba_note,
    "organ":   organ_note,
    "bell":    bell_note,
    "strings": strings_note,
}

# Per-instrument default gain — chosen so chords sit at similar perceived
# loudness across instruments. Sustained voices get less gain (avoid build-up
# in chord summing); short percussive voices get more.
DEFAULT_GAIN: dict[str, float] = {
    "piano":   0.35,
    "pizz":    0.55,
    "marimba": 0.50,
    "organ":   0.30,
    "bell":    0.35,
    "strings": 0.32,
}

# Block-chord duration per instrument (seconds). Sustained instruments hold
# longer; percussive ones get a shorter window since they decay faster.
BLOCK_DUR: dict[str, float] = {
    "piano":   2.5,
    "pizz":    1.8,
    "marimba": 1.2,
    "organ":   2.4,
    "bell":    4.0,
    "strings": 2.5,
}

# General MIDI program numbers for the "real" version of each timbre.
# Used when emitting MIDI files so a DAW or external player picks a sensible
# patch automatically.
GM_PROGRAM: dict[str, int] = {
    "piano":   0,    # Acoustic Grand Piano
    "pizz":    45,   # Pizzicato Strings
    "marimba": 12,   # Marimba
    "organ":   19,   # Church Organ
    "bell":    9,    # Glockenspiel
    "strings": 48,   # String Ensemble 1
}


def voice(midi: int, duration: float, instrument: str = "piano",
          gain: float | None = None) -> np.ndarray:
    fn = INSTRUMENTS.get(instrument, piano_note)
    g = gain if gain is not None else DEFAULT_GAIN.get(instrument, 0.35)
    return fn(midi, duration=duration, gain=g)


# ─── Chord/arpeggio rendering ──────────────────────────────────────
def render_block_chord(notes: list[int], duration: float | None = None,
                       instrument: str = "piano") -> np.ndarray:
    """All notes struck simultaneously."""
    if not notes:
        return np.zeros(int(SR * 1.0), dtype=np.float64)
    dur = duration if duration is not None else BLOCK_DUR.get(instrument, 2.5)
    layers = [voice(m, duration=dur, instrument=instrument) for m in notes]
    n = max(len(x) for x in layers)
    mix = np.zeros(n, dtype=np.float64)
    for x in layers:
        mix[: len(x)] += x
    # Headroom: scale by 1/sqrt(N) so 3-note chord and 2-note dyad sit at similar loudness.
    mix /= max(np.sqrt(len(notes)), 1.0)
    return _safe_normalize(mix, target=0.85)


def render_arpeggio(notes: list[int], stagger: float = 0.11, tail: float | None = None,
                    direction: str = "up", instrument: str = "piano") -> np.ndarray:
    """Notes struck in sequence with `stagger` seconds between onsets."""
    if not notes:
        return np.zeros(int(SR * 1.0), dtype=np.float64)
    if tail is None:
        tail = max(0.6, BLOCK_DUR.get(instrument, 2.5) - 0.4)
    seq = sorted(notes) if direction == "up" else sorted(notes, reverse=True)
    note_dur = stagger * len(seq) + tail
    layers = []
    for i, m in enumerate(seq):
        delay_samples = int(i * stagger * SR)
        body = voice(m, duration=note_dur - i * stagger, instrument=instrument)
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
