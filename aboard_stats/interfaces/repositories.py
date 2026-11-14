"""Extension ports for application-provided game data storage."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from aboard_stats.invariants import GameResult


class GameDataset(Protocol):
    """Read-only source of invariant game records, such as an exported file."""

    def load_games(self) -> Sequence[GameResult]:
        """Return the available games as invariant models."""
        ...


class GameRepository(GameDataset, Protocol):
    """Writable active database supplied by an application."""

    def save_game(self, game: GameResult) -> None:
        """Persist one completed game."""
        ...
