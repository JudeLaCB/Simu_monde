"""Project-owned deterministic random number generation."""

from __future__ import annotations

import random


class SeededRNG:
    """A deterministic random-number stream owned by the simulation core."""

    def __init__(self, seed: int) -> None:
        if isinstance(seed, bool) or not isinstance(seed, int):
            raise TypeError("seed must be an integer, not a boolean")
        self._generator = random.Random(seed)

    def random(self) -> float:
        """Return the next pseudo-random value in the half-open interval [0, 1)."""
        return self._generator.random()
