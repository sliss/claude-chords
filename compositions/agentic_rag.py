"""The Agentic RAG — a ragtime piano piece. 2/4, 96 BPM.

Form: 16-bar strain in C major (A 8 + A' 8). Standard stride LH. RH uses
the classic ragtime 3-3-2 syncopation (notes on the 1, the 'a' of 1, and
the '&' of 2 in 16th-note grouping) plus chromatic neighbor tones and
brief call-and-response motifs in the upper register — two retrieval
agents trading their findings, naturally.

Harmonic plan:
  A  | C  | C7 | F  | C  | C  | D7 | G7 | C  |
  A' | F  | Fm | C  | E7 | Am | D7 | G7 | C  |

Idiomatic colour: V7/IV (C7 → F), V/V (D7), modal-mixture iv (Fm) for
that bluesy half-step descent, V/vi (E7 → Am) walking back to V.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "bin"))

from sequencer import render

BPM = 96
BAR = 2.0  # 2/4: each bar is 2 beats

events: list[tuple[float, int, float, float]] = []


# ─── Helpers ────────────────────────────────────────────────────────
def n(beat: float, midi: int, dur: float, gain: float) -> None:
    if dur > 0 and gain > 0:
        events.append((beat, midi, dur, gain))


def stride(bar_start: float, bass1: int, bass2: int,
           chord_notes: list[int], gain_b: float = 0.42,
           gain_c: float = 0.20) -> None:
    """Classic ragtime LH for one 2/4 bar.

      beat 1     -> bass note (root)
      '&' of 1   -> chord stab
      beat 2     -> alternate bass (usually the 5th)
      '&' of 2   -> chord stab

    All durations are 0.45 beats so adjacent strikes don't overlap.
    """
    n(bar_start,        bass1, 0.45, gain_b)
    for c in chord_notes:
        n(bar_start + 0.5, c, 0.45, gain_c)
    n(bar_start + 1.0,  bass2, 0.45, gain_b)
    for c in chord_notes:
        n(bar_start + 1.5, c, 0.45, gain_c)


def rh_syncopated(bar_start: float, pitches6: list[int],
                  gain: float = 0.46) -> None:
    """Six-note 3-3-2 pattern over one bar (8 sixteenths).

    Onset pattern, in 16th-note positions:
        beat 0.00 (16th)   strong
        beat 0.25 (16th)   strong, runs into next
        beat 0.50 (8th)    long, syncopated
        beat 1.00 (16th)   pickup
        beat 1.25 (16th)   strong
        beat 1.50 (8th)    long, anticipates next bar

    pitches6 = the six MIDI notes filling those positions, in order.
    """
    p = pitches6
    accents = [1.00, 0.85, 1.05, 0.85, 0.92, 1.00]
    durs    = [0.25, 0.25, 0.50, 0.25, 0.25, 0.50]
    onsets  = [0.00, 0.25, 0.50, 1.00, 1.25, 1.50]
    for pitch, on, du, ac in zip(p, onsets, durs, accents):
        n(bar_start + on, pitch, du * 0.95, gain * ac)


def rh_run(bar_start: float, pitches: list[int], unit: float = 0.25,
           gain: float = 0.42) -> None:
    """Even sixteenth-note run; useful for cadential flourishes."""
    for i, p in enumerate(pitches):
        n(bar_start + i * unit, p, unit * 0.95, gain)


# ─── A section (bars 1-8) ──────────────────────────────────────────
# Bar 1 — C major: opening statement, octave leap E->G
stride(0 * BAR, 36, 43, [52, 55, 60])                    # C2 G2 / E3 G3 C4
rh_syncopated(0 * BAR, [76, 72, 79, 76, 72, 76])         # E5 C5 G5 E5 C5 E5

# Bar 2 — C7: Bb pulls toward F. Same RH shape with b7 colouring.
stride(1 * BAR, 36, 43, [52, 55, 58])                    # C2 G2 / E3 G3 Bb3
rh_syncopated(1 * BAR, [76, 70, 76, 79, 70, 79])         # E5 Bb4 E5 G5 Bb4 G5

# Bar 3 — F: subdominant arrival, melody up to A.
stride(2 * BAR, 41, 48, [53, 57, 60])                    # F2 C3 / F3 A3 C4
rh_syncopated(2 * BAR, [77, 81, 84, 81, 77, 72])         # F5 A5 C6 A5 F5 C5

# Bar 4 — C: return, descending arpeggio answer.
stride(3 * BAR, 36, 43, [52, 55, 60])
rh_syncopated(3 * BAR, [79, 76, 72, 76, 72, 67])         # G5 E5 C5 E5 C5 G4

# Bar 5 — C: restate with a small variation — the second "agent" enters
#           an octave below, doubling the figure (call-and-response feel).
stride(4 * BAR, 36, 43, [52, 55, 60])
rh_syncopated(4 * BAR, [76, 72, 79, 76, 72, 67])         # E5 C5 G5 E5 C5 G4
n(4 * BAR + 0.0, 64, 0.25, 0.18)                          # E4 doubling
n(4 * BAR + 0.5, 67, 0.5, 0.18)                           # G4 doubling

# Bar 6 — D7 (V/V): F# enters, bright lift toward G7.
stride(5 * BAR, 38, 45, [54, 57, 60])                    # D2 A2 / F#3 A3 C4
rh_syncopated(5 * BAR, [78, 74, 78, 81, 74, 81])         # F#5 D5 F#5 A5 D5 A5

# Bar 7 — G7: dominant, with the b7 (F) prominent.
stride(6 * BAR, 43, 50, [50, 53, 59])                    # G2 D3 / D3 F3 B3
rh_syncopated(6 * BAR, [77, 74, 79, 77, 74, 71])         # F5 D5 G5 F5 D5 B4

# Bar 8 — C: cadence back to tonic. Cadential chromatic walk-up
#           (E F F# G) on RH last two beats of the bar.
stride(7 * BAR, 36, 43, [52, 55, 60])
rh_run(7 * BAR + 0.0, [76, 72, 76, 79], unit=0.25, gain=0.45)  # E C E G
rh_run(7 * BAR + 1.0, [76, 77, 78, 79], unit=0.25, gain=0.40)  # E F F# G chromatic


# ─── A' section (bars 9-16) ────────────────────────────────────────
# Bar 9 — F: subdominant feature, RH up around the high A.
stride(8 * BAR, 41, 48, [53, 57, 60])                    # F2 C3 / F3 A3 C4
rh_syncopated(8 * BAR, [81, 77, 84, 81, 77, 72])         # A5 F5 C6 A5 F5 C5

# Bar 10 — Fm (modal mixture): drop the A to Ab. Half-step descent
#          gives that ragtime "pathos" moment before C returns.
stride(9 * BAR, 41, 48, [53, 56, 60])                    # F2 C3 / F3 Ab3 C4
rh_syncopated(9 * BAR, [80, 77, 84, 80, 77, 72])         # Ab5 F5 C6 Ab5 F5 C5

# Bar 11 — C: home, with a wider RH gesture (octave reach G4-G5).
stride(10 * BAR, 36, 43, [52, 55, 60])
rh_syncopated(10 * BAR, [76, 67, 76, 79, 76, 72])        # E5 G4 E5 G5 E5 C5

# Bar 12 — E7 (V/vi): G# leading tone, sets up Am.
stride(11 * BAR, 40, 47, [56, 59, 62])                   # E2 B2 / G#3 B3 D4
rh_syncopated(11 * BAR, [80, 76, 71, 76, 80, 71])        # G#5 E5 B4 E5 G#5 B4

# Bar 13 — Am: arrival on vi, melody outlines the triad.
stride(12 * BAR, 45, 52, [57, 60, 64])                   # A2 E3 / A3 C4 E4
rh_syncopated(12 * BAR, [81, 76, 72, 76, 81, 72])        # A5 E5 C5 E5 A5 C5

# Bar 14 — D7 (V/V): same shape as bar 6 to recall the A section.
stride(13 * BAR, 38, 45, [54, 57, 60])
rh_syncopated(13 * BAR, [78, 74, 78, 81, 74, 81])

# Bar 15 — G7: dominant, with a sweeping RH descent for cadential drive.
stride(14 * BAR, 43, 50, [50, 53, 59])
rh_run(14 * BAR + 0.0, [83, 81, 79, 77], unit=0.25, gain=0.45)  # B5 A5 G5 F5
rh_run(14 * BAR + 1.0, [74, 71, 67, 65], unit=0.25, gain=0.42)  # D5 B4 G4 F4

# Bar 16 — C: final tonic. RH plays rolled tonic chord, LH solid octave.
n(15 * BAR + 0.0, 36, 1.6, 0.50)                          # C2 bass
n(15 * BAR + 0.0, 48, 1.6, 0.40)                          # C3 octave
n(15 * BAR + 0.0, 60, 0.20, 0.42)                         # C5 (rolled)
n(15 * BAR + 0.10, 64, 0.20, 0.44)                        # E5
n(15 * BAR + 0.20, 67, 0.20, 0.46)                        # G5
n(15 * BAR + 0.30, 72, 1.5, 0.50)                         # C6 held


if __name__ == "__main__":
    from sequencer import cli_instrument
    args = cli_instrument()
    render(events, name="agentic_rag", bpm=BPM, total_beats=16 * BAR,
           time_sig=(2, 4), instrument=args.instrument, play=args.play)
