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

__all__ = [
    "PlayerPlacementSummary",
    "PlayerStreaks",
    "count_player_placements",
    "longest_loss_streak",
    "longest_win_streak",
    "summarize_player_placements",
    "summarize_player_streaks",
]
