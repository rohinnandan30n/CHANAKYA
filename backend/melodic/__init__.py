"""Melodic module for accent identification and raga mapping."""

from .accent_identifier import identify_accents
from .raga_engine import apply_raga
from .dev2 import apply_melody

__all__ = ["identify_accents", "apply_raga", "apply_melody"]
