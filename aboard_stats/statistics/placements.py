"""Placement statistics calculated from invariant game result models."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass
from datetime import datetime

from aboard_stats.invariants import GameResult

# Kept as a public type alias for callers that used the former name.
GameRecord = GameResult


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


def _iter_results(games: Iterable[GameResult]) -> Iterator[tuple[str, int]]:
    for game_index, game in enumerate(games, start=1):
        if not isinstance(game, GameResult):
            raise TypeError(f"Game {game_index} must be a GameResult")
        for player in game.players:
            yield player.player_name, player.place


def count_player_placements(
    games: Iterable[GameResult], player_name: str
) -> dict[int, int]:
    """Count how many times ``player_name`` finished in each place."""
    if not player_name.strip():
        raise ValueError("player_name must not be empty")

    counts: Counter[int] = Counter(
        place for name, place in _iter_results(games) if name == player_name
    )
    return dict(sorted(counts.items()))


def summarize_player_placements(
    games: Iterable[GameResult],
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
    games: Iterable[GameResult],
) -> dict[str, PlayerStreaks]:
    """Calculate longest win and loss runs in each player's chronological games.

    Games without a player's result do not break that player's streak. Place 1
    is a win; every other place is a loss. Naive and timezone-aware game times
    cannot be mixed for the same player because their ordering is ambiguous.
    """
    results_by_player: dict[str, list[tuple[datetime, int]]] = {}
    awareness_by_player: dict[str, bool] = {}
    for game_index, game in enumerate(games, start=1):
        if not isinstance(game, GameResult):
            raise TypeError(f"Game {game_index} must be a GameResult")
        played_at = game.ended_at
        is_aware = played_at.tzinfo is not None and played_at.utcoffset() is not None

        for player in game.players:
            previous_awareness = awareness_by_player.setdefault(
                player.player_name, is_aware
            )
            if previous_awareness != is_aware:
                raise ValueError(
                    f"Cannot mix timezone-aware and naive game times for "
                    f"{player.player_name!r}"
                )
            results_by_player.setdefault(player.player_name, []).append(
                (played_at, player.place)
            )

    return {
        player_name: _calculate_streaks(
            place for _, place in sorted(player_results, key=lambda result: result[0])
        )
        for player_name, player_results in results_by_player.items()
    }


def longest_win_streak(games: Iterable[GameResult], player_name: str) -> int:
    """Return the player's longest consecutive run of first-place finishes."""
    if not player_name.strip():
        raise ValueError("player_name must not be empty")
    return summarize_player_streaks(games).get(player_name, PlayerStreaks(0, 0)).win


def longest_loss_streak(games: Iterable[GameResult], player_name: str) -> int:
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
