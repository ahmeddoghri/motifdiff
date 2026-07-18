# motifdiff

Random notes are not a composition, they are a cat on a keyboard. motifdiff writes an actual MIDI file and then grades itself against exactly that cat.

![CI](https://github.com/ahmeddoghri/motifdiff/actions/workflows/ci.yml/badge.svg)
![python](https://img.shields.io/badge/python-3.9%2B-blue)
![deps](https://img.shields.io/badge/runtime%20deps-none-success)
![license](https://img.shields.io/badge/license-MIT-black)

A lot of "AI music" demos hit shuffle and call it creativity. motifdiff uses a
masked, iterative denoising loop over MIDI pitch tokens, filling in notes
around fixed anchors and nudging everything toward a chord progression, then
scores the result against a random baseline instead of just trusting that it
sounds good because a computer made it.

## Run it

```bash
git clone https://github.com/ahmeddoghri/motifdiff
cd motifdiff
pip install -e ".[dev]"
python -m motifdiff.benchmark
```

The benchmark writes a MIDI file at `artifacts/motifdiff.mid` and a metrics
JSON file next to it, so you can both listen to the evidence and read it.

## Verified benchmark

Generated locally with `python -m motifdiff.benchmark`:

```text
metric             guided   random
scale_adherence      1.00     0.46
motif_reuse          0.07     0.00
tonal_anchor         0.50     0.08
mean_leap            3.90     9.87
```

The guided sequence stays in key 100% of the time against the random
baseline's coin-flip 46%. Mean melodic leap drops from 9.87 semitones to
3.90, which is the difference between a melody and someone falling down a
flight of stairs onto a piano.

## What gets measured

- Scale adherence, so the notes belong to the key instead of just near it.
- Motif reuse, so the piece remembers what it already said.
- Tonal anchor, so downbeats land on chord tones instead of wherever.
- Mean melodic leap, so the contour stays singable by an actual human throat.

## Research trail

- Generating symbolic music from natural language prompts, 2024: https://arxiv.org/abs/2410.02084
- MidiCaps and symbolic music captions, 2024: https://arxiv.org/abs/2406.02255
- GraphMuse symbolic music graph processing, 2024: https://arxiv.org/abs/2407.12671
- Hierarchical symbolic pop music generation, 2024: https://arxiv.org/abs/2409.08155

## Tests

```bash
pytest -q
ruff check .
```

MIT © Ahmed Doghri
