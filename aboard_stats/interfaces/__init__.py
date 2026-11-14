"""Extension ports and user-facing interfaces for board game statistics."""

from aboard_stats.interfaces.image_recognition import ResultImageRecognizer
from aboard_stats.interfaces.repositories import GameDataset, GameRepository

__all__ = ["GameDataset", "GameRepository", "ResultImageRecognizer"]
