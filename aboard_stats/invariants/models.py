"""Database-independent models for the board game statistics contract."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


def _current_utc_time() -> datetime:
    return datetime.now(UTC)


@dataclass(frozen=True, slots=True)
class PlayerResult:
    """One player's display name and occupied place in a game."""

    player_name: str
    place: int

    def __post_init__(self) -> None:
        if not isinstance(self.player_name, str) or not self.player_name.strip():
            raise ValueError("player_name must not be empty")
        if isinstance(self.place, bool) or not isinstance(self.place, int):
            raise TypeError("place must be an integer")
        if self.place < 1:
            raise ValueError("place must be positive")


@dataclass(frozen=True, slots=True)
class GameResult:
    """A completed game and its participant results.

    Timezone-aware timestamps are normalized to UTC. A naive timestamp is
    preserved as a wall-clock value for legacy sources that provide no timezone;
    persistence adapters may reject it when they require an unambiguous instant.
    """

    game_name: str
    players: tuple[PlayerResult, ...]
    ended_at: datetime = field(default_factory=_current_utc_time)

    def __post_init__(self) -> None:
        if not isinstance(self.game_name, str) or not self.game_name.strip():
            raise ValueError("game_name must not be empty")
        if not isinstance(self.ended_at, datetime):
            raise TypeError("ended_at must be a datetime")

        if self.ended_at.tzinfo is not None and self.ended_at.utcoffset() is not None:
            object.__setattr__(self, "ended_at", self.ended_at.astimezone(UTC))

        try:
            players = tuple(self.players)
        except TypeError as error:
            raise TypeError(
                "players must be an iterable of PlayerResult values"
            ) from error
        if not players:
            raise ValueError("a game must contain at least one player result")
        for player_index, player in enumerate(players, start=1):
            if not isinstance(player, PlayerResult):
                raise TypeError(f"Player result {player_index} must be a PlayerResult")
            if player.place > len(players):
                raise ValueError(
                    f"Player result {player_index} place exceeds player count"
                )
        object.__setattr__(self, "players", players)

    @property
    def player_count(self) -> int:
        """Return the number of participant result rows in this game."""
        return len(self.players)
