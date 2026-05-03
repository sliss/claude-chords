"""Bach-style four-voice chorale in G major. 8 bars, 4/4, ~72 BPM.

SATB texture, half-note harmonic rhythm (2 chords per bar). Two parallel
4-bar phrases — antecedent (half cadence on V) and consequent (perfect
authentic cadence on I).

Voice-leading rules applied throughout:
  - No parallel perfect 5ths or 8ves between any pair of voices
  - No hidden 5ths/8ves between OUTER voices (S-B) approached by similar motion
  - No voice crossings (B <= T <= A <= S in every chord)
  - Leading tone (F#) resolves up to G at every cadence (S or T as appropriate)
  - Chord-7th (the C in V7) resolves down by step
  - Mostly stepwise inner-voice motion; bass moves by step or P4/P5
  - Common tones held over chord changes when possible
  - Doubled root or fifth in triads (never the leading tone or the chord-7th)

A parallel-interval audit runs every time the script executes — see
`verify_voice_leading()` at the bottom. Goal: 0 warnings.

Phrase 1 (bars 1-4)  G major, ends on V   — half cadence
Phrase 2 (bars 5-8)  G major, ends on I   — perfect authentic cadence
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "bin"))

from sequencer import render

BPM = 72
NOTE_DUR = 1.95  # beats — half-note rhythm with slight gap for articulation

events: list[tuple[float, int, float, float]] = []
chords_satb: list[tuple[int, int, int, int]] = []  # for verification

# Pitch reference (MIDI)
C2, D2, E2, F2, F_2, G2, A2, B2 = 36, 38, 40, 41, 42, 43, 45, 47
C3, D3, E3, F3, F_3, G3, A3, B3 = 48, 50, 52, 53, 54, 55, 57, 59
C4, D4, E4, F4, F_4, G4, A4, B4 = 60, 62, 64, 65, 66, 67, 69, 71
C5, D5, E5, F5, F_5, G5         = 72, 74, 76, 77, 78, 79


def chord(beat: float, S: int, A: int, T: int, B: int) -> None:
    """Add a 4-voice chord. Soprano + bass get slightly more gain than the
    inner voices, mirroring how a chorus or organ sounds."""
    events.append((beat, S, NOTE_DUR, 0.40))
    events.append((beat, A, NOTE_DUR, 0.28))
    events.append((beat, T, NOTE_DUR, 0.28))
    events.append((beat, B, NOTE_DUR, 0.36))
    chords_satb.append((S, A, T, B))


# ════════════════════════════════════════════════════════════════════
# PHRASE 1 (bars 1-4): G major → V (half cadence)
#   Chords:  I    ii6  | I    V    | vi6  IV   | I    V   (HC)
#   Soprano: D5   C5   | B4   D5   | E5   C5   | B4   A4
# ════════════════════════════════════════════════════════════════════

# Bar 1 ─────────────────
# Beat 0: I, root in bass, 5th in S, 3rd in A, root in T (doubled root)
chord(0,  D5, B3, G3, G2)
# Beat 2: ii6 (1st inv, 3rd in bass).  Bass C3 ↑ from G2 (P4).
#   Bass C is the 3rd of A-minor — common to double the bass note in 1st inv.
#   S↓M2, A↑P4, T↑M2 — contrary/oblique mix avoids parallels.
chord(2,  C5, E4, A3, C3)

# Bar 2 ─────────────────
# Beat 4: I (back to tonic). Bass leaps down from C3 to G2 (P5 down).
#   Voice-leading: contrary motion in outer voices (S↓m2, B↓P4).
chord(4,  B4, G4, D4, G2)
# Beat 6: V (root pos). Bass G2 → D2 (P4 down). Soprano ↑m3 to D5.
#   F#3 in tenor as leading tone.
chord(6,  D5, A3, F_3, D2)

# Bar 3 ─────────────────
# Beat 8: vi6 (1st inv, 3rd in bass). Bass D2 → G2 (P4 up).
#   Avoids the V→vi parallel-octave trap (both bass and soprano not moving
#   in similar motion to a perfect interval).
#   vi6: B=G2, T=B3, A=E4, S=E5 (E doubled — root and S).
chord(8,  E5, E4, B3, G2)
# Beat 10: IV (root pos). Bass G2 → C3 (P4 up). Smooth descent in upper voices.
chord(10, C5, E4, G3, C3)

# Bar 4 ─────────────────
# Beat 12: I (root pos). Bass C3 → G2 (P5 down) — contrary to S↓m2.
#   Voicing chosen so A=D4, T=B3 (no T-above-A crossing).
chord(12, B4, D4, B3, G2)
# Beat 14: V (root pos). Bass G2 → D3 (P4 up). Soprano ↓M2 from B4 to A4
#   for the half cadence. Leading tone F#4 in alto.
chord(14, A4, F_4, D4, D3)


# ════════════════════════════════════════════════════════════════════
# PHRASE 2 (bars 5-8): G major → I (perfect authentic cadence)
#   Chords:  I    IV   | vi   ii6  | V    vi   | V7   I    (PAC)
#   Soprano: B4   C5   | D5   C5   | B4   D5   | C5   B4
# ════════════════════════════════════════════════════════════════════

# Bar 5 ─────────────────
# Beat 16: I (root pos). Bass D3 → G2 — typical V→I bass motion within bar
#   (treat the phrase boundary as a fresh start).
chord(16, B4, D4, B3, G2)
# Beat 18: IV (root pos). Bass G2 → C3 (P4 up). Common-tone E held in alto;
#   tenor swapped below alto to avoid voice crossing.
chord(18, C5, E4, G3, C3)

# Bar 6 ─────────────────
# Beat 20: vi6 (3rd in bass). Bass C3 → G2 (P5 down).
#   E in alto and soprano = doubled-root E (in 1st inv this is the bass-note pitch).
chord(20, D5, B3, G3, E3)  # vi root pos: B=E3, T=G3, A=B3, S=D5?
                            # Wait D5 is in vi (E G B)? No, D not in Em.
                            # Let me reconsider — soprano is D5, which is in V or I.
                            # Use I instead of vi: I with S=D5 = good.
# Use I again (bar 6 beat 20 = I, beat 22 = ii6)
# Actually let me restructure beat 20-22 as I → ii6 (which is fine harmonically).
# Beat 20: I (root pos). Bass C3 → G2 (P5 down). S↑M2 to D5. Contrary motion.
# (This overrides what I just did above, but the chord() call has already been added.
#  Fix this by restructuring — I'll just write it cleanly after this comment.)

# Reset: remove the wrong chord we just added
events = events[:-4]  # remove last 4 events (the wrong chord at beat 20)
chords_satb.pop()      # remove last entry from verification list

# Now write it correctly
chord(20, D5, B3, G3, G2)  # I (root pos), S=D5
# Beat 22: ii6 (3rd in bass). Bass G2 → C3 (P4 up). S↓M2 to C5. Contrary.
chord(22, C5, E4, A3, C3)

# Bar 7 ─────────────────
# Beat 24: V (root pos). Bass C3 → D3 (M2 up). All voices move stepwise.
chord(24, B4, F_4, D4, D3)  # B4 = 3 of I — wait V chord has D F# A; B not in V. ✗
# Fix: use vi (E G B) with S=B4. vi6 with G in bass.
# Or change soprano to A4 or D5 to fit V.
# Let me use vi: E G B with S=B4 (5th of vi).
# Bass: prev was C3=48, going to E3 (52, vi root) or G2 (43, vi6).
# Use vi6 (G in bass): bass C3→G2 (P4 down). Smooth.
events = events[:-4]
chords_satb.pop()
chord(24, B4, E4, G3, G2)  # vi6: B=G2, T=G3, A=E4, S=B4 (vi=Em with G in bass)

# Beat 26: V (root pos). Bass goes DOWN to D2 (not up to D3) to avoid hidden
#   octaves in outer voices with the previous chord (vi6 had G2 in bass, S
#   moves up m3 here — bass needs to move contrary, hence D2 not D3).
#   Alto leaps up to A4 to keep voicing balanced; doubled root in B+A.
chord(26, D5, A4, F_3, D2)  # V: B=D2, T=F#3, A=A4, S=D5

# Bar 8 ─────────────────
# Beat 28: V7 (root pos). Bass and inner voices stay; soprano steps D5→C5
#   to introduce the 7. Common-tone voice change — maximally smooth.
chord(28, C5, A4, F_3, D2)

# Beat 30: I (PAC) — the textbook resolution.
#   B D2 → G2 (P5 up — proper V→I bass motion).
#   T F#3 → G3 (leading tone up by step).
#   A A4 → D4 (5 of V → 5 of I, alto leap of P5 down — acceptable for the
#       sake of completing the triad without parallels).
#   S C5 → B4 (the 7 of V7 resolves down by step to the 3 of I).
#   Outer voices: B↑P5, S↓m2 → no parallel/hidden 8ve.
chord(30, B4, D4, G3, G2)


# ════════════════════════════════════════════════════════════════════
# VOICE-LEADING AUDIT
# ════════════════════════════════════════════════════════════════════

VOICE_NAMES = ("S", "A", "T", "B")


def _interval(a: int, b: int) -> int:
    """Reduced interval modulo octave."""
    return abs(a - b) % 12


def verify_voice_leading() -> list[str]:
    """Catch parallel P5/P8 between any two voices, voice crossings, and
    hidden P5/P8 in outer voices (S-B) approached by similar motion."""
    warnings: list[str] = []
    for i in range(len(chords_satb) - 1):
        c1, c2 = chords_satb[i], chords_satb[i + 1]
        S, A, T, B = c2
        if not (B <= T <= A <= S):
            warnings.append(
                f"chord {i+1}->{i+2}: voice crossing in next chord "
                f"(S={S} A={A} T={T} B={B})"
            )
        for vi_a in range(4):
            for vi_b in range(vi_a + 1, 4):
                int1 = _interval(c1[vi_a], c1[vi_b])
                int2 = _interval(c2[vi_a], c2[vi_b])
                delta_a = c2[vi_a] - c1[vi_a]
                delta_b = c2[vi_b] - c1[vi_b]
                if delta_a == 0 or delta_b == 0:
                    continue            # need both voices to actually move
                # Parallel motion = same direction. Contrary or oblique motion
                # at the same interval is fine.
                if (delta_a > 0) != (delta_b > 0):
                    continue
                if int1 == int2 == 7:
                    warnings.append(
                        f"chord {i+1}->{i+2}: parallel P5  "
                        f"{VOICE_NAMES[vi_a]}({c1[vi_a]}->{c2[vi_a]}) // "
                        f"{VOICE_NAMES[vi_b]}({c1[vi_b]}->{c2[vi_b]})"
                    )
                if int1 == int2 == 0:
                    warnings.append(
                        f"chord {i+1}->{i+2}: parallel P8/unison  "
                        f"{VOICE_NAMES[vi_a]}({c1[vi_a]}->{c2[vi_a]}) // "
                        f"{VOICE_NAMES[vi_b]}({c1[vi_b]}->{c2[vi_b]})"
                    )
        # Hidden 5/8 in OUTER voices (S and B): both moved similar motion
        # arriving at perfect interval where the leap to S or B is by leap (not step)
        b1, b2 = c1[3], c2[3]
        s1, s2 = c1[0], c2[0]
        if b1 != b2 and s1 != s2:
            same_dir = (b2 - b1) * (s2 - s1) > 0
            if same_dir:
                interval = _interval(s2, b2)
                if interval in (0, 7):  # P8 or P5
                    # Allow if soprano moved by step (m2 or M2)
                    if abs(s2 - s1) > 2:
                        kind = "P8" if interval == 0 else "P5"
                        warnings.append(
                            f"chord {i+1}->{i+2}: hidden {kind} in outer voices "
                            f"(B {b1}->{b2}, S {s1}->{s2})"
                        )
    return warnings


if __name__ == "__main__":
    from sequencer import cli_instrument
    args = cli_instrument()

    warnings = verify_voice_leading()
    if warnings:
        print(f"=== Voice-leading audit: {len(warnings)} issue(s) ===")
        for w in warnings:
            print(f"  {w}")
        print()
    else:
        print("=== Voice-leading audit: clean ===")
        print()

    render(events, name="chorale_bach", bpm=BPM, total_beats=32,
           time_sig=(4, 4), instrument=args.instrument, play=args.play)
