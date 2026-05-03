"""Romantic-era minuet/intermezzo in Eb major. 12 bars, 3/4, 80 BPM.

Harmonic plan:
  bar  1: Ebmaj7              (lush tonic)
  bar  2: Bb7/D               (V7 in first inversion — smooth bass)
  bar  3: Cm7                 (vi7)
  bar  4: Abmaj7              (IVmaj7)
  bar  5: Fm9                 (ii9)
  bar  6: Bb7sus4 → Bb7       (V with 4-3 suspension in melody)
  bar  7: Gø7                 (G half-dim 7 = vii°7 of vi)
  bar  8: Cm7                 (vi7 — soft landing)
  bar  9: Fm7                 (ii7 again)
  bar 10: Cb–Eb–Gb–A          (German augmented 6th)
  bar 11: Bb7  (V7)           (Ger+6 resolves outward to V)
  bar 12: Ebmaj9              (final tonic with 9th)

Texture: bass-on-1, arpeggiated mid voicing on 2 and 3 (Chopin-ish), with a
sustained alto line. Almost no ornaments — the harmony does the work.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "bin"))

from sequencer import render

BPM = 80

events: list[tuple[float, int, float, float]] = []


def n(beat: float, midi: int, dur_beats: float, gain: float = 0.40) -> None:
    if dur_beats <= 0 or gain <= 0:
        return
    events.append((beat, midi, dur_beats, gain))


def melody(beat, midi, dur=1.0, gain=0.46):  n(beat, midi, dur, gain)
def alto(beat, midi, dur=1.0, gain=0.18):    n(beat, midi, dur, gain)


def lh_arpeg(start_beat: float, bass: int,
             mid_a: list[int], mid_b: list[int]) -> None:
    """Romantic LH: bass beat 1 (rings full bar), then 2-note voicings on
    beats 2 and 3, each ringing into the next bar's first beat."""
    n(start_beat,        bass, 3.4, 0.38)
    for m in mid_a:
        n(start_beat + 1, m, 2.4, 0.16)
    for m in mid_b:
        n(start_beat + 2, m, 1.7, 0.16)


# Bar 1 — Ebmaj7
melody(0, 79, 3.0, 0.44)
alto(0, 70, 3.2, 0.16)
lh_arpeg(0, 39, [55, 58], [62, 65])

# Bar 2 — Bb7/D
melody(3, 77, 1.0, 0.42)
melody(4, 75, 1.0, 0.40)
melody(5, 74, 1.0, 0.40)
alto(3, 70, 3.2, 0.16)
lh_arpeg(3, 38, [53, 56], [58, 62])

# Bar 3 — Cm7
melody(6, 75, 2.0, 0.42)
melody(8, 74, 1.0, 0.40)
alto(6, 67, 3.2, 0.16)
lh_arpeg(6, 36, [51, 55], [58, 62])

# Bar 4 — Abmaj7
melody(9, 72, 1.0, 0.42)
melody(10, 70, 1.0, 0.40)
melody(11, 68, 1.0, 0.40)
alto(9, 65, 3.2, 0.16)
lh_arpeg(9, 32, [48, 51], [55, 60])

# Bar 5 — Fm9
melody(12, 72, 2.0, 0.42)
melody(14, 70, 1.0, 0.40)
alto(12, 68, 3.2, 0.16)
lh_arpeg(12, 41, [56, 60], [63, 67])

# Bar 6 — Bb7sus4 → Bb7  (4-3 suspension in melody)
melody(15, 75, 1.0, 0.42)
melody(16, 74, 2.0, 0.42)
alto(15, 68, 3.2, 0.16)
n(15, 34, 3.4, 0.40)
n(15, 51, 1.0, 0.16)
n(16, 50, 2.0, 0.16)
n(15, 53, 3.0, 0.14)
n(16, 56, 2.0, 0.14)

# Bar 7 — Gø7
melody(18, 72, 1.0, 0.42)
melody(19, 73, 1.0, 0.42)
melody(20, 72, 1.0, 0.40)
alto(18, 70, 3.2, 0.16)
lh_arpeg(18, 43, [58, 61], [65, 70])

# Bar 8 — Cm7  (deceptive landing)
melody(21, 70, 1.5, 0.42)
melody(22.5, 72, 0.5, 0.36)
melody(23, 70, 1.0, 0.40)
alto(21, 67, 3.2, 0.16)
lh_arpeg(21, 36, [51, 55], [58, 63])

# Bar 9 — Fm7  (climbing toward the climax)
melody(24, 77, 1.0, 0.44)
melody(25, 75, 1.0, 0.42)
melody(26, 73, 1.0, 0.42)
alto(24, 68, 3.2, 0.16)
lh_arpeg(24, 41, [56, 60], [63, 68])

# Bar 10 — German augmented 6th  (Cb Eb Gb A)
melody(27, 73, 1.0, 0.42)
melody(28, 72, 1.0, 0.42)
melody(29, 69, 1.0, 0.46)            # the "+6" upper voice — pushes up to Bb
alto(27, 66, 3.2, 0.18)
n(27, 35, 3.4, 0.42)                 # Cb2 bass
n(27, 51, 1.0, 0.16)
n(28, 54, 2.0, 0.16)
n(28, 57, 2.0, 0.16)                 # A3 — completes the German +6

# Bar 11 — Bb7 (V7)  (outward resolution from Ger+6)
melody(30, 70, 1.5, 0.46)
melody(31.5, 68, 0.5, 0.34)
melody(32, 67, 1.0, 0.42)
alto(30, 62, 3.2, 0.16)
lh_arpeg(30, 34, [53, 56], [58, 62])

# Bar 12 — Ebmaj9  (final tonic, 9th enters last)
melody(33, 65, 0.4, 0.30)            # short appoggiatura into the tonic
melody(33.4, 63, 2.6, 0.46)
alto(33, 70, 3.4, 0.18)
n(33, 27, 3.6, 0.40)                 # Eb1 deep bass
n(33, 39, 3.6, 0.22)                 # Eb2 octave
n(33.5, 55, 3.0, 0.18)               # G3 (3rd) — slight delay
n(34, 58, 2.4, 0.18)                 # Bb3 (5th)
n(34.5, 65, 2.0, 0.18)               # F4 (9th) — last to bloom in
n(35, 63, 1.6, 0.18)                 # Eb4


if __name__ == "__main__":
    render(events, name="minuet_romantic", bpm=BPM, total_beats=36, time_sig=(3, 4))
