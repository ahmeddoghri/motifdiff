from pathlib import Path

from motifdiff import generate, score_sequence, write_midi


def test_generation_is_deterministic() -> None:
    assert generate(seed=5) == generate(seed=5)


def test_guided_sequence_is_tonal() -> None:
    metrics = score_sequence(generate(seed=9))
    assert metrics.scale_adherence >= 0.90
    assert metrics.tonal_anchor >= 0.50


def test_writes_valid_midi(tmp_path: Path) -> None:
    path = write_midi(generate(seed=1, steps=16), tmp_path / "demo.mid")
    assert path.read_bytes().startswith(b"MThd")
    assert b"MTrk" in path.read_bytes()
