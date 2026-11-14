"""Score and score-gap statistics calculated from invariant game models."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from aboard_stats.invariants import GameResult


@dataclass(frozen=True, slots=True)
class PlayerScoreStats:
    """Highest score and largest win/loss margins for one player."""

    max_score: int
    winning_margin: int
    losing_gap: int


def summarize_player_scores(
    games: Iterable[GameResult],
) -> dict[str, PlayerScoreStats]:
    """Calculate each player's highest score and largest win/loss margin.

    Player result models may carry an optional ``score`` extension. Games whose
    players do not provide that extension are rejected.
    """
    max_scores: dict[str, int] = {}
    max_winning_margins: dict[str, int] = {}
    max_losing_gaps: dict[str, int] = {}

    for game_index, game in enumerate(games, start=1):
        if not isinstance(game, GameResult):
            raise TypeError(f"Game {game_index} must be a GameResult")

        results: list[tuple[str, int, int]] = []
        for player in game.players:
            score = getattr(player, "score", None)
            if isinstance(score, bool) or not isinstance(score, int):
                raise TypeError(
                    f"Player {player.player_name!r} in game {game_index} "
                    "has an invalid score"
                )
            if score < 0:
                raise ValueError(
                    f"Player {player.player_name!r} in game {game_index} "
                    "has an invalid score"
                )
            results.append((player.player_name, player.place, score))

        second_place_scores = [score for _, place, score in results if place == 2]
        first_place_scores = [score for _, place, score in results if place == 1]

        for player_name, place, score in results:
            max_scores[player_name] = max(max_scores.get(player_name, 0), score)
            if place == 1 and second_place_scores:
                margin = max(0, score - max(second_place_scores))
                max_winning_margins[player_name] = max(
                    max_winning_margins.get(player_name, 0), margin
                )
            elif place != 1 and first_place_scores:
                gap = max(0, min(first_place_scores) - score)
                max_losing_gaps[player_name] = max(
                    max_losing_gaps.get(player_name, 0), gap
                )

    return {
        player_name: PlayerScoreStats(
            max_score=score,
            winning_margin=max_winning_margins.get(player_name, 0),
            losing_gap=max_losing_gaps.get(player_name, 0),
        )
        for player_name, score in max_scores.items()
    }


def max_player_score(games: Iterable[GameResult], player_name: str) -> int:
    """Return a player's highest recorded score, or zero if they have no games."""
    _validate_player_name(player_name)
    return (
        summarize_player_scores(games)
        .get(
            player_name,
            PlayerScoreStats(max_score=0, winning_margin=0, losing_gap=0),
        )
        .max_score
    )


def max_player_winning_margin(games: Iterable[GameResult], player_name: str) -> int:
    """Return the largest point margin over second place in the player's wins."""
    _validate_player_name(player_name)
    return (
        summarize_player_scores(games)
        .get(
            player_name,
            PlayerScoreStats(max_score=0, winning_margin=0, losing_gap=0),
        )
        .winning_margin
    )


def max_player_losing_gap(games: Iterable[GameResult], player_name: str) -> int:
    """Return the largest point gap from first place in the player's losses."""
    _validate_player_name(player_name)
    return (
        summarize_player_scores(games)
        .get(
            player_name,
            PlayerScoreStats(max_score=0, winning_margin=0, losing_gap=0),
        )
        .losing_gap
    )


def _validate_player_name(player_name: str) -> None:
    if not player_name.strip():
        raise ValueError("player_name must not be empty")
