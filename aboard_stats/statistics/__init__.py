"""Pure statistical calculations over invariant game models."""

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
from aboard_stats.statistics.scores import (
    PlayerScoreStats,
    max_player_losing_gap,
    max_player_score,
    max_player_winning_margin,
    summarize_player_scores,
)

__all__ = [
    "GameRecord",
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
