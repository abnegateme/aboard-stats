"""Compatibility imports for placement statistics."""

from aboard_stats.statistics.placements import (
    GameRecord,
    PlayerPlacementSummary,
    PlayerStreaks,
    count_player_placements,
    longest_loss_streak,
    longest_win_streak,
    summarize_player_placements,
    summarize_player_streaks,
)

__all__ = [
    "GameRecord",
    "PlayerPlacementSummary",
    "PlayerStreaks",
    "count_player_placements",
    "longest_loss_streak",
    "longest_win_streak",
    "summarize_player_placements",
    "summarize_player_streaks",
]
