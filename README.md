# aboard-stats

## Project disclaimer

aboard-stats began as a simple statistics tool for online Everdell. It is
gradually expanding into a general-purpose library and applications for board
game statistics; the current tools and data formats are still focused on
Everdell.

Requires Python 3.15.

## Invariants and extension interfaces

The shared data model is independent of storage and defined in
[`docs/invariants.md`](docs/invariants.md). The architecture and SQLite adapter
are described in
[`docs/architecture/database-contract.md`](docs/architecture/database-contract.md).
The package separates `invariants`, `database`, `statistics`, and `interfaces`.

An active dataset object is required. If no company export is selected, the
application uses its clean local database, created by `create_default_repository`
on first use. Selecting a company export switches the active dataset to a
read-only object; the exported file is not modified. Applications may also
provide their own `GameRepository` implementation. Image recognition can be
supplied through `ResultImageRecognizer`, which returns the same invariant game
model.

```python
from datetime import UTC, datetime
from pathlib import Path

from aboard_stats import GameResult, PlayerResult, summarize_player_placements
from aboard_stats.database import (
    SQLiteGameArchive,
    create_default_repository,
)

repository = create_default_repository()
game = GameResult(
    game_name="Everdell",
    ended_at=datetime(2026, 11, 14, 18, 30, tzinfo=UTC),
    players=(PlayerResult("Corviurge", 1), PlayerResult("Alice", 2)),
)
repository.save_game(game)
print(summarize_player_placements(repository.load_games()))

company_export = SQLiteGameArchive(Path("exports/company.sqlite3"))
print(summarize_player_placements(company_export.load_games()))
```

`GameResult.ended_at` defaults to the current UTC time for results entered
immediately after a game. Existing Everdell JSON and its report remain supported;
their timezone-naive timestamps are not silently converted to UTC. Player-only
views and merged company datasets are future work.

## Placement statistics

The `aboard_stats` package counts how many times each player finished in
each place. Names are matched exactly as recorded in the dataset. To calculate
counts for one player:

```python
from pathlib import Path

from aboard_stats import count_player_placements
from aboard_stats.interfaces.everdell_json import load_everdell_games

games = load_everdell_games(Path("data/everdell-batch-results-v3.json"))
counts = count_player_placements(games, "Corviurge")
print(counts)  # For example: {1: 12, 2: 8, 3: 4, 4: 2}
```

The `longest_win_streak(games, player_name)` and
`longest_loss_streak(games, player_name)` functions return the longest run of
wins and non-first-place finishes. Streaks follow each game's `ended_at`; games
where the player did not participate do not interrupt a streak.

`max_player_score(games, player_name)` returns the player's highest score.
`max_player_winning_margin(games, player_name)` returns the largest winning
margin over second place. `max_player_losing_gap(games, player_name)` returns
the largest gap from first place in a loss, regardless of the player's place.

Generate a standalone HTML summary for all players:

```bash
python -m aboard_stats.everdell_report
```

By default, the script reads `data/everdell-batch-results-v3.json` and writes
`reports/everdell-statistics.html`. Open that file in a browser. Use `--input`
and `--output` to choose different paths.

The placement counting and HTML rendering helpers are separate from the
Everdell dataset loader so they can be reused with other games that use the
same player/place result structure.

## Screenshot filtering

The screenshot utility scans a folder recursively for likely Everdell result
screenshots. A quick OCR pass looks for a `VICTORY` or `DEFEAT` heading.
Placement labels (`1ST` through `4TH`) help recover difficult cases. The tool
does not read or save game results.
Likely matches are moved into an `everdell_results` folder inside the input
folder. If two images have the same name, the later one gets a numeric suffix.

The utility supports BMP, GIF, JPEG, PNG, TIFF, and WebP images. The output
folder is skipped on later runs. The current detector is a heuristic and should
be checked against the user's photo collection.

## Setup on Windows

Install Python 3.15, then open PowerShell in the project folder:

```powershell
py -3.15 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts\filter_result_screenshots.py "C:\path\to\photos"
```

## Setup on Linux

Install Python 3.15 and its venv support, then run from the project folder:

```bash
python3.15 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/filter_result_screenshots.py "/path/to/photos"
```

The OCR engine and English language data are installed into the environment
from `requirements.txt`; no separate OCR installation is needed.
