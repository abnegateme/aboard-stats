"""Generate an HTML placement report from an Everdell v3 dataset."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping
from datetime import datetime
from pathlib import Path

from boardgame_stats.html_report import render_placement_report
from boardgame_stats.placements import (
    GameRecord,
    summarize_player_placements,
    summarize_player_streaks,
)
from boardgame_stats.scores import summarize_player_scores

DEFAULT_INPUT = Path("data/everdell-batch-results-v3.json")
DEFAULT_OUTPUT = Path("reports/everdell-statistics.html")
EXPECTED_SCHEMA_VERSION = "3.0.0"


def load_everdell_games(path: Path) -> list[GameRecord]:
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

    typed_games: list[GameRecord] = []
    for game_index, game in enumerate(games, start=1):
        if not isinstance(game, Mapping):
            raise TypeError(f"Game {game_index} must be a JSON object")
        game_datetime = game.get("game_datetime")
        if not isinstance(game_datetime, str):
            raise TypeError(f"Game {game_index} has no valid game_datetime")
        try:
            datetime.strptime(game_datetime, "%Y-%m-%dT%H:%M:%S")
        except ValueError as error:
            raise ValueError(
                f"Game {game_index} has an invalid game_datetime: {game_datetime!r}"
            ) from error

        # Validate player names and places before producing any report output.
        summarize_player_placements([game])
        typed_games.append(game)

    return typed_games


def _format_period(games: list[GameRecord]) -> str:
    if not games:
        return "Нет данных"

    game_dates = sorted(str(game["game_datetime"])[:10] for game in games)
    first_date = datetime.strptime(game_dates[0], "%Y-%m-%d").strftime("%d.%m.%Y")
    last_date = datetime.strptime(game_dates[-1], "%Y-%m-%d").strftime("%d.%m.%Y")
    return first_date if first_date == last_date else f"{first_date} — {last_date}"


def generate_everdell_report(input_path: Path, output_path: Path) -> Path:
    """Create a standalone HTML report and return its path."""
    if input_path.resolve() == output_path.resolve():
        raise ValueError("Input dataset and output report must be different files")

    games = load_everdell_games(input_path)
    summaries = summarize_player_placements(games)
    scores = summarize_player_scores(games)
    streaks = summarize_player_streaks(games)
    report = render_placement_report(
        summaries,
        scores=scores,
        streaks=streaks,
        game_count=len(games),
        period=_format_period(games),
        title="Everdell — статистика мест",
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Сформировать HTML-сводку по результатам Everdell."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"JSON-набор v3 (по умолчанию: {DEFAULT_INPUT})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Путь для HTML-отчета (по умолчанию: {DEFAULT_OUTPUT})",
    )
    args = parser.parse_args()

    try:
        output_path = generate_everdell_report(args.input, args.output)
    except (OSError, TypeError, ValueError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1

    print(f"Отчет сохранен: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
