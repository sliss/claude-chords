"""Chord/interval vocabulary and auto-assignment logic."""
from __future__ import annotations

from dataclasses import dataclass

# Semitones above root for each named interval. Both common spellings supported.
INTERVALS: dict[str, int] = {
    "P1": 0, "U": 0,
    "m2": 1,
    "M2": 2,
    "m3": 3,
    "M3": 4,
    "P4": 5,
    "TT": 6, "A4": 6, "d5": 6,
    "P5": 7,
    "m6": 8,
    "M6": 9,
    "m7": 10,
    "M7": 11,
    "P8": 12,
}

# Triads + tetrads. Key = canonical quality name. Value = (semitones above root...).
QUALITIES: dict[str, tuple[int, ...]] = {
    # Triads
    "maj":   (0, 4, 7),
    "min":   (0, 3, 7),
    "dim":   (0, 3, 6),
    "aug":   (0, 4, 8),
    "sus2":  (0, 2, 7),
    "sus4":  (0, 5, 7),
    # Tetrads (7th chords)
    "maj7":  (0, 4, 7, 11),
    "m7":    (0, 3, 7, 10),
    "7":     (0, 4, 7, 10),    # dominant 7
    "dim7":  (0, 3, 6, 9),
    "m7b5":  (0, 3, 6, 10),    # half-diminished
    "mMaj7": (0, 3, 7, 11),
    "aug7":  (0, 4, 8, 10),
    # 6th chords
    "6":     (0, 4, 7, 9),
    "m6":    (0, 3, 7, 9),
}

# Suffix -> canonical quality. Exact-case match (so "M7" is maj7, "m7" is min7).
# Order doesn't affect correctness (we match by equality), only readability.
SUFFIX_TABLE: list[tuple[str, str]] = [
    # Empty = bare root = major triad
    ("",        "maj"),
    # Major triad spellings
    ("maj",     "maj"), ("major",  "maj"), ("M",      "maj"),
    # Minor triad
    ("m",       "min"), ("min",    "min"), ("minor",  "min"), ("-",      "min"),
    # Diminished / augmented triads
    ("dim",     "dim"), ("o",      "dim"), ("°", "dim"),  # ° = U+00B0
    ("aug",     "aug"), ("+",      "aug"),
    # Suspended
    ("sus2",    "sus2"),
    ("sus4",    "sus4"), ("sus",   "sus4"),
    # Major 7
    ("maj7",    "maj7"), ("M7",    "maj7"), ("major7", "maj7"),
    ("Δ7", "maj7"), ("Δ","maj7"),  # Δ7, Δ
    # Minor 7
    ("m7",      "m7"), ("min7",  "m7"), ("-7", "m7"),
    # Dominant 7
    ("7",       "7"), ("dom7", "7"),
    # Diminished 7
    ("dim7",    "dim7"), ("o7",  "dim7"), ("°7", "dim7"),
    # Half-diminished
    ("m7b5",    "m7b5"), ("ø7", "m7b5"), ("ø", "m7b5"),  # ø7, ø
    # Minor-major 7
    ("mMaj7",   "mMaj7"), ("mM7", "mMaj7"), ("minMaj7", "mMaj7"),
    # Augmented 7
    ("aug7",    "aug7"), ("+7",  "aug7"), ("7#5",     "aug7"),
    # 6th
    ("6",       "6"),
    ("m6",      "m6"), ("min6", "m6"),
]

# How to render the quality in a chord label (after the root letter).
QUALITY_LABEL: dict[str, str] = {
    "maj":   "maj",
    "min":   "min",
    "dim":   "dim",
    "aug":   "aug",
    "sus2":  "sus2",
    "sus4":  "sus4",
    "maj7":  "maj7",
    "m7":    "m7",
    "7":     "7",
    "dim7":  "dim7",
    "m7b5":  "m7b5",
    "mMaj7": "mMaj7",
    "aug7":  "aug7",
    "6":     "6",
    "m6":    "m6",
}

PITCH_CLASS: dict[str, int] = {
    "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "Fb": 4,
    "E#": 5, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8,
    "A": 9, "A#": 10, "Bb": 10, "B": 11, "Cb": 11,
}

PC_NAME = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


@dataclass
class Chord:
    notes: list[int]
    label: str
    kind: str           # "dyad" | "triad" | "tetrad"

    def to_dict(self) -> dict:
        return {"notes": self.notes, "label": self.label, "kind": self.kind}


def midi_root_in_octave(pc: int, target_midi: int = 60) -> int:
    base = (target_midi // 12) * 12 + pc
    return min([base - 12, base, base + 12], key=lambda m: abs(m - target_midi))


def parse_root_quality(s: str) -> tuple[str, int, str] | None:
    """Parse 'Cmaj', 'F#m7', 'Bbdim7' -> (root_spelling, pitch_class, quality).

    Returns the user's chosen root spelling (e.g. 'Bb') along with its pitch
    class so labels can honor the original spelling rather than canonicalizing
    to sharps.
    """
    s = s.strip()
    if not s:
        return None
    for root_len in (2, 1):
        if len(s) < root_len:
            continue
        root = s[:root_len]
        if root not in PITCH_CLASS:
            continue
        rest = s[root_len:]
        for suffix, quality in SUFFIX_TABLE:
            if rest == suffix:
                return root, PITCH_CLASS[root], quality
    return None


def parse_bare_quality(s: str) -> str | None:
    """Parse a bare quality argument like 'maj7', 'm', 'dim7' -> canonical quality.
    Returns None if `s` doesn't unambiguously name a quality (notably the empty
    string, which means 'no arg' rather than 'major')."""
    s = s.strip()
    if not s:
        return None
    for suffix, quality in SUFFIX_TABLE:
        if suffix and s == suffix:
            return quality
    return None


def kind_of(quality: str) -> str:
    n = len(QUALITIES[quality])
    return {3: "triad", 4: "tetrad"}.get(n, "chord")


def build_chord(root_pc: int, quality: str, root_name: str | None = None) -> Chord:
    intervals = QUALITIES[quality]
    root = midi_root_in_octave(root_pc, target_midi=60)
    notes = [root + i for i in intervals]
    name = root_name if root_name is not None else PC_NAME[root_pc]
    label = f"{name}{QUALITY_LABEL[quality]}"
    return Chord(notes=notes, label=label, kind=kind_of(quality))


def build_dyad(root_pc: int, interval: str, root_name: str | None = None) -> Chord:
    semis = INTERVALS[interval]
    root = midi_root_in_octave(root_pc, target_midi=60)
    notes = [root, root + semis]
    name = root_name if root_name is not None else PC_NAME[root_pc]
    label = f"{name} + {interval}"
    return Chord(notes=notes, label=label, kind="dyad")


# Default rotation when no quality requested: pleasant variety of triads.
DEFAULT_ROTATION: list[tuple[int, str]] = [
    (0, "maj"), (9, "min"), (5, "maj"), (2, "min"),
    (7, "maj"), (4, "min"), (10, "maj"), (11, "dim"),
    (3, "maj"), (8, "min"), (1, "maj"), (6, "min"),
    (0, "min"), (5, "min"), (7, "min"), (2, "maj"),
    (4, "maj"), (9, "maj"),
]


def auto_pick_chord(used_labels: set[str], quality: str | None = None) -> Chord:
    """Pick an unused chord. With `quality=None`, uses DEFAULT_ROTATION (varied
    triads). With a specific quality, rotates through roots chromatically
    starting from a circle-of-fifths-ish order for variety."""
    if quality is None:
        rotation = DEFAULT_ROTATION
    else:
        order = [0, 7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5]
        rotation = [(pc, quality) for pc in order]
    for pc, q in rotation:
        chord = build_chord(pc, q)
        if chord.label not in used_labels:
            return chord
    # All taken: fall back to first entry.
    pc, q = rotation[0]
    return build_chord(pc, q)


def auto_pick_dyad(used_labels: set[str], interval: str) -> Chord:
    order = [0, 7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5]
    for pc in order:
        chord = build_dyad(pc, interval)
        if chord.label not in used_labels:
            return chord
    return build_dyad(0, interval)
