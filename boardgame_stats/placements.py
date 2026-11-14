"""Placement statistics shared by games with ranked player results."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass

GameRecord = Mapping[str, object]


@dataclass(frozen=True, slots=True)
class PlayerPlacementSummary:
    """Placement counts for one player across a set of games."""

    player_name: str
    placements: Mapping[int, int]

    @property
    def games_played(self) -> int:
        """Return the number of recorded games for this player."""
        return sum(self.placements.values())


def _iter_results(games: Iterable[GameRecord]) -> Iterable[tuple[str, int]]:
    for game_index, game in enumerate(games, start=1):
        players = game.get("players")
        if not isinstance(players, Sequence) or isinstance(players, str | bytes):
            raise TypeError(f"Game {game_index} must contain a players list")

        for player_index, player in enumerate(players, start=1):
            if not isinstance(player, Mapping):
                raise TypeError(
                    f"Player {player_index} in game {game_index} must be an object"
                )

            player_name = player.get("player_name")
            place = player.get("place")
            if not isinstance(player_name, str):
                raise TypeError(
                    f"Player {player_index} in game {game_index} has no valid name"
                )
            if not player_name.strip():
                raise ValueError(
                    f"Player {player_index} in game {game_index} has no valid name"
                )
            if isinstance(place, bool) or not isinstance(place, int):
                raise TypeError(
                    f"Player {player_index} in game {game_index} has an invalid place"
                )
            if place < 1:
                raise ValueError(
                    f"Player {player_index} in game {game_index} has an invalid place"
                )

            yield player_name, place


def count_player_placements(
    games: Iterable[GameRecord], player_name: str
) -> dict[int, int]:
    """Count how many times ``player_name`` finished in each place.

    Names are matched exactly as written in the game records. The returned
    mapping contains only places that player occupied; an unknown player gets
    an empty mapping.
    """
    if not player_name.strip():
        raise ValueError("player_name must not be empty")

    counts: Counter[int] = Counter(
        place for name, place in _iter_results(games) if name == player_name
    )
    return dict(sorted(counts.items()))


def summarize_player_placements(
    games: Iterable[GameRecord],
) -> tuple[PlayerPlacementSummary, ...]:
    """Summarize placement counts for every player in the supplied games."""
    counts_by_player: dict[str, Counter[int]] = {}
    for player_name, place in _iter_results(games):
        counts_by_player.setdefault(player_name, Counter())[place] += 1

    summaries = (
        PlayerPlacementSummary(
            player_name=player_name,
            placements=dict(sorted(counts.items())),
        )
        for player_name, counts in counts_by_player.items()
    )
    return tuple(
        sorted(
            summaries,
            key=lambda summary: (-summary.games_played, summary.player_name.casefold()),
        )
    )
