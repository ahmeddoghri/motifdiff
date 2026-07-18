"""Masked motif diffusion for small MIDI generation demos."""

from .generator import generate, score_sequence
from .midi import write_midi

__all__ = ["generate", "score_sequence", "write_midi"]
