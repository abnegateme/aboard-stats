"""Compatibility imports for score statistics."""

from aboard_stats.statistics.scores import (
    PlayerScoreStats,
    max_player_losing_gap,
    max_player_score,
    max_player_winning_margin,
    summarize_player_scores,
)

__all__ = [
    "PlayerScoreStats",
    "max_player_losing_gap",
    "max_player_score",
    "max_player_winning_margin",
    "summarize_player_scores",
]
