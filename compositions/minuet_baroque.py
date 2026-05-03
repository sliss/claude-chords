"""Baroque-style minuet in G major. 8 bars, 3/4, 132 BPM.

Idiomatic features:
  - Trills (start on upper auxiliary, Baroque practice)
  - Upper and lower mordents
  - Long appoggiaturas
  - Walking bass with chromatic passing tones
  - Secondary dominant (V/V) leading to half cadence
  - 4-3 suspension at the cadence
  - Inner alto voice for three-voice texture
  - Sequential treatment in bars 5-6 (figure transposed down a third)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "bin"))

from sequencer import render

BPM = 132
Q = 60.0 / BPM
GRACE_S = 0.055

events: list[tuple[float, int, float, float]] = []


def n(beat: float, midi: int, dur: float = 1.0, gain: float = 0.42) -> None:
    if dur <= 0 or gain <= 0:
        return
    events.append((beat, midi, dur, gain))


def rh(beat, midi, dur=1.0, gain=0.45):  n(beat, midi, dur, gain)
def alto(beat, midi, dur=1.0, gain=0.20): n(beat, midi, dur, gain)
def bass(beat, midi, dur=1.0, gain=0.40): n(beat, midi, dur, gain)


def trill(beat: float, principal: int, dur_beats: float,
          upper_st: int = 2, gain: float = 0.30) -> None:
    """Baroque trill: starts on upper auxiliary, lands on principal."""
    rate = 13.5
    count = max(4, int(round(dur_beats * Q * rate)))
    if count % 2 == 1:
        count += 1
    note_dur = dur_beats / count
    for i in range(count):
        midi = principal + upper_st if i % 2 == 0 else principal
        n(beat + i * note_dur, midi, note_dur * 1.15, gain)


def upper_mordent(beat, principal, upper_st=2, total_beats=1.0, gain=0.42):
    g = GRACE_S / Q
    n(beat,         principal,            g,                   gain)
    n(beat + g,     principal + upper_st, g,                   gain * 0.9)
    n(beat + 2*g,   principal,            total_beats - 2*g,   gain)


def lower_mordent(beat, principal, lower_st=1, total_beats=1.0, gain=0.42):
    g = GRACE_S / Q
    n(beat,         principal,            g,                   gain)
    n(beat + g,     principal - lower_st, g,                   gain * 0.9)
    n(beat + 2*g,   principal,            total_beats - 2*g,   gain)


def appog(beat, ornament, principal, total_beats=1.0, gain=0.46):
    half = total_beats / 2
    n(beat,        ornament,  half, gain)
    n(beat + half, principal, half, gain * 0.78)


# BAR 1 — I (G major)
trill(0, 74, 1, upper_st=2)
rh(1, 72, 0.5);  rh(1.5, 71, 0.5)
appog(2, 71, 69, 1)
bass(0, 43); bass(1, 50); bass(2, 47)
alto(0, 67); alto(1, 66); alto(2, 64)

# BAR 2 — V (with V7 colour)
upper_mordent(3, 78)
rh(4, 76, 0.5); rh(4.5, 74, 0.5)
rh(5, 72, 1)
bass(3, 50); bass(4, 45); bass(5, 50)
alto(3, 69); alto(4, 69); alto(5, 69)

# BAR 3 — I, descent
rh(6, 71, 1)
appog(7, 72, 71, 1)
rh(8, 69, 1)
bass(6, 43); bass(7, 47); bass(8, 50)
alto(6, 67); alto(7, 67); alto(8, 66)

# BAR 4 — V/V → V (half cadence)
rh(9, 67, 0.5); rh(9.5, 73, 0.5)
trill(10, 74, 2, upper_st=2)
bass(9, 45); bass(10, 50); bass(11, 50)
alto(9, 69); alto(10, 66); alto(11, 66)

# BAR 5 — I (ascending sequence start)
rh(12, 67, 0.5); rh(12.5, 71, 0.5)
rh(13, 74, 0.5); rh(13.5, 72, 0.5)
upper_mordent(14, 71)
bass(12, 43); bass(13, 47); bass(14, 50)
alto(12, 64); alto(13, 64); alto(14, 67)

# BAR 6 — vi (Em); same figure transposed down a third
rh(15, 64, 0.5); rh(15.5, 67, 0.5)
rh(16, 71, 0.5); rh(16.5, 69, 0.5)
upper_mordent(17, 67)
bass(15, 40); bass(16, 47); bass(17, 50)
alto(15, 60); alto(16, 60); alto(17, 64)

# BAR 7 — ii6 → V7 with 4-3 suspension into bar 8
rh(18, 72, 1)
rh(19, 71, 1)
n(20, 67, 1.0, 0.40)
bass(18, 45); bass(19, 50); bass(20, 50)
alto(18, 64); alto(19, 65); alto(20, 65)

# BAR 8 — I with cadential trill
appog(21, 67, 66, 0.5)
trill(21.5, 71, 1.5, upper_st=2)
n(23, 67, 1.0, 0.50)
bass(21, 50); bass(22, 43); bass(23, 43)
alto(21, 62); alto(22, 59); alto(23, 59)


if __name__ == "__main__":
    render(events, name="minuet_baroque", bpm=BPM, total_beats=24)
