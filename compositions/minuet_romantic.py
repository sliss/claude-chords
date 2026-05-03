"""Romantic minuet in Eb major. 28 bars, 3/4, 80 BPM. Rounded binary form.

Structure (no literal repeats, so it doesn't drag at this tempo):

  A  section  bars  1-8   — Eb major, modulates to Bb (V) by the end
  B  section  bars  9-16  — opens in Bb, harmonic excursion through related keys,
                             cadences back on V7/Eb (Bb7) to set up the return
  A' section  bars 17-28  — return in Eb, original opening + extended coda
                             built around the German augmented 6th

Texture stays the same throughout: bass on beat 1 (rings the bar),
two-note inner voicing arpeggiated on beats 2 and 3, sustained alto in
the middle, melody on top.
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
    """Bass on beat 1 (rings full bar), 2-note voicings on beats 2 and 3."""
    n(start_beat,        bass, 3.4, 0.38)
    for m in mid_a:
        n(start_beat + 1, m, 2.4, 0.16)
    for m in mid_b:
        n(start_beat + 2, m, 1.7, 0.16)


# Pitch reference (MIDI):
#   Eb1=27 Bb1=34 Cb2=35 C2=36 D2=38 Eb2=39 F2=41 G2=43 Ab2=44 Bb2=46
#   B2=47 Cb3=47 C3=48 D3=50 Eb3=51 E3=52 F3=53 F#3=54 Gb3=54 G3=55
#   Ab3=56 A3=57 Bb3=58 Cb4=59 B3=59 C4=60 Db4=61 D4=62 Eb4=63 E4=64
#   F4=65 F#4=66 Gb4=66 G4=67 Ab4=68 A4=69 Bb4=70 Cb5=71 B4=71 C5=72
#   Db5=73 D5=74 Eb5=75 E5=76 F5=77 F#5=78 Gb5=78 G5=79 Ab5=80 A5=81
#   Bb5=82

# ════════════════════════════════════════════════════════════════════
# A SECTION — bars 1-8, modulating Eb → Bb (V)
# ════════════════════════════════════════════════════════════════════

# Bar 1 — Ebmaj7  (I — opening)
melody(0, 79, 3.0, 0.44)             # G5 dotted-half
alto(0, 70, 3.2, 0.16)
lh_arpeg(0, 39, [55, 58], [62, 65])  # Eb2 | G3 Bb3 | D4 F4

# Bar 2 — Cm7  (vi)
melody(3, 77, 1.0, 0.42)             # F5
melody(4, 75, 1.0, 0.40)             # Eb5
melody(5, 74, 1.0, 0.40)             # D5
alto(3, 67, 3.2, 0.16)
lh_arpeg(3, 36, [51, 55], [58, 62])  # C2 | Eb3 G3 | Bb3 D4

# Bar 3 — Fm7  (ii)
melody(6, 75, 2.0, 0.42)             # Eb5 half-note
melody(8, 72, 1.0, 0.40)             # C5
alto(6, 68, 3.2, 0.16)
lh_arpeg(6, 41, [56, 60], [63, 67])  # F2 | Ab3 C4 | Eb4 G4

# Bar 4 — Bb7sus4 → Bb7  (V with 4-3 suspension)
melody(9, 75, 1.0, 0.42)             # Eb5 (the sus4)
melody(10, 74, 2.0, 0.42)            # D5 (resolves down)
alto(9, 68, 3.2, 0.16)               # Ab4 (b7 of Bb)
n(9, 34, 3.4, 0.40)                  # Bb1 bass
n(9, 51, 1.0, 0.16)                  # Eb3 sus4
n(10, 50, 2.0, 0.16)                 # D3 (resolves to 3rd)
n(9, 53, 3.0, 0.14)                  # F3 sustained
n(10, 56, 2.0, 0.14)                 # Ab3 (b7)

# Bar 5 — Ebmaj7  (return to I, restatement)
melody(12, 79, 2.0, 0.42)            # G5 half
melody(14, 77, 1.0, 0.40)            # F5
alto(12, 70, 3.2, 0.16)
lh_arpeg(12, 39, [55, 58], [62, 65])

# Bar 6 — Abmaj7  (IV — lush descent begins)
melody(15, 75, 1.0, 0.42)            # Eb5
melody(16, 74, 1.0, 0.40)            # D5
melody(17, 72, 1.0, 0.40)            # C5
alto(15, 65, 3.2, 0.16)              # F4 (3rd of Ab)
lh_arpeg(15, 32, [48, 51], [55, 60]) # Ab1 | C3 Eb3 | G3 C4

# Bar 7 — F7  (V/V — secondary dominant pivot, has A natural)
melody(18, 69, 1.0, 0.44)            # A4 (chromatic — leading tone of Bb!)
melody(19, 72, 1.0, 0.42)            # C5
melody(20, 75, 1.0, 0.42)            # Eb5
alto(18, 65, 3.2, 0.16)
lh_arpeg(18, 41, [57, 60], [63, 65]) # F2 | A3 C4 | Eb4 F4   (F7 = F A C Eb)

# Bar 8 — Bb major  (V — half-cadence in Eb / new tonic for B section)
melody(21, 74, 2.0, 0.46)            # D5 half (the 3rd of Bb)
melody(23, 77, 1.0, 0.44)            # F5 (the 5th)
alto(21, 70, 3.2, 0.16)              # Bb4
lh_arpeg(21, 34, [50, 53], [58, 62]) # Bb1 | D3 F3 | Bb3 D4


# ════════════════════════════════════════════════════════════════════
# B SECTION — bars 9-16, in Bb, harmonic excursion back to V7/Eb
# ════════════════════════════════════════════════════════════════════

# Bar 9 — Bbmaj7  (I in Bb — restful start to B)
melody(24, 74, 3.0, 0.42)            # D5 dotted-half (sustained, restful)
alto(24, 70, 3.2, 0.16)
lh_arpeg(24, 34, [50, 53], [57, 62]) # Bb1 | D3 F3 | A3 D4

# Bar 10 — Gm7  (vi in Bb)
melody(27, 77, 1.0, 0.42)            # F5
melody(28, 74, 1.0, 0.40)            # D5
melody(29, 70, 1.0, 0.40)            # Bb4
alto(27, 67, 3.2, 0.16)
lh_arpeg(27, 43, [58, 62], [65, 70]) # G2 | Bb3 D4 | F4 Bb4

# Bar 11 — Cm7  (ii in Bb)
melody(30, 75, 1.0, 0.42)            # Eb5
melody(31, 74, 1.0, 0.40)            # D5
melody(32, 72, 1.0, 0.40)            # C5
alto(30, 70, 3.2, 0.16)
lh_arpeg(30, 36, [51, 55], [58, 63]) # C2 | Eb3 G3 | Bb3 Eb4

# Bar 12 — F7  (V in Bb / V/V in Eb)
melody(33, 69, 1.0, 0.42)            # A4
melody(34, 77, 1.0, 0.44)            # F5
melody(35, 81, 1.0, 0.46)            # A5 (climbing — top of phrase)
alto(33, 72, 3.2, 0.16)              # C5 inner
lh_arpeg(33, 41, [57, 60], [63, 65]) # F2 | A3 C4 | Eb4 F4

# Bar 13 — Dø7  (D half-dim7: D F Ab C — chromatic, vii°7 of Em or pre-G7)
melody(36, 77, 1.0, 0.42)            # F5
melody(37, 75, 1.0, 0.40)            # Eb5
melody(38, 73, 1.0, 0.40)            # Db5  (chromatic descent, b9 colour)
alto(36, 68, 3.2, 0.18)              # Ab4
lh_arpeg(36, 38, [53, 56], [60, 65]) # D2 | F3 Ab3 | C4 F4

# Bar 14 — G7  (V/vi in Eb — secondary dominant pulling toward Cm)
melody(39, 71, 1.0, 0.42)            # B4 (chromatic — leading tone of Cm!)
melody(40, 74, 1.0, 0.42)            # D5
melody(41, 77, 1.0, 0.44)            # F5  (the b7 of G7 — pulls down to Eb)
alto(39, 67, 3.2, 0.16)              # G4
lh_arpeg(39, 43, [59, 62], [65, 67]) # G2 | B3 D4 | F4 G4

# Bar 15 — Cm7  (vi — the deceptive landing instead of expected resolution)
melody(42, 75, 3.0, 0.44)            # Eb5 dotted-half — sustained sigh
alto(42, 67, 3.2, 0.16)
lh_arpeg(42, 36, [51, 55], [58, 63]) # C2 | Eb3 G3 | Bb3 Eb4

# Bar 16 — Bb7  (V7 in Eb — final preparation for return)
melody(45, 77, 1.0, 0.44)            # F5
melody(46, 75, 1.0, 0.42)            # Eb5
melody(47, 74, 1.0, 0.42)            # D5  (descending — leads into return)
alto(45, 70, 3.2, 0.16)
lh_arpeg(45, 34, [53, 56], [58, 62]) # Bb1 | F3 Ab3 | Bb3 D4


# ════════════════════════════════════════════════════════════════════
# A' SECTION — bars 17-28, return in Eb with extended coda
# ════════════════════════════════════════════════════════════════════

# Bar 17 — Ebmaj7  (RETURN — restate the opening)
melody(48, 79, 3.0, 0.46)            # G5 dotted-half (restatement)
alto(48, 70, 3.2, 0.16)
lh_arpeg(48, 39, [55, 58], [62, 65])

# Bar 18 — Bb7/D
melody(51, 77, 1.0, 0.42)
melody(52, 75, 1.0, 0.40)
melody(53, 74, 1.0, 0.40)
alto(51, 70, 3.2, 0.16)
lh_arpeg(51, 38, [53, 56], [58, 62])

# Bar 19 — Cm7
melody(54, 75, 2.0, 0.42)
melody(56, 74, 1.0, 0.40)
alto(54, 67, 3.2, 0.16)
lh_arpeg(54, 36, [51, 55], [58, 62])

# Bar 20 — Abmaj7
melody(57, 72, 1.0, 0.42)
melody(58, 70, 1.0, 0.40)
melody(59, 68, 1.0, 0.40)
alto(57, 65, 3.2, 0.16)
lh_arpeg(57, 32, [48, 51], [55, 60])

# Bar 21 — Fm9
melody(60, 72, 2.0, 0.42)            # C5 half
melody(62, 70, 1.0, 0.40)            # Bb4
alto(60, 68, 3.2, 0.16)
lh_arpeg(60, 41, [56, 60], [63, 67])

# Bar 22 — Bb7sus4 → Bb7  (V, suspension as before)
melody(63, 75, 1.0, 0.42)
melody(64, 74, 2.0, 0.42)
alto(63, 68, 3.2, 0.16)
n(63, 34, 3.4, 0.40)
n(63, 51, 1.0, 0.16)
n(64, 50, 2.0, 0.16)
n(63, 53, 3.0, 0.14)
n(64, 56, 2.0, 0.14)

# Bar 23 — Cbmaj7  (bVI maj7 — deflection into modal mixture territory)
# Cb Eb Gb Bb. Spelled as MIDI: Cb=B(47/59), Eb=51/63, Gb=54/66, Bb=58/70
melody(66, 70, 1.0, 0.44)            # Bb4
melody(67, 78, 1.0, 0.44)            # Gb5 (the b3 above Eb melody — modal colour)
melody(68, 77, 1.0, 0.42)            # F5
alto(66, 63, 3.2, 0.18)              # Eb4 inner
n(66, 35, 3.4, 0.42)                 # Cb2 bass
n(66, 51, 1.0, 0.16)                 # Eb3
n(67, 54, 2.0, 0.16)                 # Gb3
n(67, 58, 2.0, 0.16)                 # Bb3 (completes Cbmaj7)

# Bar 24 — Ger+6  (Cb Eb Gb A) — the iconic Romantic moment
# Bass holds Cb (common-tone with bar 23). Upper voice introduces A natural,
# which pushes UP to Bb in bar 25; Cb pushes DOWN to Bb. Outward resolution.
melody(69, 73, 1.0, 0.42)            # Db5
melody(70, 72, 1.0, 0.42)            # C5
melody(71, 69, 1.0, 0.48)            # A4 — the augmented 6th, pushes up to Bb!
alto(69, 66, 3.2, 0.18)              # Gb4
n(69, 35, 3.4, 0.42)                 # Cb2 bass (held over from bar 23)
n(69, 51, 1.0, 0.16)                 # Eb3
n(70, 54, 2.0, 0.16)                 # Gb3
n(70, 57, 2.0, 0.18)                 # A3 — completes the German +6

# Bar 25 — Bb7 (V7) — Ger+6 resolves outward to V
melody(72, 70, 3.0, 0.46)            # Bb4 dotted-half — A4 of bar 24 resolves UP
alto(72, 62, 3.2, 0.16)              # D4 (the 3rd of Bb)
lh_arpeg(72, 34, [53, 56], [58, 62]) # Bb1 | F3 Ab3 | Bb3 D4

# Bar 26 — Cadential 6/4 over Bb bass  (I64 — dominant function)
# Bass = Bb (V), upper = G+Bb+Eb (the tonic Eb chord in 2nd inversion)
# This is the classic cadential figure that resolves down to V proper.
melody(75, 75, 1.5, 0.44)            # Eb5 (the 4 above Bb)
melody(76.5, 74, 0.5, 0.36)          # D5 eighth (passing toward bar 27)
melody(77, 75, 1.0, 0.40)            # Eb5 again — the 4 still hovering
alto(75, 70, 3.2, 0.18)              # Bb4 (the 5th — doubles bass)
n(75, 34, 3.4, 0.40)                 # Bb1 bass — V
n(75, 55, 3.0, 0.18)                 # G3 (the 3 of Eb / 6 above Bb)
n(75, 63, 3.0, 0.18)                 # Eb4 (the root of Eb / 4 above Bb)

# Bar 27 — Bb7  (V7 — 6/4 resolves to 5/3, with melody 4-3 suspension)
melody(78, 74, 2.0, 0.44)            # D5 (the Eb of bar 26 finally resolves to D)
melody(80, 73, 1.0, 0.42)            # Db5 (b7 of Bb7, pulls down to C in bar 28)
alto(78, 65, 3.2, 0.16)              # F4 (the 5th of Bb)
n(78, 34, 3.4, 0.40)                 # Bb1 bass
n(78, 50, 3.0, 0.16)                 # D3 (3rd, resolved from Eb)
n(78, 56, 2.0, 0.16)                 # Ab3 (b7 — makes it Bb7 proper)

# Bar 28 — Ebmaj9  (FINAL TONIC — full bloom)
melody(81, 65, 0.4, 0.32)            # F4 grace appoggiatura
melody(81.4, 63, 2.6, 0.48)          # Eb4 — final tonic, sustained
alto(81, 70, 3.4, 0.18)              # Bb4 sustained
n(81, 27, 3.6, 0.42)                 # Eb1 — deep bass
n(81, 39, 3.6, 0.24)                 # Eb2 octave
n(81.5, 55, 3.0, 0.18)               # G3 (3rd) slightly delayed
n(82, 58, 2.4, 0.18)                 # Bb3 (5th)
n(82.5, 65, 2.0, 0.20)               # F4 (9th — last to bloom in)
n(83, 63, 1.6, 0.18)                 # Eb4

# ════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    from sequencer import cli_instrument
    args = cli_instrument()
    render(events, name="minuet_romantic", bpm=BPM, total_beats=84,
           time_sig=(3, 4), instrument=args.instrument, play=args.play)
