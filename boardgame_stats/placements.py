"""Placement statistics shared by games with ranked player results."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime

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


@dataclass(frozen=True, slots=True)
class PlayerStreaks:
    """Longest runs of wins and losses for a player."""

    win: int
    loss: int


def _iter_game_results(game: GameRecord, game_index: int) -> Iterator[tuple[str, int]]:
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


def _iter_results(games: Iterable[GameRecord]) -> Iterator[tuple[str, int]]:
    for game_index, game in enumerate(games, start=1):
        if not isinstance(game, Mapping):
            raise TypeError(f"Game {game_index} must be an object")
        yield from _iter_game_results(game, game_index)


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


def summarize_player_streaks(
    games: Iterable[GameRecord],
) -> dict[str, PlayerStreaks]:
    """Calculate longest win and loss runs in each player's chronological games.

    Games without a player's result do not break that player's streak. Place 1
    is a win; every other place is a loss.
    """
    results_by_player: dict[str, list[tuple[datetime, int]]] = {}
    for game_index, game in enumerate(games, start=1):
        if not isinstance(game, Mapping):
            raise TypeError(f"Game {game_index} must be an object")

        game_datetime = game.get("game_datetime")
        if not isinstance(game_datetime, str):
            raise TypeError(f"Game {game_index} has no valid game_datetime")
        try:
            played_at = datetime.strptime(game_datetime, "%Y-%m-%dT%H:%M:%S")
        except ValueError as error:
            raise ValueError(
                f"Game {game_index} has an invalid game_datetime: {game_datetime!r}"
            ) from error

        for player_name, place in _iter_game_results(game, game_index):
            results_by_player.setdefault(player_name, []).append((played_at, place))

    return {
        player_name: _calculate_streaks(
            place for _, place in sorted(player_results, key=lambda result: result[0])
        )
        for player_name, player_results in results_by_player.items()
    }


def longest_win_streak(games: Iterable[GameRecord], player_name: str) -> int:
    """Return the player's longest consecutive run of first-place finishes."""
    if not player_name.strip():
        raise ValueError("player_name must not be empty")
    return summarize_player_streaks(games).get(player_name, PlayerStreaks(0, 0)).win


def longest_loss_streak(games: Iterable[GameRecord], player_name: str) -> int:
    """Return the player's longest consecutive run of non-first-place finishes."""
    if not player_name.strip():
        raise ValueError("player_name must not be empty")
    return summarize_player_streaks(games).get(player_name, PlayerStreaks(0, 0)).loss


def _calculate_streaks(places: Iterable[int]) -> PlayerStreaks:
    longest_win = longest_loss = 0
    current_win = current_loss = 0

    for place in places:
        if place == 1:
            current_win += 1
            current_loss = 0
        else:
            current_loss += 1
            current_win = 0
        longest_win = max(longest_win, current_win)
        longest_loss = max(longest_loss, current_loss)

    return PlayerStreaks(win=longest_win, loss=longest_loss)
