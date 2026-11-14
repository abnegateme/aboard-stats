"""Read the versioned Everdell JSON dataset into invariant models."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from aboard_stats.invariants import GameResult, PlayerResult

EXPECTED_SCHEMA_VERSION = "3.0.0"


@dataclass(frozen=True, slots=True)
class EverdellPlayerResult(PlayerResult):
    """Everdell-specific data extending the shared player result invariant."""

    character: str
    score: int
    events_completed: int
    resources_left: int

    def __post_init__(self) -> None:
        PlayerResult.__post_init__(self)
        if not isinstance(self.character, str) or not self.character.strip():
            raise ValueError("character must not be empty")
        for field_name in ("score", "events_completed", "resources_left"):
            value = getattr(self, field_name)
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{field_name} must be an integer")
            if value < 0:
                raise ValueError(f"{field_name} must not be negative")


class EverdellGameResult(GameResult):
    """Shared game result carrying Everdell-specific player extensions."""


def load_everdell_games(path: Path) -> list[EverdellGameResult]:
    """Load and validate the fields used by the Everdell statistics report."""
    try:
        dataset = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Cannot read dataset {path}: {error}") from error

    if not isinstance(dataset, Mapping):
        raise TypeError("Dataset root must be a JSON object")
    if dataset.get("schema_version") != EXPECTED_SCHEMA_VERSION:
        raise ValueError(
            f"Expected schema version {EXPECTED_SCHEMA_VERSION}, "
            f"got {dataset.get('schema_version')!r}"
        )

    games = dataset.get("games")
    if not isinstance(games, list):
        raise TypeError("Dataset must contain a games list")

    typed_games: list[EverdellGameResult] = []
    for game_index, game in enumerate(games, start=1):
        if not isinstance(game, Mapping):
            raise TypeError(f"Game {game_index} must be a JSON object")
        game_datetime = game.get("game_datetime")
        if not isinstance(game_datetime, str):
            raise TypeError(f"Game {game_index} has no valid game_datetime")
        try:
            ended_at = datetime.strptime(game_datetime, "%Y-%m-%dT%H:%M:%S")
        except ValueError as error:
            raise ValueError(
                f"Game {game_index} has an invalid game_datetime: {game_datetime!r}"
            ) from error

        raw_players = game.get("players")
        if not isinstance(raw_players, list):
            raise TypeError(f"Game {game_index} must contain a players list")
        players: list[EverdellPlayerResult] = []
        for player_index, raw_player in enumerate(raw_players, start=1):
            if not isinstance(raw_player, Mapping):
                raise TypeError(
                    f"Player {player_index} in game {game_index} must be an object"
                )
            try:
                players.append(
                    EverdellPlayerResult(
                        player_name=raw_player.get("player_name"),
                        place=raw_player.get("place"),
                        character=raw_player.get("character"),
                        score=raw_player.get("score"),
                        events_completed=raw_player.get("events_completed"),
                        resources_left=raw_player.get("resources_left"),
                    )
                )
            except (TypeError, ValueError) as error:
                raise ValueError(
                    f"Invalid player {player_index} in game {game_index}: {error}"
                ) from error

        try:
            typed_games.append(
                EverdellGameResult(
                    game_name="Everdell",
                    ended_at=ended_at,
                    players=tuple(players),
                )
            )
        except (TypeError, ValueError) as error:
            raise ValueError(f"Invalid game {game_index}: {error}") from error

    return typed_games
