"""How much of "guided beats random" is the generation algorithm, and how
much is two things that have nothing to do with it?

``generate()`` writes a hand-composed 8-note motif directly into the
sequence at four fixed offsets (transposed by 0 or +5 semitones), and only
fills the *remaining* half of the 64 steps with the stochastic,
transition-and-chord-weighted denoising step. Concretely: of 64 steps, 32
are copied verbatim from ``motif = [60, 62, 64, 67, REST, 64, 62, 60]``,
never touched by any generative process at all.

Separately, ``score_sequence``'s ``scale_adherence`` metric checks whether
each note's pitch class is in C major. ``generate()``'s candidate pool
(``[REST, 60, 62, 64, 65, 67, 69, 71, 72, 74]``) is *already* restricted to
exactly those pitch classes, so scale_adherence is guaranteed to be 1.0 for
any output the generator could possibly produce, by construction, with zero
credit due to the transition weights or chord scoring. Comparing that
against ``random_sequence`` (uniform over 30 chromatic pitches across two
and a half octaves, no restriction at all) makes the 1.00-vs-0.46 headline
almost entirely a candidate-space difference, not an algorithm difference.

``fair_random_sequence`` draws uniformly from the *same* restricted
candidate pool ``generate()`` uses, with no motif anchor and no weighting
at all, the correct apples-to-apples baseline. ``generated_only`` strips
the hand-written anchor out of a ``generate()`` output entirely, crediting
the algorithm only for the steps it actually produced. Comparing those two
head to head, averaged over 50 seeds for stability, isolates what the
transition-and-chord-aware weighting actually contributes once the
hardcoded content and the strawman baseline are both removed: a real,
modest, positive effect on tonal_anchor and mean_leap, nowhere near the
size of the published headline gap.
"""
from __future__ import annotations

import random

from .generator import REST, generate

CANDIDATES = [REST, 60, 62, 64, 65, 67, 69, 71, 72, 74]

# Mirrors generate()'s internal anchoring exactly: an 8-note motif is
# written verbatim at every 16-step block offset. This does not depend on
# the motif's pitches, only its length and the block structure, both of
# which generate() hardcodes the same way.
_MOTIF_LENGTH = 8
_BLOCK_SIZE = 16


def anchored_indices(steps: int = 64) -> set[int]:
    """Step indices that ``generate()`` fills from the hand-written motif
    template, never touched by the stochastic denoising process."""
    indices = set()
    for offset in range(0, steps, _BLOCK_SIZE):
        for idx in range(_MOTIF_LENGTH):
            if offset + idx < steps:
                indices.add(offset + idx)
    return indices


def fair_random_sequence(seed: int, steps: int = 64) -> list[int]:
    """Uniform random pick from the exact same candidate pool ``generate()``
    uses. No motif anchor, no transition weighting, no chord scoring: the
    baseline that isolates what the "smart" part of generate() contributes."""
    rng = random.Random(seed)
    return [rng.choice(CANDIDATES) for _ in range(steps)]


def generated_only(sequence: list[int], steps: int = 64) -> list[int]:
    """Strip the hand-written anchor out of a ``generate()`` output,
    replacing those positions with REST so scoring credits only the steps
    the denoising algorithm actually produced."""
    anchored = anchored_indices(steps)
    return [sequence[i] if i not in anchored else REST for i in range(steps)]


def generate_generated_only(seed: int, steps: int = 64) -> list[int]:
    return generated_only(generate(seed=seed, steps=steps), steps=steps)
