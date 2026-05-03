# claude-chords

Per-session piano-chord audio cues for Claude Code. Each tab gets a unique chord; a glance — er, listen — tells you which tab needs you.

Built for [Claude Code](https://claude.com/claude-code) on macOS. Pure Python (numpy + stdlib `wave`), no soundfont/synth dependencies. Audio plays via the built-in `afplay`.

## How it sounds

Each session is assigned a chord (a triad by default, or a 2-note dyad). Three events make sound:

| Event | Variant |
|---|---|
| `UserPromptSubmit` (you press enter) | arpeggio up |
| `Stop` (Claude finishes a turn) | block chord (all notes at once) |
| `Notification` (Claude needs input) | arpeggio down |

Same chord across all three events → same harmonic identity, distinguishable contour.

## Install

```
git clone https://github.com/sliss/claude-chords.git
cd claude-chords
python3 install.py
```

Requirements: macOS, Python 3.9+, `numpy` (`pip install numpy`).

The installer:
- renders `skill/SKILL.md.tmpl` to `~/.claude/skills/tone/SKILL.md` with this directory's path baked in
- backs up `~/.claude/settings.json` to `settings.json.bak.<timestamp>`
- adds a `SessionStart` hook (records each session's PID so `/tone` can identify "this session")
- replaces the audio hooks with a dispatcher
- if your previous hooks contained `afplay <path.wav>`, seeds `state/fallbacks.json` from those paths so unassigned sessions still get your prior default sounds (otherwise it falls back to system sounds: `Pop.aiff`, `Hero.aiff`, `Glass.aiff`)

Restart any open Claude Code sessions so the `SessionStart` hook can register them. Then `/tone` in any tab to assign a chord.

## Use

In any session, run `/tone` (or paste:

```
/tone
```

```
/tone P4        # perfect-fourth dyad, auto-pick free root
/tone M6        # major-sixth dyad
/tone min       # any free minor triad
/tone Cmaj      # specific triad
/tone F#dim     # specific triad
/tone off       # clear; revert to default sounds
/tone list      # show all current assignments
```

## Uninstall

```
python3 install.py --uninstall
```

Restores the most recent settings backup and removes the skill symlink. (Cached audio under `state/cache/` and the registry under `state/registry.json` stay; delete the project dir to fully clean up.)

## Compositions

`compositions/` contains short pieces I composed by hand (well, by Claude) using the same synth. Each script defines an event list and calls `sequencer.render()`, which writes both:

- `compositions/output/<name>.wav` — preview audio (gitignored; regenerate with `python3 compositions/<name>.py`)
- `compositions/output/<name>.mid` — Standard MIDI File you can drag into any DAW

Currently three minuet variations:

| File | Era | Notes |
|---|---|---|
| `minuet_classical.py` | Classical | G major, simple I-V-I-vi-V7-I, oompah-pah LH |
| `minuet_baroque.py` | Baroque | G major, walking bass, trills + mordents + appoggiaturas, V/V at the half cadence, 4-3 suspension |
| `minuet_romantic.py` | Romantic | Eb major, Chopin-ish broken-chord LH, maj7/9 chords throughout, German augmented 6th at bar 10 |

Run any of them: `python3 compositions/minuet_baroque.py`. Output goes to `compositions/output/`.

## How it works

- `bin/synth.py` — additive synthesis, mildly inharmonic, with an attack click. Renders mono 16-bit WAV.
- `bin/midi.py` — Standard MIDI File writer (Type 0, stdlib-only, no `mido` dep).
- `bin/sequencer.py` — event-list runtime: takes `(start_beat, midi_note, dur_beats, gain)` tuples and produces both `.wav` and `.mid`.
- `bin/chords.py` — interval/triad vocabulary and auto-pick (avoids labels already in the registry).
- `bin/registry.py` — JSON-on-disk registry, content-addressed audio cache.
- `bin/register_session.py` — `SessionStart` hook. Writes `session_id` to `state/sessions/<claude_pid>`.
- `bin/find_session.py` — walks ancestor PIDs to discover the current session_id (used by `/tone`).
- `bin/play_event.py` — hook dispatcher. Reads `session_id` from stdin JSON, plays the cached chord variant, falls back to existing wav if no assignment.
- `bin/assign_chord.py` — `/tone` backend. Parses arg, picks/builds chord, renders all 3 variants, updates registry.
- `skill/SKILL.md` — instructs Claude how to invoke `assign_chord.py`.
