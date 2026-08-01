"""Tests for the hardcoded-motif and tautological-baseline findings."""

from __future__ import annotations

from motifdiff.generator import REST, generate, random_sequence, score_sequence
from motifdiff.generator_v2 import (
    anchored_indices,
    fair_random_sequence,
    generated_only,
)

STEPS = 64


# --- the finding: half the "guided" sequence is a hardcoded motif ----------

def test_exactly_half_the_sequence_is_anchored():
    anchored = anchored_indices(STEPS)
    assert len(anchored) == 32
    assert len(set(range(STEPS)) - anchored) == 32


def test_anchored_positions_are_the_same_transposed_motif_every_block():
    """The four anchored blocks are the identical 8-note motif, transposed
    by 0 or +5 semitones, not four independently generated phrases."""
    seq = generate(seed=12)
    anchored = sorted(anchored_indices(STEPS))
    block0 = [seq[i] for i in anchored if i < 16]
    block2 = [seq[i] for i in anchored if 32 <= i < 48]
    assert block0 == block2  # both are shift=0 blocks (offset 0 and 32)


# --- the finding: scale_adherence is tautological --------------------------

def test_scale_adherence_is_guaranteed_for_any_generate_output():
    """generate()'s candidate pool is pre-restricted to in-scale pitches,
    so scale_adherence == 1.0 regardless of the weighting logic."""
    for seed in range(1, 10):
        assert score_sequence(generate(seed=seed)).scale_adherence == 1.0


def test_fair_random_also_hits_perfect_scale_adherence():
    """A naive uniform pick from the SAME restricted candidate pool, no
    weighting at all, gets the identical scale_adherence score."""
    for seed in range(1, 10):
        assert score_sequence(fair_random_sequence(seed)).scale_adherence == 1.0


def test_published_random_baseline_uses_an_unrestricted_chromatic_range():
    """The strawman: random_sequence draws from 30 chromatic pitches, not
    the same palette generate() is restricted to."""
    seq = random_sequence(seed=1)
    notes = {p for p in seq if p != REST}
    assert len(notes) > 0
    assert not all(p in {60, 62, 64, 65, 67, 69, 71, 72, 74} for p in notes)


# --- the fix: isolate the algorithm's real, non-tautological contribution --

def test_generated_only_strips_the_hardcoded_anchor():
    full = generate(seed=12)
    stripped = generated_only(full)
    anchored = anchored_indices(STEPS)
    for i in anchored:
        assert stripped[i] == REST
    for i in set(range(STEPS)) - anchored:
        assert stripped[i] == full[i]


def test_algorithm_beats_fair_baseline_on_average_but_modestly():
    """Averaged over many seeds (not one anecdote): the transition-and-
    chord weighting has a real, positive, but modest effect on tonal_anchor
    and mean_leap once the hardcoded motif and unfair baseline are removed."""
    n = 50
    gen_tonal = gen_leap = fair_tonal = fair_leap = 0.0
    for seed in range(1, n + 1):
        gm = score_sequence(generated_only(generate(seed=seed)))
        fm = score_sequence(fair_random_sequence(seed))
        gen_tonal += gm.tonal_anchor
        gen_leap += gm.mean_leap
        fair_tonal += fm.tonal_anchor
        fair_leap += fm.mean_leap
    gen_tonal /= n
    gen_leap /= n
    fair_tonal /= n
    fair_leap /= n

    assert gen_tonal > fair_tonal  # real edge, algorithm beats fair random
    assert gen_leap < fair_leap    # real edge, smaller leaps than fair random
    # but the edge is modest, nowhere near the published guided-vs-random gap
    assert gen_tonal - fair_tonal < 0.2
    assert fair_leap - gen_leap < 2.0


def test_fair_random_is_deterministic():
    assert fair_random_sequence(7) == fair_random_sequence(7)


# --- the original module is untouched ---------------------------------------

def test_original_generator_module_untouched():
    import motifdiff.generator as generator_module

    assert not hasattr(generator_module, "fair_random_sequence")


def test_original_benchmark_numbers_still_reproduce():
    guided = score_sequence(generate(seed=12))
    random_baseline = score_sequence(random_sequence(seed=12))
    assert round(guided.scale_adherence, 2) == 1.00
    assert round(random_baseline.scale_adherence, 2) == 0.46
    assert round(guided.mean_leap, 2) == 3.90
    assert round(random_baseline.mean_leap, 2) == 9.87
