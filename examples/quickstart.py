from motifdiff import generate, score_sequence, write_midi

sequence = generate(seed=3, steps=32)
metrics = score_sequence(sequence)
write_midi(sequence, "artifacts/quickstart.mid")
print(f"scale={metrics.scale_adherence:.2f} motif_reuse={metrics.motif_reuse:.2f}")
