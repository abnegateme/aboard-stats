"""Reusable board game statistics models and calculations."""

from aboard_stats.invariants import GameResult, PlayerResult
from aboard_stats.statistics import (
    PlayerPlacementSummary,
    PlayerScoreStats,
    PlayerStreaks,
    count_player_placements,
    longest_loss_streak,
    longest_win_streak,
    max_player_losing_gap,
    max_player_score,
    max_player_winning_margin,
    summarize_player_placements,
    summarize_player_scores,
    summarize_player_streaks,
)

__all__ = [
    "GameResult",
    "PlayerPlacementSummary",
    "PlayerResult",
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
