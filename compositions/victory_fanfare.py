"""Victory Fanfare — variation on Nobuo Uematsu's Final Fantasy cue.

Compact arrangement: ~5 seconds. C major, 4/4, 120 BPM.

Form (tight):
  Beat 0     — tutti C major punch
  Beats 1-3  — gesture 1: "ta-ta-ta-TAAAH" → E (3rd), in parallel sixths
  Beats 3-5  — gesture 2: "ta-ta-ta-TAAAH" → G (5th)
  Beat 5     — V7 stab + triplet pickup back to tonic
  Beat 6.25  — full-register C major arrival, held ~2 beats

The original cue is in Bb major; transposed to C here. The "ta-ta-ta-TAH"
target lands on the 3rd then the 5th of the key — same shape as the
original's Bb→D, Bb→F gestures. Final chord spans five octaves.

Played after `git push` succeeds when the shell function is installed.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "bin"))

from sequencer import render

BPM = 120

events: list[tuple[float, int, float, float]] = []


def n(beat: float, midi: int, dur: float, gain: float) -> None:
    if dur > 0 and gain > 0:
        events.append((beat, midi, dur, gain))


def fanfare_gesture(start: float, target: int, harmony_below: int) -> None:
    """The signature 'ta-ta-ta-TAAAH'.

    Three rapid C5 16ths (after a half-beat breath of silence to articulate
    the gesture) into a held target note with parallel `harmony_below`
    underneath for that brass-section sixth.
    """
    PICKUP = 72  # C5 — the tonic-hammer that makes the figure iconic
    for off in (0.50, 0.75, 1.00):
        n(start + off, PICKUP, 0.20, 0.45)
    n(start + 1.25, target,        0.75, 0.55)
    n(start + 1.25, harmony_below, 0.75, 0.40)


# ─── Beat 0: tutti punch ───────────────────────────────────────────
PUNCH_DUR = 0.40
for midi, gain in [
    (36, 0.55), (48, 0.45), (52, 0.32), (55, 0.32),
    (60, 0.45), (64, 0.40), (67, 0.42), (72, 0.45),
]:
    n(0.00, midi, PUNCH_DUR, gain)


# ─── Beats 1-3: gesture → E (3rd), with G4 below ──────────────────
fanfare_gesture(start=1.0, target=76, harmony_below=67)

# ─── Beats 3-5: gesture → G (5th), with B4 below ──────────────────
fanfare_gesture(start=3.0, target=79, harmony_below=71)


# ─── Beat 5: V7 stab ───────────────────────────────────────────────
V7_DUR = 0.60
for midi, gain in [
    (43, 0.50),   # G2 bass
    (53, 0.42),   # F3 (the 7th)
    (59, 0.42),   # B3 (leading tone)
    (65, 0.45),   # F4
    (71, 0.48),   # B4
    (74, 0.50),   # D5
]:
    n(5.00, midi, V7_DUR, gain)


# ─── Beat 5.75: triplet pickup launching the arrival ──────────────
n(5.75, 72, 0.18, 0.50)   # C5
n(5.95, 76, 0.18, 0.55)   # E5
n(6.15, 79, 0.18, 0.60)   # G5


# ─── Beat 6.35: full-register C major arrival, held ───────────────
ARRIVAL = 6.35
ARR_DUR = 2.50
for midi, gain in [
    (36, 0.60),   # C2 (low)
    (43, 0.42),   # G2
    (48, 0.45),   # C3
    (52, 0.32),   # E3
    (55, 0.32),   # G3
    (60, 0.45),   # C4
    (64, 0.42),   # E4
    (67, 0.45),   # G4
    (72, 0.50),   # C5
    (76, 0.55),   # E5
    (79, 0.60),   # G5
    (84, 0.68),   # C6 (brightest top)
]:
    n(ARRIVAL, midi, ARR_DUR, gain)


# ─── LH continuity: keep bass moving between the punch and V7 ─────
n(1.00, 36, 0.40, 0.40)   # C2 under gesture 1
n(2.00, 43, 0.40, 0.32)   # G2
n(3.00, 36, 0.40, 0.40)   # C2 under gesture 2
n(4.00, 43, 0.40, 0.32)   # G2


TOTAL_BEATS = ARRIVAL + ARR_DUR

if __name__ == "__main__":
    from sequencer import cli_instrument
    args = cli_instrument()
    render(events, name="victory_fanfare", bpm=BPM,
           total_beats=TOTAL_BEATS, time_sig=(4, 4),
           instrument=args.instrument, play=args.play)
