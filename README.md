# motifdiff

A tiny symbolic music generator with an actual listenable artifact. It uses a
masked, iterative denoising loop over MIDI pitch tokens, then scores the result
against a random baseline instead of shrugging and calling random notes music.

![CI](https://github.com/ahmeddoghri/motifdiff/actions/workflows/ci.yml/badge.svg)
![python](https://img.shields.io/badge/python-3.9%2B-blue)
![deps](https://img.shields.io/badge/runtime%20deps-none-success)
![license](https://img.shields.io/badge/license-MIT-black)

## Run it

```bash
git clone https://github.com/ahmeddoghri/motifdiff
cd motifdiff
pip install -e ".[dev]"
python -m motifdiff.benchmark
```

The benchmark writes a MIDI file at `artifacts/motifdiff.mid` and a metrics
JSON file next to it.

## Verified benchmark

These numbers were generated locally with `python -m motifdiff.benchmark`:

```text
metric             guided   random
scale_adherence      1.00     0.46
motif_reuse          0.07     0.00
tonal_anchor         0.50     0.08
mean_leap            3.90     9.87
```

## What gets measured

- Scale adherence, so the notes belong to the key.
- Motif reuse, so the piece has memory instead of wandering.
- Tonal anchor, so downbeats land on chord tones.
- Mean melodic leap, so the contour stays singable.

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
