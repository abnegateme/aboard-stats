"""SQLite implementations for active repositories and exported datasets."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from aboard_stats.interfaces.repositories import GameDataset, GameRepository
from aboard_stats.invariants import GameResult, PlayerResult

DEFAULT_DATABASE_PATH = Path("data/aboard-stats.sqlite3")
_SCHEMA_VERSION = 1
_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS games (
    game_id INTEGER PRIMARY KEY,
    game_name TEXT NOT NULL CHECK (length(trim(game_name)) > 0),
    ended_at TEXT NOT NULL,
    player_count INTEGER NOT NULL CHECK (player_count > 0),
    UNIQUE (game_name, ended_at)
);

CREATE TABLE IF NOT EXISTS game_results (
    game_id INTEGER NOT NULL REFERENCES games(game_id) ON DELETE CASCADE,
    player_order INTEGER NOT NULL CHECK (player_order > 0),
    player_name TEXT NOT NULL CHECK (length(trim(player_name)) > 0),
    place INTEGER NOT NULL CHECK (place > 0),
    PRIMARY KEY (game_id, player_order)
);
"""


class SQLiteGameRepository(GameRepository):
    """Writable SQLite repository for the active local dataset."""

    def __init__(self, database_path: Path) -> None:
        self._database_path = database_path

    def initialize(self) -> None:
        """Create an empty database when absent, or validate its schema."""
        connection = self._connect()
        try:
            version = connection.execute("PRAGMA user_version").fetchone()[0]
            if version > _SCHEMA_VERSION:
                raise RuntimeError(
                    f"Database schema version {version} is newer than supported "
                    f"version {_SCHEMA_VERSION}"
                )
            connection.executescript(_SCHEMA_SQL)
            connection.execute(f"PRAGMA user_version = {_SCHEMA_VERSION}")
        finally:
            connection.close()

    def save_game(self, game: GameResult) -> None:
        """Persist the shared invariants for one game in a single transaction."""
        if not isinstance(game, GameResult):
            raise TypeError("game must be a GameResult")
        ended_at_text = _format_datetime(game.ended_at)
        self.initialize()
        connection = self._connect()
        try:
            with connection:
                cursor = connection.execute(
                    """
                    INSERT INTO games (game_name, ended_at, player_count)
                    VALUES (?, ?, ?)
                    """,
                    (game.game_name, ended_at_text, game.player_count),
                )
                game_id = cursor.lastrowid
                if game_id is None:
                    raise RuntimeError("SQLite did not return the new game ID")
                connection.executemany(
                    """
                    INSERT INTO game_results (
                        game_id, player_order, player_name, place
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        (game_id, player_order, player.player_name, player.place)
                        for player_order, player in enumerate(game.players, start=1)
                    ),
                )
        finally:
            connection.close()

    def load_games(self) -> tuple[GameResult, ...]:
        """Load rows from the active database as validated invariant models."""
        self.initialize()
        connection = self._connect()
        try:
            return _read_games(connection)
        finally:
            connection.close()

    def _connect(self) -> sqlite3.Connection:
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self._database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection


class SQLiteGameArchive(GameDataset):
    """Read-only view of an exported company database."""

    def __init__(self, database_path: Path) -> None:
        self._database_path = database_path

    def load_games(self) -> tuple[GameResult, ...]:
        """Read an exported database without initializing or modifying it."""
        if not self._database_path.is_file():
            raise FileNotFoundError(self._database_path)
        connection = sqlite3.connect(
            f"{self._database_path.resolve().as_uri()}?mode=ro",
            uri=True,
        )
        connection.row_factory = sqlite3.Row
        try:
            version = connection.execute("PRAGMA user_version").fetchone()[0]
            if version != _SCHEMA_VERSION:
                raise RuntimeError(
                    f"Unsupported exported database schema version {version}"
                )
            return _read_games(connection)
        finally:
            connection.close()


def create_default_repository(
    database_path: Path = DEFAULT_DATABASE_PATH,
) -> SQLiteGameRepository:
    """Create or resume the clean-by-default local database repository."""
    repository = SQLiteGameRepository(database_path)
    repository.initialize()
    return repository


def _read_games(connection: sqlite3.Connection) -> tuple[GameResult, ...]:
    game_rows = connection.execute(
        """
        SELECT game_id, game_name, ended_at
        FROM games
        ORDER BY ended_at, game_name
        """
    ).fetchall()
    games: list[GameResult] = []
    for game_row in game_rows:
        player_rows = connection.execute(
            """
            SELECT player_name, place
            FROM game_results
            WHERE game_id = ?
            ORDER BY player_order
            """,
            (game_row["game_id"],),
        ).fetchall()
        games.append(
            GameResult(
                game_name=game_row["game_name"],
                ended_at=_parse_datetime(game_row["ended_at"]),
                players=tuple(
                    PlayerResult(
                        player_name=row["player_name"],
                        place=row["place"],
                    )
                    for row in player_rows
                ),
            )
        )
    return tuple(games)


def _format_datetime(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("SQLite storage requires a timezone-aware ended_at")
    return (
        value.astimezone(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")
    )


def _parse_datetime(value: str) -> datetime:
    if not value.endswith("Z"):
        raise ValueError("Stored ended_at must use the canonical UTC Z suffix")
    return datetime.fromisoformat(value)
