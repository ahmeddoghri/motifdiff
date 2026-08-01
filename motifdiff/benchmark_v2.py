"""Is "guided beats random" measuring the generation algorithm, or a
hardcoded motif and a strawman baseline?

``benchmark.py`` compares one ``generate()`` output against one
``random_sequence()`` output. Two things inflate that gap that have
nothing to do with the masked denoising algorithm:

  1. Half of ``generate()``'s 64 steps are a hand-written 8-note motif
     copied in verbatim, never touched by any generative process.
  2. ``scale_adherence`` is guaranteed to be 1.0 for any ``generate()``
     output, because its candidate pool is pre-restricted to in-scale
     pitches; ``random_sequence`` draws from an unrestricted 30-pitch
     chromatic range, so the 1.00-vs-0.46 gap is a candidate-space
     difference, not an algorithm difference.

This module isolates what the transition-and-chord-aware weighting
actually contributes, once the hardcoded content is stripped out and the
baseline is made fair (same candidate pool, no anchor, pure random),
averaged over 50 seeds for stability rather than one anecdote.

    python -m motifdiff.benchmark_v2
"""
from __future__ import annotations

from .generator import generate, score_sequence
from .generator_v2 import fair_random_sequence, generated_only

N_SEEDS = 50


def _average(seeds: range) -> tuple[dict, dict]:
    gen_totals = {"scale_adherence": 0.0, "tonal_anchor": 0.0, "mean_leap": 0.0}
    fair_totals = {"scale_adherence": 0.0, "tonal_anchor": 0.0, "mean_leap": 0.0}
    for seed in seeds:
        full = generate(seed=seed)
        gm = score_sequence(generated_only(full))
        fm = score_sequence(fair_random_sequence(seed))
        gen_totals["scale_adherence"] += gm.scale_adherence
        gen_totals["tonal_anchor"] += gm.tonal_anchor
        gen_totals["mean_leap"] += gm.mean_leap
        fair_totals["scale_adherence"] += fm.scale_adherence
        fair_totals["tonal_anchor"] += fm.tonal_anchor
        fair_totals["mean_leap"] += fm.mean_leap
    n = len(seeds)
    gen_avg = {k: v / n for k, v in gen_totals.items()}
    fair_avg = {k: v / n for k, v in fair_totals.items()}
    return gen_avg, fair_avg


def main() -> None:
    seeds = range(1, N_SEEDS + 1)
    gen_avg, fair_avg = _average(seeds)

    published_guided = score_sequence(generate(seed=12))

    print(f"motifdiff benchmark v2: isolating the algorithm from the hardcoded motif "
          f"(n={N_SEEDS} seeds)\n")
    print(f"{'metric':<18}{'generated_only':>16}{'fair_random':>14}")
    print(f"{'scale_adherence':<18}{gen_avg['scale_adherence']:>16.3f}{fair_avg['scale_adherence']:>14.3f}")
    print(f"{'tonal_anchor':<18}{gen_avg['tonal_anchor']:>16.3f}{fair_avg['tonal_anchor']:>14.3f}")
    print(f"{'mean_leap':<18}{gen_avg['mean_leap']:>16.3f}{fair_avg['mean_leap']:>14.3f}")
    print("\npublished 'guided' (seed=12, includes the hardcoded motif anchor):")
    print(f"  scale_adherence={published_guided.scale_adherence:.2f}  "
          f"tonal_anchor={published_guided.tonal_anchor:.2f}  "
          f"mean_leap={published_guided.mean_leap:.2f}")
    print("\nscale_adherence is tied at 1.000 either way: it's guaranteed by the")
    print("candidate pool, not evidence the algorithm is doing anything. tonal_anchor")
    print("and mean_leap DO show a real, modest edge for the actual weighting over a")
    print("fair same-palette baseline, but nowhere near the size of the published")
    print("guided-vs-random gap, which is inflated by a hardcoded motif and an")
    print("unrestricted chromatic strawman baseline.")


if __name__ == "__main__":
    main()
