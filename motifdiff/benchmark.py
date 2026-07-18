from __future__ import annotations

import json
from pathlib import Path

from .generator import generate, random_sequence, score_sequence
from .midi import write_midi


def main() -> None:
    out = Path("artifacts")
    out.mkdir(exist_ok=True)
    guided = generate(seed=12)
    random_baseline = random_sequence(seed=12)
    guided_metrics = score_sequence(guided)
    random_metrics = score_sequence(random_baseline)
    write_midi(guided, out / "motifdiff.mid")
    payload = {
        "guided": guided_metrics.__dict__,
        "random": random_metrics.__dict__,
    }
    (out / "metrics.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print("motifdiff benchmark: masked symbolic MIDI generation")
    print("metric             guided   random")
    print(f"scale_adherence     {guided_metrics.scale_adherence:5.2f}    {random_metrics.scale_adherence:5.2f}")
    print(f"motif_reuse         {guided_metrics.motif_reuse:5.2f}    {random_metrics.motif_reuse:5.2f}")
    print(f"tonal_anchor        {guided_metrics.tonal_anchor:5.2f}    {random_metrics.tonal_anchor:5.2f}")
    print(f"mean_leap           {guided_metrics.mean_leap:5.2f}    {random_metrics.mean_leap:5.2f}")
    print("artifact            artifacts/motifdiff.mid")


if __name__ == "__main__":
    main()
