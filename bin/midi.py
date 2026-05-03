"""Standard MIDI File (SMF) writer for the same event format used by the
sequencer: list of (start_beat, midi_note, dur_beats, gain) tuples.

No external deps — emits raw SMF Type 0 bytes via stdlib only.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

# Acoustic Grand Piano (General MIDI program 0).
DEFAULT_PROGRAM = 0


def _vlq(n: int) -> bytes:
    """Variable-length quantity encoding for delta times."""
    if n < 0:
        raise ValueError("VLQ can't encode negative")
    out = [n & 0x7F]
    n >>= 7
    while n:
        out.append((n & 0x7F) | 0x80)
        n >>= 7
    return bytes(reversed(out))


def _gain_to_velocity(gain: float) -> int:
    """Map our event gain (~0.05–0.55 typical range) to MIDI velocity 1–127.
    Uses a slight curve so soft notes stay distinguishable.
    """
    v = int(round(gain * 220))
    return max(1, min(127, v))


def events_to_midi(
    events: Iterable[tuple[float, int, float, float]],
    path: Path | str,
    bpm: float,
    time_sig: tuple[int, int] = (3, 4),
    ppqn: int = 480,
    program: int = DEFAULT_PROGRAM,
) -> None:
    """Write `events` to a Standard MIDI File at `path`.

    events:    iterable of (start_beat, midi_note, dur_beats, gain)
    bpm:       quarter-note tempo
    time_sig:  (numerator, denominator); denominator must be a power of 2
    ppqn:      pulses per quarter note (timing resolution; 480 is common)
    program:   General MIDI program number (0 = acoustic grand)
    """
    # Convert events to absolute-tick note-on / note-off pairs.
    on_off: list[tuple[int, int, int, int]] = []  # (tick, kind, note, velocity)
    for start_beat, midi_note, dur_beats, gain in events:
        if gain <= 0 or dur_beats <= 0:
            continue
        vel = _gain_to_velocity(gain)
        start_tick = int(round(start_beat * ppqn))
        end_tick = int(round((start_beat + dur_beats) * ppqn))
        if end_tick <= start_tick:
            end_tick = start_tick + 1
        on_off.append((start_tick, 1, midi_note, vel))   # 1 = note-on
        on_off.append((end_tick,   0, midi_note, vel))   # 0 = note-off

    # Sort: by tick, with note-offs (kind=0) before note-ons (kind=1) at the
    # same tick — keeps repeated same-pitch notes from being silently merged.
    on_off.sort(key=lambda x: (x[0], x[1]))

    track = bytearray()

    # Tempo meta (microseconds per quarter).
    us_per_q = int(round(60_000_000 / bpm))
    track += _vlq(0)
    track += bytes([0xFF, 0x51, 0x03])
    track += us_per_q.to_bytes(3, "big")

    # Time-signature meta.  denominator stored as power of 2 (2 = quarter).
    num, den = time_sig
    den_pow = den.bit_length() - 1
    if 1 << den_pow != den:
        raise ValueError(f"time_sig denominator must be a power of 2, got {den}")
    track += _vlq(0)
    track += bytes([0xFF, 0x58, 0x04, num & 0xFF, den_pow & 0xFF, 24, 8])

    # Program change to piano (channel 0).
    track += _vlq(0)
    track += bytes([0xC0, program & 0x7F])

    # Note on/off events.
    last_tick = 0
    for tick, kind, note, vel in on_off:
        delta = tick - last_tick
        track += _vlq(delta)
        status = 0x90 if kind == 1 else 0x80
        track += bytes([status, note & 0x7F, vel & 0x7F])
        last_tick = tick

    # End-of-track meta.
    track += _vlq(0)
    track += bytes([0xFF, 0x2F, 0x00])

    header = (
        b"MThd"
        + (6).to_bytes(4, "big")          # header chunk length
        + (0).to_bytes(2, "big")          # format 0 (single track)
        + (1).to_bytes(2, "big")          # one track
        + ppqn.to_bytes(2, "big")         # division
    )
    track_chunk = (
        b"MTrk" + len(track).to_bytes(4, "big") + bytes(track)
    )

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(header + track_chunk)
