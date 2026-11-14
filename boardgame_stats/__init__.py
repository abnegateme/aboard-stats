"""Reusable statistics helpers for board game results."""

from boardgame_stats.placements import (
    PlayerPlacementSummary,
    PlayerStreaks,
    count_player_placements,
    longest_loss_streak,
    longest_win_streak,
    summarize_player_placements,
    summarize_player_streaks,
)
from boardgame_stats.scores import (
    PlayerScoreStats,
    max_player_losing_gap,
    max_player_score,
    max_player_winning_margin,
    summarize_player_scores,
)

__all__ = [
    "PlayerPlacementSummary",
    "PlayerScoreStats",
    "PlayerStreaks",
    "count_player_placements",
    "longest_loss_streak",
    "longest_win_streak",
    "max_player_losing_gap",
    "max_player_score",
    "max_player_winning_margin",
    "summarize_player_placements",
    "summarize_player_scores",
    "summarize_player_streaks",
]
