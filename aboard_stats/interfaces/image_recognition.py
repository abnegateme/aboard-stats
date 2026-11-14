"""Extension port for image-based game result recognition."""

from __future__ import annotations

from typing import Protocol

from aboard_stats.invariants import GameResult


class ResultImageRecognizer(Protocol):
    """Recognize a complete game result from the supplied image bytes."""

    def recognize(self, image: bytes) -> GameResult:
        """Return a validated game model or raise when it cannot be resolved."""
        ...
