"""Score and score-gap statistics for ranked game results."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from boardgame_stats.placements import GameRecord, _iter_game_players


@dataclass(frozen=True, slots=True)
class PlayerScoreStats:
    """Highest score and largest win/loss margins for one player."""

    max_score: int
    winning_margin: int
    losing_gap: int


def summarize_player_scores(
    games: Iterable[GameRecord],
) -> dict[str, PlayerScoreStats]:
    """Calculate each player's highest score and largest win/loss margin.

    For a win, the margin is the player's score minus the second-place score.
    For a loss, it is the first-place score minus the player's score. Games
    without the relevant comparison place do not contribute a margin.
    """
    max_scores: dict[str, int] = {}
    max_winning_margins: dict[str, int] = {}
    max_losing_gaps: dict[str, int] = {}

    for game_index, game in enumerate(games, start=1):
        if not isinstance(game, Mapping):
            raise TypeError(f"Game {game_index} must be an object")

        results: list[tuple[str, int, int]] = []
        for player_name, place, player in _iter_game_players(game, game_index):
            score = player.get("score")
            if isinstance(score, bool) or not isinstance(score, int):
                raise TypeError(
                    f"Player {player_name!r} in game {game_index} has an invalid score"
                )
            if score < 0:
                raise ValueError(
                    f"Player {player_name!r} in game {game_index} has an invalid score"
                )
            results.append((player_name, place, score))

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


def max_player_score(games: Iterable[GameRecord], player_name: str) -> int:
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


def max_player_winning_margin(games: Iterable[GameRecord], player_name: str) -> int:
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


def max_player_losing_gap(games: Iterable[GameRecord], player_name: str) -> int:
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
