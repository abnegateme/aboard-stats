"""Render placement summaries as a self-contained HTML page."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from html import escape

from boardgame_stats.placements import PlayerPlacementSummary, PlayerStreaks


def render_placement_report(
    summaries: Sequence[PlayerPlacementSummary],
    *,
    streaks: Mapping[str, PlayerStreaks],
    game_count: int,
    period: str,
    title: str,
) -> str:
    """Render a responsive, dependency-free placement report."""
    all_places = {place for summary in summaries for place in summary.placements}
    places = list(range(1, max(all_places, default=1) + 1))
    place_headers = "".join(
        f'<th class="place place-{place}" scope="col">{place}-е место</th>'
        for place in places
    )

    rows: list[str] = []
    for summary in summaries:
        cells = "".join(
            f'<td class="place place-{place}">{summary.placements.get(place, 0)}</td>'
            for place in places
        )
        player_streaks = streaks.get(summary.player_name, PlayerStreaks(0, 0))
        rows.append(
            "<tr>"
            f'<th class="player" scope="row">{escape(summary.player_name)}</th>'
            f'<td class="games">{summary.games_played}</td>'
            f"{cells}"
            f'<td class="streak">{player_streaks.win}</td>'
            f'<td class="streak">{player_streaks.loss}</td>'
            "</tr>"
        )

    if rows:
        table_body = "\n".join(rows)
    else:
        table_body = (
            f'<tr><td class="empty" colspan="{4 + len(places)}">'
            "В этом наборе пока нет результатов."
            "</td></tr>"
        )

    player_count = len(summaries)
    return f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>
    :root {{ color-scheme: light; --ink: #19342d; --muted: #62736d; --paper: #f4f7f2; --line: #dce5dc; --green: #245c47; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--paper); color: var(--ink); font: 16px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif; }}
    main {{ width: min(1120px, calc(100% - 32px)); margin: 48px auto; }}
    .eyebrow {{ margin: 0 0 8px; color: var(--green); font-size: .76rem; font-weight: 750; letter-spacing: .12em; text-transform: uppercase; }}
    h1 {{ margin: 0; font-size: clamp(2rem, 5vw, 3.25rem); letter-spacing: -.045em; line-height: 1.08; }}
    .intro {{ margin: 12px 0 28px; color: var(--muted); }}
    .cards {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; margin-bottom: 24px; }}
    .card {{ min-height: 104px; padding: 18px 20px; border: 1px solid var(--line); border-radius: 16px; background: #fff; box-shadow: 0 5px 18px #19342d08; }}
    .card-label {{ display: block; color: var(--muted); font-size: .85rem; }}
    .card-value {{ display: block; margin-top: 5px; font-size: 1.55rem; font-weight: 750; letter-spacing: -.025em; }}
    .table-wrap {{ overflow: auto; border: 1px solid var(--line); border-radius: 16px; background: #fff; box-shadow: 0 8px 28px #19342d0b; }}
    table {{ width: 100%; border-collapse: collapse; white-space: nowrap; }}
    caption {{ padding: 18px 20px 14px; text-align: left; font-size: 1.05rem; font-weight: 700; }}
    th, td {{ padding: 13px 16px; border-top: 1px solid #edf1ec; text-align: right; }}
    thead th {{ color: var(--muted); background: #fafcf9; font-size: .82rem; font-weight: 650; }}
    th:first-child, td:first-child {{ text-align: center; }}
    .player {{ min-width: 180px; text-align: left; font-weight: 650; }}
    .games {{ font-weight: 700; }}
    .place {{ min-width: 102px; font-variant-numeric: tabular-nums; }}
    .streak {{ min-width: 110px; font-variant-numeric: tabular-nums; font-weight: 650; }}
    .place-1 {{ color: #8a5b00; }}
    .place-2 {{ color: #586a75; }}
    .place-3 {{ color: #87533a; }}
    tbody tr:hover {{ background: #f7faf6; }}
    .empty {{ padding: 36px; color: var(--muted); text-align: center; }}
    footer {{ margin: 14px 4px; color: var(--muted); font-size: .84rem; }}
    @media (max-width: 640px) {{ main {{ margin: 28px auto; }} .cards {{ grid-template-columns: 1fr; gap: 9px; }} .card {{ min-height: 0; padding: 14px 16px; }} .card-value {{ font-size: 1.25rem; }} }}
  </style>
</head>
<body>
  <main>
    <p class="eyebrow">Статистика настольных игр</p>
    <h1>{escape(title)}</h1>
    <p class="intro">Занятые места и максимальные серии для каждого игрока.</p>
    <section class="cards" aria-label="Общая информация">
      <article class="card"><span class="card-label">Партий</span><span class="card-value">{game_count}</span></article>
      <article class="card"><span class="card-label">Игроков</span><span class="card-value">{player_count}</span></article>
      <article class="card"><span class="card-label">Период</span><span class="card-value">{escape(period)}</span></article>
    </section>
    <div class="table-wrap">
      <table>
        <caption>Места и серии</caption>
        <thead><tr><th class="player" scope="col">Игрок</th><th scope="col">Партий</th>{place_headers}<th scope="col">Макс. серия побед</th><th scope="col">Макс. серия поражений</th></tr></thead>
        <tbody>
{table_body}
        </tbody>
      </table>
    </div>
    <footer>Строки упорядочены по числу партий. Имена учитываются точно так, как они записаны в наборе данных.</footer>
  </main>
</body>
</html>
"""
