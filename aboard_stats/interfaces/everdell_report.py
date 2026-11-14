"""Generate an HTML placement report from an Everdell v3 dataset."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from aboard_stats.interfaces.everdell_json import load_everdell_games
from aboard_stats.interfaces.html_report import render_placement_report
from aboard_stats.invariants import GameResult
from aboard_stats.statistics import (
    summarize_player_placements,
    summarize_player_scores,
    summarize_player_streaks,
)

DEFAULT_INPUT = Path("data/everdell-batch-results-v3.json")
DEFAULT_OUTPUT = Path("reports/everdell-statistics.html")


def _format_period(games: Sequence[GameResult]) -> str:
    if not games:
        return "Нет данных"

    game_dates = sorted(game.ended_at.date() for game in games)
    first_date = game_dates[0].strftime("%d.%m.%Y")
    last_date = game_dates[-1].strftime("%d.%m.%Y")
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
