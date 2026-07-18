from __future__ import annotations

import random
from collections import Counter, defaultdict
from dataclasses import dataclass

REST = -1
C_MAJOR = {0, 2, 4, 5, 7, 9, 11}
CHORDS = [
    {60, 64, 67},
    {65, 69, 72},
    {67, 71, 74},
    {60, 64, 67},
]

CORPUS = [
    [60, 62, 64, 67, REST, 64, 62, 60, 65, 64, 62, 60, REST, 60, 62, 64],
    [67, 67, 69, 71, 72, REST, 71, 69, 67, 64, 65, 67, REST, 67, 65, 64],
    [60, REST, 60, 64, 67, 69, 67, 64, 62, REST, 62, 65, 69, 67, 65, 62],
    [72, 71, 69, 67, 65, REST, 64, 62, 60, 62, 64, 65, 67, REST, 64, 60],
]


@dataclass(frozen=True)
class MusicMetrics:
    scale_adherence: float
    motif_reuse: float
    tonal_anchor: float
    mean_leap: float


def _transition_counts() -> dict[int, Counter[int]]:
    counts: dict[int, Counter[int]] = defaultdict(Counter)
    for melody in CORPUS:
        prev = 60
        for pitch in melody:
            counts[prev][pitch] += 1
            if pitch != REST:
                prev = pitch
    return counts


def _candidate_score(candidate: int, prev: int, step: int, transition: dict[int, Counter[int]]) -> float:
    score = 0.2 + transition.get(prev, Counter()).get(candidate, 0)
    if candidate == REST:
        return score + (0.6 if step % 4 != 0 else -0.8)
    if candidate % 12 in C_MAJOR:
        score += 2.5
    chord = CHORDS[(step // 16) % len(CHORDS)]
    if step % 4 == 0 and candidate in chord:
        score += 2.0
    if prev != REST:
        leap = abs(candidate - prev)
        score += max(0.0, 2.0 - 0.25 * leap)
    return score


def generate(seed: int = 7, steps: int = 64) -> list[int]:
    rng = random.Random(seed)
    transition = _transition_counts()
    motif = [60, 62, 64, 67, REST, 64, 62, 60]
    sequence: list[int | None] = [None] * steps
    for offset in range(0, steps, 16):
        shift = 0 if offset % 32 == 0 else 5
        for idx, pitch in enumerate(motif):
            if offset + idx < steps:
                sequence[offset + idx] = REST if pitch == REST else pitch + shift

    candidates = [REST, 60, 62, 64, 65, 67, 69, 71, 72, 74]
    for _ in range(5):
        for idx in range(steps):
            if sequence[idx] is not None:
                continue
            prev = next((sequence[j] for j in range(idx - 1, -1, -1) if sequence[j] is not None), 60)
            assert prev is not None
            weights = [_candidate_score(c, prev, idx, transition) for c in candidates]
            total = sum(max(0.01, w) for w in weights)
            pick = rng.random() * total
            acc = 0.0
            for candidate, weight in zip(candidates, weights):
                acc += max(0.01, weight)
                if acc >= pick:
                    sequence[idx] = candidate
                    break

    return [int(pitch) if pitch is not None else REST for pitch in sequence]


def random_sequence(seed: int = 7, steps: int = 64) -> list[int]:
    rng = random.Random(seed)
    candidates = [REST] + list(range(48, 77))
    return [rng.choice(candidates) for _ in range(steps)]


def score_sequence(sequence: list[int]) -> MusicMetrics:
    notes = [pitch for pitch in sequence if pitch != REST]
    scale = sum(1 for pitch in notes if pitch % 12 in C_MAJOR) / max(1, len(notes))
    grams = [tuple(sequence[i : i + 4]) for i in range(max(0, len(sequence) - 3))]
    counts = Counter(grams)
    repeated = sum(count for gram, count in counts.items() if count > 1 and REST not in gram)
    motif_reuse = repeated / max(1, len(grams))
    anchors = []
    for idx in range(0, len(sequence), 4):
        pitch = sequence[idx]
        if pitch != REST:
            anchors.append(1.0 if pitch in CHORDS[(idx // 16) % len(CHORDS)] else 0.0)
    tonal_anchor = sum(anchors) / max(1, len(anchors))
    leaps = []
    last = None
    for pitch in notes:
        if last is not None:
            leaps.append(abs(pitch - last))
        last = pitch
    mean_leap = sum(leaps) / max(1, len(leaps))
    return MusicMetrics(scale, motif_reuse, tonal_anchor, mean_leap)
