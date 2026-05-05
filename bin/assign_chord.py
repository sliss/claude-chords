"""/tone skill backend: assign a chord to the current session."""
from __future__ import annotations

import argparse
import sys

from chords import (
    Chord,
    INTERVALS,
    PC_NAME,
    QUALITIES,
    auto_pick_chord,
    auto_pick_dyad,
    build_chord,
    parse_bare_quality,
    parse_root_quality,
)
from find_session import find_session_id
from registry import (
    cache_path,
    ensure_dirs,
    load_registry,
    save_registry,
)
from synth import (
    INSTRUMENTS,
    render_arpeggio,
    render_block_chord,
    write_wav,
)


def render_variants(notes: list[int], instrument: str = "piano") -> None:
    """Render block, arp_up, arp_down WAVs for these notes if not cached."""
    for variant in ("block", "arp_up", "arp_down"):
        path = cache_path(notes, variant, instrument)
        if path.exists():
            continue
        if variant == "block":
            sig = render_block_chord(notes, instrument=instrument)
        elif variant == "arp_up":
            sig = render_arpeggio(notes, direction="up", instrument=instrument)
        else:
            sig = render_arpeggio(notes, direction="down", instrument=instrument)
        write_wav(path, sig)


def midi_label(notes: list[int]) -> str:
    return " ".join(f"{PC_NAME[n % 12]}{(n // 12) - 1}" for n in notes)


def cmd_list(reg: dict) -> str:
    if not reg:
        return "No chord assignments yet."
    lines = ["Current chord assignments:"]
    for sid, entry in reg.items():
        if "label" not in entry:
            continue
        sid_short = sid[:8]
        instr = entry.get("instrument", "piano")
        lines.append(f"  {sid_short}  {entry['label']:<14} [{midi_label(entry['notes'])}]  ({instr})")
    return "\n".join(lines)


def cmd_off(reg: dict, sid: str) -> tuple[dict, str]:
    if sid in reg:
        prev = reg.pop(sid)
        return reg, f"Cleared chord assignment ({prev['label']}) for this session."
    return reg, "No chord was assigned for this session."


def parse_arg(arg: str):
    s = arg.strip()
    if not s:
        return ("auto-default", None)
    rq = parse_root_quality(s)
    if rq is not None:
        root_name, pc, quality = rq
        return build_chord(pc, quality, root_name=root_name)
    if s in INTERVALS:
        return ("auto-dyad", s)
    bare = parse_bare_quality(s)
    if bare is not None:
        return ("auto-quality", bare)
    raise ValueError(f"Could not parse chord spec: {s!r}")


def usage_msg() -> str:
    qualities = " ".join(sorted(QUALITIES.keys()))
    intervals = " ".join(INTERVALS.keys())
    instruments = " ".join(INSTRUMENTS.keys())
    return (
        f"Valid arguments:\n"
        f"  (empty)              auto-pick free triad\n"
        f"  <quality>            auto-pick of that quality (e.g. maj7, m7, 7, dim7)\n"
        f"  <interval>           auto-pick dyad (e.g. P4, M6, m3, P5)\n"
        f"  <Root><quality>      specific chord (e.g. Cmaj7, F#m, Bbdim7, Esus4)\n"
        f"  off | clear          remove assignment for this session\n"
        f"  list                 show all current assignments\n"
        f"\n"
        f"Optional flag:\n"
        f"  --instrument <name>  one of: {instruments}\n"
        f"\n"
        f"Known qualities: {qualities}\n"
        f"Known intervals: {intervals}"
    )


def main() -> int:
    ensure_dirs()

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--instrument", "-i", default="piano")
    parser.add_argument("chord", nargs="*", default=[])
    args = parser.parse_args()

    arg = " ".join(args.chord).strip()
    instrument = args.instrument

    if instrument not in INSTRUMENTS:
        print(f"ERROR: unknown instrument {instrument!r}. "
              f"Known: {', '.join(INSTRUMENTS.keys())}", file=sys.stderr)
        return 2

    reg = load_registry()

    if arg == "list":
        print(cmd_list(reg))
        return 0

    sid = find_session_id()
    if not sid:
        print("ERROR: could not resolve current session_id (is the SessionStart "
              "hook installed? Try restarting the Claude session).", file=sys.stderr)
        return 2

    if arg in ("off", "clear", "none"):
        reg, msg = cmd_off(reg, sid)
        save_registry(reg)
        print(msg)
        return 0

    try:
        parsed = parse_arg(arg)
    except ValueError as e:
        print(f"ERROR: {e}\n\n{usage_msg()}", file=sys.stderr)
        return 2

    used_labels = {e["label"] for s, e in reg.items() if s != sid and "label" in e}

    if isinstance(parsed, Chord):
        chord = parsed
        if chord.label in used_labels:
            print(f"NOTE: '{chord.label}' is already assigned to another session, "
                  f"but you asked for it specifically — using it anyway.")
    else:
        kind, spec = parsed
        if kind == "auto-default":
            chord = auto_pick_chord(used_labels)
        elif kind == "auto-quality":
            chord = auto_pick_chord(used_labels, quality=spec)
        elif kind == "auto-dyad":
            chord = auto_pick_dyad(used_labels, interval=spec)
        else:
            print(f"ERROR: unexpected parse result {kind}", file=sys.stderr)
            return 2

    render_variants(chord.notes, instrument=instrument)

    entry = chord.to_dict()
    entry["instrument"] = instrument
    reg[sid] = entry
    save_registry(reg)

    print(f"Assigned: {chord.label}  ({chord.kind}, {instrument}, "
          f"notes: {midi_label(chord.notes)})")
    print(f"  Stop -> block chord  |  UserPromptSubmit -> arpeggio up  |  "
          f"Notification -> arpeggio down")
    return 0


if __name__ == "__main__":
    sys.exit(main())
