"""Simple classical-era minuet in G major. 8 bars, 3/4, 108 BPM.

Plain harmonic plan: I V I V | I vi V7 I.
Right hand outlines each bar's chord with three quarter notes.
Left hand plays the standard minuet "oompah-pah" — bass on beat 1,
two-note inner chord on beats 2 and 3.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "bin"))

from sequencer import render

BPM = 108

events: list[tuple[float, int, float, float]] = []


def rh(beat: float, midi: int, dur: float = 1.0) -> None:
    events.append((beat, midi, dur, 0.45))


def oompah(beat: float, root: int, voicing: list[int]) -> None:
    """Bass on beat 1, voiced two-note chord on beats 2 and 3."""
    events.append((beat,     root, 1.0, 0.40))
    for n in voicing:
        events.append((beat + 1, n, 0.9, 0.22))
        events.append((beat + 2, n, 0.9, 0.22))


# Bar 1 — I (G):    D5 B4 G4
rh(0, 74); rh(1, 71); rh(2, 67)
oompah(0, 43, [59, 62])

# Bar 2 — V (D):    A4 D5 F#5
rh(3, 69); rh(4, 74); rh(5, 78)
oompah(3, 50, [54, 57])

# Bar 3 — I:        G5 D5 B4
rh(6, 79); rh(7, 74); rh(8, 71)
oompah(6, 43, [59, 62])

# Bar 4 — V (half cadence): A4 dotted-half
rh(9, 69, 3)
oompah(9, 50, [54, 57])

# Bar 5 — I:        G4 B4 D5
rh(12, 67); rh(13, 71); rh(14, 74)
oompah(12, 43, [59, 62])

# Bar 6 — vi (Em):  E5 G5 B5
rh(15, 76); rh(16, 79); rh(17, 83)
oompah(15, 40, [55, 59])

# Bar 7 — V7 (D7):  A5 F#5 D5
rh(18, 81); rh(19, 78); rh(20, 74)
oompah(18, 50, [54, 60])

# Bar 8 — I:        G5 (held), with sustained tonic triad in LH
rh(21, 79, 3)
events.append((21, 43, 3.0, 0.38))   # bass G2
events.append((21, 59, 3.0, 0.18))   # B3
events.append((21, 62, 3.0, 0.18))   # D4

if __name__ == "__main__":
    from sequencer import cli_instrument
    args = cli_instrument()
    render(events, name="minuet_classical", bpm=BPM, total_beats=24,
           instrument=args.instrument, play=args.play)
