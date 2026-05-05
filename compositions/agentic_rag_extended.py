"""The Agentic RAG (extended). 2/4, 96 BPM.

Extended form with a full trio in the subdominant (F major), Joplin-style:

  Intro     (bars  1-4 ,  C major)   — stride pickup, descending RH fanfare
  A strain  (bars  5-20,  C major)   — the original 16-bar rag, lightly revoiced
  Trio C    (bars 21-36, F major)    — lyrical statement, less syncopated
  Trio C'   (bars 37-52, F major)    — same harmony, RH ornamented in 16ths
  A reprise (bars 53-60, C major)    — condensed home statement
  Coda      (bars 61-64, C major)    — cadential flourish

Trio harmonic plan (bars 21-36, in F):
  | F   | C7  | F   | F7  |  I  V7  I  V7/IV
  | Bb  | Bbm | F   | D7  |  IV iv  I  V/ii   (modal mixture borrowed from A)
  | Gm  | C7  | F   | F   |  ii V7  I  I
  | F   | A7  | Dm  | C7  |  I  V/vi vi V7    (turnaround back to A or C')

The A reprise drops back to C major via the C7 at the end of the trio
(C7 is V7 in F but functions as I7 in C — pivot chord).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "bin"))

from sequencer import render

BPM = 96
BAR = 2.0  # 2/4

events: list[tuple[float, int, float, float]] = []


# ─── Helpers ────────────────────────────────────────────────────────
def n(beat: float, midi: int, dur: float, gain: float) -> None:
    if dur > 0 and gain > 0:
        events.append((beat, midi, dur, gain))


def stride(bar_start: float, bass1: int, bass2: int,
           chord_notes: list[int], gain_b: float = 0.42,
           gain_c: float = 0.20) -> None:
    """Standard ragtime LH for one 2/4 bar."""
    n(bar_start,        bass1, 0.45, gain_b)
    for c in chord_notes:
        n(bar_start + 0.5, c, 0.45, gain_c)
    n(bar_start + 1.0,  bass2, 0.45, gain_b)
    for c in chord_notes:
        n(bar_start + 1.5, c, 0.45, gain_c)


def rh_syncopated(bar_start: float, pitches6: list[int],
                  gain: float = 0.46) -> None:
    """Six-note 3-3-2 pattern over one bar (8 sixteenths)."""
    accents = [1.00, 0.85, 1.05, 0.85, 0.92, 1.00]
    durs    = [0.25, 0.25, 0.50, 0.25, 0.25, 0.50]
    onsets  = [0.00, 0.25, 0.50, 1.00, 1.25, 1.50]
    for pitch, on, du, ac in zip(pitches6, onsets, durs, accents):
        n(bar_start + on, pitch, du * 0.95, gain * ac)


def rh_lyrical(bar_start: float, pitches4: list[int],
               gain: float = 0.45) -> None:
    """Cantabile 4-note line over one bar — a quarter, two eighths, a quarter.
    Used in the trio for a more singing line that still moves with the LH."""
    durs   = [0.50, 0.25, 0.25, 1.00]
    onsets = [0.00, 0.50, 0.75, 1.00]
    for pitch, on, du in zip(pitches4, onsets, durs):
        n(bar_start + on, pitch, du * 0.95, gain)


def rh_run(bar_start: float, pitches: list[int], unit: float = 0.25,
           gain: float = 0.42) -> None:
    """Even unit-note run; useful for cadential flourishes and 16th-note sweeps."""
    for i, p in enumerate(pitches):
        n(bar_start + i * unit, p, unit * 0.95, gain)


def rh_octaves(bar_start: float, pitches6: list[int],
               gain: float = 0.46) -> None:
    """Like rh_syncopated, but doubles each note an octave below — louder,
    punchier, used in the trio variation."""
    rh_syncopated(bar_start, pitches6, gain=gain)
    rh_syncopated(bar_start, [p - 12 for p in pitches6], gain=gain * 0.55)


# ─── Intro (bars 1-4) ──────────────────────────────────────────────
# Bar 1 — C: high RH fanfare, descending arpeggio
stride(0 * BAR, 36, 43, [52, 55, 60])
rh_run(0 * BAR + 0.0, [84, 79, 76, 72], unit=0.25, gain=0.46)  # C6 G5 E5 C5
n(0 * BAR + 1.0, 79, 0.5, 0.42)                                 # G5
n(0 * BAR + 1.5, 76, 0.5, 0.40)                                 # E5

# Bar 2 — G7: stepwise descent
stride(1 * BAR, 43, 50, [50, 53, 59])
rh_run(1 * BAR + 0.0, [77, 74, 71, 67], unit=0.25, gain=0.44)  # F5 D5 B4 G4
n(1 * BAR + 1.0, 71, 0.5, 0.42)                                 # B4
n(1 * BAR + 1.5, 74, 0.5, 0.40)                                 # D5

# Bar 3 — C: rebound up
stride(2 * BAR, 36, 43, [52, 55, 60])
rh_run(2 * BAR + 0.0, [72, 76, 79, 84], unit=0.25, gain=0.46)  # C5 E5 G5 C6
n(2 * BAR + 1.0, 79, 0.5, 0.42)                                 # G5
n(2 * BAR + 1.5, 76, 0.5, 0.40)                                 # E5

# Bar 4 — G7: half-cadence pickup into A strain
stride(3 * BAR, 43, 50, [50, 53, 59])
rh_run(3 * BAR + 0.0, [83, 79, 77, 74], unit=0.25, gain=0.44)  # B5 G5 F5 D5
rh_run(3 * BAR + 1.0, [71, 74, 77, 79], unit=0.25, gain=0.42)  # B4 D5 F5 G5  (lift)


# ─── A strain (bars 5-20) ──────────────────────────────────────────
A0 = 4 * BAR

# Bar 5 — C
stride(A0 + 0 * BAR, 36, 43, [52, 55, 60])
rh_syncopated(A0 + 0 * BAR, [76, 72, 79, 76, 72, 76])

# Bar 6 — C7 (V7/IV)
stride(A0 + 1 * BAR, 36, 43, [52, 55, 58])
rh_syncopated(A0 + 1 * BAR, [76, 70, 76, 79, 70, 79])

# Bar 7 — F
stride(A0 + 2 * BAR, 41, 48, [53, 57, 60])
rh_syncopated(A0 + 2 * BAR, [77, 81, 84, 81, 77, 72])

# Bar 8 — C
stride(A0 + 3 * BAR, 36, 43, [52, 55, 60])
rh_syncopated(A0 + 3 * BAR, [79, 76, 72, 76, 72, 67])

# Bar 9 — C (with octave-below doubling: the second "agent" answers)
stride(A0 + 4 * BAR, 36, 43, [52, 55, 60])
rh_syncopated(A0 + 4 * BAR, [76, 72, 79, 76, 72, 67])
n(A0 + 4 * BAR + 0.0, 64, 0.25, 0.18)
n(A0 + 4 * BAR + 0.5, 67, 0.5, 0.18)

# Bar 10 — D7 (V/V)
stride(A0 + 5 * BAR, 38, 45, [54, 57, 60])
rh_syncopated(A0 + 5 * BAR, [78, 74, 78, 81, 74, 81])

# Bar 11 — G7
stride(A0 + 6 * BAR, 43, 50, [50, 53, 59])
rh_syncopated(A0 + 6 * BAR, [77, 74, 79, 77, 74, 71])

# Bar 12 — C with chromatic walk-up
stride(A0 + 7 * BAR, 36, 43, [52, 55, 60])
rh_run(A0 + 7 * BAR + 0.0, [76, 72, 76, 79], unit=0.25, gain=0.45)
rh_run(A0 + 7 * BAR + 1.0, [76, 77, 78, 79], unit=0.25, gain=0.40)

# Bar 13 — F
stride(A0 + 8 * BAR, 41, 48, [53, 57, 60])
rh_syncopated(A0 + 8 * BAR, [81, 77, 84, 81, 77, 72])

# Bar 14 — Fm (modal mixture)
stride(A0 + 9 * BAR, 41, 48, [53, 56, 60])
rh_syncopated(A0 + 9 * BAR, [80, 77, 84, 80, 77, 72])

# Bar 15 — C
stride(A0 + 10 * BAR, 36, 43, [52, 55, 60])
rh_syncopated(A0 + 10 * BAR, [76, 67, 76, 79, 76, 72])

# Bar 16 — E7 (V/vi)
stride(A0 + 11 * BAR, 40, 47, [56, 59, 62])
rh_syncopated(A0 + 11 * BAR, [80, 76, 71, 76, 80, 71])

# Bar 17 — Am
stride(A0 + 12 * BAR, 45, 52, [57, 60, 64])
rh_syncopated(A0 + 12 * BAR, [81, 76, 72, 76, 81, 72])

# Bar 18 — D7 (V/V)
stride(A0 + 13 * BAR, 38, 45, [54, 57, 60])
rh_syncopated(A0 + 13 * BAR, [78, 74, 78, 81, 74, 81])

# Bar 19 — G7 with sweeping descent
stride(A0 + 14 * BAR, 43, 50, [50, 53, 59])
rh_run(A0 + 14 * BAR + 0.0, [83, 81, 79, 77], unit=0.25, gain=0.45)
rh_run(A0 + 14 * BAR + 1.0, [74, 71, 67, 65], unit=0.25, gain=0.42)

# Bar 20 — C7 PIVOT (V7 in F): turn to the trio. Rolled chord with extra
# Bb to start preparing the ear for F major.
stride(A0 + 15 * BAR, 36, 43, [52, 55, 58])
n(A0 + 15 * BAR + 0.00, 76, 0.20, 0.42)   # E5
n(A0 + 15 * BAR + 0.10, 79, 0.20, 0.44)   # G5
n(A0 + 15 * BAR + 0.20, 82, 0.30, 0.46)   # Bb5  (the pivot tone)
n(A0 + 15 * BAR + 1.00, 82, 0.50, 0.42)   # Bb5 again (anticipates F)
n(A0 + 15 * BAR + 1.50, 81, 0.50, 0.40)   # A5 leading-tone-of-F-major-feel


# ─── Trio C — bars 21-36, in F major ───────────────────────────────
T0 = (4 + 16) * BAR

# Trio bar 1 — F
stride(T0 + 0 * BAR, 41, 48, [53, 57, 60])
rh_lyrical(T0 + 0 * BAR, [77, 81, 79, 77])      # F5 A5 G5 F5

# Trio bar 2 — C7 (V7)
stride(T0 + 1 * BAR, 36, 43, [52, 55, 58])
rh_lyrical(T0 + 1 * BAR, [76, 79, 77, 76])      # E5 G5 F5 E5

# Trio bar 3 — F
stride(T0 + 2 * BAR, 41, 48, [53, 57, 60])
rh_lyrical(T0 + 2 * BAR, [77, 84, 81, 77])      # F5 C6 A5 F5

# Trio bar 4 — F7 (V7/IV: prepares Bb)
stride(T0 + 3 * BAR, 41, 48, [53, 57, 63])      # add Eb in chord
rh_lyrical(T0 + 3 * BAR, [77, 75, 74, 75])      # F5 Eb5 D5 Eb5  (Eb = b7 of F)

# Trio bar 5 — Bb (IV)
stride(T0 + 4 * BAR, 46, 53, [58, 62, 65])      # Bb2 F3 / Bb3 D4 F4
rh_lyrical(T0 + 4 * BAR, [74, 77, 82, 77])      # D5 F5 Bb5 F5

# Trio bar 6 — Bbm (iv, modal mixture — gives the trio its blue moment)
stride(T0 + 5 * BAR, 46, 53, [58, 61, 65])      # Bb2 F3 / Bb3 Db4 F4
rh_lyrical(T0 + 5 * BAR, [73, 77, 81, 77])      # Db5 F5 A5 F5

# Trio bar 7 — F
stride(T0 + 6 * BAR, 41, 48, [53, 57, 60])
rh_lyrical(T0 + 6 * BAR, [72, 77, 76, 72])      # C5 F5 E5 C5

# Trio bar 8 — D7 (V/ii: leads to Gm)
stride(T0 + 7 * BAR, 38, 45, [54, 57, 60])
rh_lyrical(T0 + 7 * BAR, [78, 74, 78, 81])      # F#5 D5 F#5 A5

# Trio bar 9 — Gm (ii)
stride(T0 + 8 * BAR, 43, 50, [55, 58, 62])      # G2 D3 / G3 Bb3 D4
rh_lyrical(T0 + 8 * BAR, [79, 82, 79, 74])      # G5 Bb5 G5 D5

# Trio bar 10 — C7 (V7)
stride(T0 + 9 * BAR, 36, 43, [52, 55, 58])
rh_lyrical(T0 + 9 * BAR, [76, 79, 82, 79])      # E5 G5 Bb5 G5

# Trio bar 11 — F
stride(T0 + 10 * BAR, 41, 48, [53, 57, 60])
rh_lyrical(T0 + 10 * BAR, [77, 81, 84, 81])     # F5 A5 C6 A5

# Trio bar 12 — F (sustained, breathing space)
stride(T0 + 11 * BAR, 41, 48, [53, 57, 60])
n(T0 + 11 * BAR + 0.0, 77, 1.0, 0.40)            # F5 half-note
n(T0 + 11 * BAR + 1.0, 81, 0.5, 0.42)            # A5 quarter
n(T0 + 11 * BAR + 1.5, 84, 0.5, 0.44)            # C6 quarter

# Trio bar 13 — F (ascending sequence start)
stride(T0 + 12 * BAR, 41, 48, [53, 57, 60])
rh_lyrical(T0 + 12 * BAR, [84, 81, 84, 86])     # C6 A5 C6 D6

# Trio bar 14 — A7 (V/vi: leads to Dm via secondary dominant)
stride(T0 + 13 * BAR, 45, 52, [57, 61, 64])     # A2 E3 / A3 C#4 E4
rh_lyrical(T0 + 13 * BAR, [85, 81, 85, 88])     # C#6 A5 C#6 E6

# Trio bar 15 — Dm (vi)
stride(T0 + 14 * BAR, 38, 45, [50, 53, 57])     # D2 A2 / D3 F3 A3
rh_lyrical(T0 + 14 * BAR, [86, 81, 77, 74])     # D6 A5 F5 D5

# Trio bar 16 — C7 (V7 of F: cadential, also pivots back to C eventually)
stride(T0 + 15 * BAR, 36, 43, [52, 55, 58])
rh_run(T0 + 15 * BAR + 0.0, [82, 79, 76, 74], unit=0.25, gain=0.44)  # Bb5 G5 E5 D5
rh_run(T0 + 15 * BAR + 1.0, [72, 70, 67, 64], unit=0.25, gain=0.42)  # C5 Bb4 G4 E4


# ─── Trio C' — bars 37-52, F major variation ───────────────────────
# Same harmony as C, but RH plays octave-doubled syncopated figures —
# the "agents" are now confidently amplifying their findings.
TP0 = T0 + 16 * BAR

# Trio' bar 1 — F (octaves)
stride(TP0 + 0 * BAR, 41, 48, [53, 57, 60])
rh_octaves(TP0 + 0 * BAR, [81, 77, 84, 81, 77, 81])     # A F C A F A

# Trio' bar 2 — C7
stride(TP0 + 1 * BAR, 36, 43, [52, 55, 58])
rh_octaves(TP0 + 1 * BAR, [79, 76, 79, 82, 76, 82])     # G E G Bb E Bb

# Trio' bar 3 — F
stride(TP0 + 2 * BAR, 41, 48, [53, 57, 60])
rh_octaves(TP0 + 2 * BAR, [84, 81, 89, 84, 81, 77])     # C A F(high) C A F

# Trio' bar 4 — F7 with chromatic descent
stride(TP0 + 3 * BAR, 41, 48, [53, 57, 63])
rh_run(TP0 + 3 * BAR + 0.0, [82, 81, 80, 79], unit=0.25, gain=0.44)  # Bb A Ab G
rh_run(TP0 + 3 * BAR + 1.0, [78, 77, 76, 75], unit=0.25, gain=0.42)  # F# F E Eb

# Trio' bar 5 — Bb
stride(TP0 + 4 * BAR, 46, 53, [58, 62, 65])
rh_octaves(TP0 + 4 * BAR, [82, 77, 86, 82, 77, 74])     # Bb F D6 Bb F D

# Trio' bar 6 — Bbm
stride(TP0 + 5 * BAR, 46, 53, [58, 61, 65])
rh_octaves(TP0 + 5 * BAR, [82, 77, 85, 82, 77, 73])     # Bb F C#6 Bb F Db

# Trio' bar 7 — F (broad)
stride(TP0 + 6 * BAR, 41, 48, [53, 57, 60])
rh_octaves(TP0 + 6 * BAR, [81, 77, 84, 81, 77, 72])     # A F C A F C

# Trio' bar 8 — D7
stride(TP0 + 7 * BAR, 38, 45, [54, 57, 60])
rh_octaves(TP0 + 7 * BAR, [78, 74, 78, 81, 74, 81])

# Trio' bar 9 — Gm with running 16ths
stride(TP0 + 8 * BAR, 43, 50, [55, 58, 62])
rh_run(TP0 + 8 * BAR + 0.0, [79, 82, 86, 82], unit=0.25, gain=0.45)  # G Bb D6 Bb
rh_run(TP0 + 8 * BAR + 1.0, [79, 74, 79, 82], unit=0.25, gain=0.42)  # G D G Bb

# Trio' bar 10 — C7
stride(TP0 + 9 * BAR, 36, 43, [52, 55, 58])
rh_run(TP0 + 9 * BAR + 0.0, [76, 79, 82, 79], unit=0.25, gain=0.45)  # E G Bb G
rh_run(TP0 + 9 * BAR + 1.0, [76, 72, 76, 79], unit=0.25, gain=0.42)  # E C E G

# Trio' bar 11 — F (climax)
stride(TP0 + 10 * BAR, 41, 48, [53, 57, 60])
rh_run(TP0 + 10 * BAR + 0.0, [89, 86, 84, 81], unit=0.25, gain=0.50)  # F6 D C A (high)
rh_run(TP0 + 10 * BAR + 1.0, [77, 81, 84, 89], unit=0.25, gain=0.50)

# Trio' bar 12 — F (relax)
stride(TP0 + 11 * BAR, 41, 48, [53, 57, 60])
rh_lyrical(TP0 + 11 * BAR, [84, 81, 77, 81])

# Trio' bar 13 — F
stride(TP0 + 12 * BAR, 41, 48, [53, 57, 60])
rh_octaves(TP0 + 12 * BAR, [84, 81, 86, 84, 81, 77])

# Trio' bar 14 — A7
stride(TP0 + 13 * BAR, 45, 52, [57, 61, 64])
rh_octaves(TP0 + 13 * BAR, [85, 81, 88, 85, 81, 77])

# Trio' bar 15 — Dm
stride(TP0 + 14 * BAR, 38, 45, [50, 53, 57])
rh_octaves(TP0 + 14 * BAR, [86, 81, 77, 81, 86, 74])

# Trio' bar 16 — C7 → pivot back to C major (trio over)
stride(TP0 + 15 * BAR, 36, 43, [52, 55, 58])
rh_run(TP0 + 15 * BAR + 0.0, [82, 79, 76, 72], unit=0.25, gain=0.46)  # Bb G E C
rh_run(TP0 + 15 * BAR + 1.0, [70, 67, 64, 60], unit=0.25, gain=0.44)  # Bb4 G4 E4 C4


# ─── A reprise (bars 53-60) ────────────────────────────────────────
# Compressed return — first 8 bars of A strain, ending strongly on tonic.
R0 = TP0 + 16 * BAR

# Reprise bar 1 — C
stride(R0 + 0 * BAR, 36, 43, [52, 55, 60])
rh_syncopated(R0 + 0 * BAR, [76, 72, 79, 76, 72, 76])

# Reprise bar 2 — C7
stride(R0 + 1 * BAR, 36, 43, [52, 55, 58])
rh_syncopated(R0 + 1 * BAR, [76, 70, 76, 79, 70, 79])

# Reprise bar 3 — F
stride(R0 + 2 * BAR, 41, 48, [53, 57, 60])
rh_syncopated(R0 + 2 * BAR, [77, 81, 84, 81, 77, 72])

# Reprise bar 4 — C
stride(R0 + 3 * BAR, 36, 43, [52, 55, 60])
rh_syncopated(R0 + 3 * BAR, [79, 76, 72, 76, 72, 67])

# Reprise bar 5 — D7
stride(R0 + 4 * BAR, 38, 45, [54, 57, 60])
rh_syncopated(R0 + 4 * BAR, [78, 74, 78, 81, 74, 81])

# Reprise bar 6 — G7
stride(R0 + 5 * BAR, 43, 50, [50, 53, 59])
rh_syncopated(R0 + 5 * BAR, [77, 74, 79, 77, 74, 71])

# Reprise bar 7 — C with chromatic walk
stride(R0 + 6 * BAR, 36, 43, [52, 55, 60])
rh_run(R0 + 6 * BAR + 0.0, [76, 72, 76, 79], unit=0.25, gain=0.45)
rh_run(R0 + 6 * BAR + 1.0, [76, 77, 78, 79], unit=0.25, gain=0.42)

# Reprise bar 8 — G7 (sets up the coda)
stride(R0 + 7 * BAR, 43, 50, [50, 53, 59])
rh_run(R0 + 7 * BAR + 0.0, [83, 81, 79, 77], unit=0.25, gain=0.45)
rh_run(R0 + 7 * BAR + 1.0, [74, 71, 67, 65], unit=0.25, gain=0.42)


# ─── Coda (bars 61-64) ─────────────────────────────────────────────
C0 = R0 + 8 * BAR

# Coda bar 1 — F (subdominant nostalgia)
stride(C0 + 0 * BAR, 41, 48, [53, 57, 60])
rh_octaves(C0 + 0 * BAR, [81, 77, 84, 81, 77, 81])

# Coda bar 2 — Fdim7 (chromatic surprise — common ragtime cliché)
stride(C0 + 1 * BAR, 41, 48, [53, 56, 59])      # F2 C3 / F3 Ab3 B3
rh_run(C0 + 1 * BAR + 0.0, [80, 77, 74, 71], unit=0.25, gain=0.45)
rh_run(C0 + 1 * BAR + 1.0, [68, 71, 74, 77], unit=0.25, gain=0.42)

# Coda bar 3 — C / G7 cadential six-four
stride(C0 + 2 * BAR, 43, 50, [52, 55, 60])      # G bass with C chord (cadential 6-4)
rh_run(C0 + 2 * BAR + 0.0, [79, 76, 72, 67], unit=0.25, gain=0.46)  # G E C G
rh_run(C0 + 2 * BAR + 1.0, [71, 74, 77, 79], unit=0.25, gain=0.44)  # B D F G  (V7)

# Coda bar 4 — C: rolled tonic with octave bass
n(C0 + 3 * BAR + 0.0, 36, 1.6, 0.55)             # C2
n(C0 + 3 * BAR + 0.0, 48, 1.6, 0.42)             # C3
n(C0 + 3 * BAR + 0.0, 55, 0.20, 0.40)            # G3
n(C0 + 3 * BAR + 0.10, 60, 0.20, 0.42)           # C4
n(C0 + 3 * BAR + 0.20, 64, 0.20, 0.44)           # E4
n(C0 + 3 * BAR + 0.30, 67, 0.20, 0.46)           # G4
n(C0 + 3 * BAR + 0.40, 72, 0.20, 0.48)           # C5
n(C0 + 3 * BAR + 0.50, 76, 0.20, 0.50)           # E5
n(C0 + 3 * BAR + 0.60, 79, 0.20, 0.52)           # G5
n(C0 + 3 * BAR + 0.70, 84, 1.3, 0.55)            # C6 — held final


TOTAL_BARS = 64

if __name__ == "__main__":
    from sequencer import cli_instrument
    args = cli_instrument()
    render(events, name="agentic_rag_extended", bpm=BPM,
           total_beats=TOTAL_BARS * BAR, time_sig=(2, 4),
           instrument=args.instrument, play=args.play)
