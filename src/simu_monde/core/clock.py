"""Fixed-timestep simulation clock."""

from __future__ import annotations

from math import isfinite


class SimulationClock:
    """Track simulation time from an integer tick count and fixed timestep."""

    def __init__(self, dt_seconds: float) -> None:
        if isinstance(dt_seconds, bool):
            raise ValueError("dt_seconds must be a positive, finite number")

        try:
            valid = isfinite(dt_seconds) and dt_seconds > 0
        except TypeError as error:
            raise ValueError("dt_seconds must be a positive, finite number") from error

        if not valid:
            raise ValueError("dt_seconds must be a positive, finite number")

        self._dt_seconds = float(dt_seconds)
        self._tick_index = 0

    @property
    def dt_seconds(self) -> float:
        """The immutable duration of one simulation tick in seconds."""
        return self._dt_seconds

    @property
    def tick_index(self) -> int:
        """The number of elapsed simulation ticks."""
        return self._tick_index

    @property
    def time_seconds(self) -> float:
        """Simulation time derived from the tick count."""
        return self._tick_index * self._dt_seconds

    def advance(self) -> None:
        """Advance the clock by exactly one tick."""
        self._tick_index += 1
