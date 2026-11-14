# Everdell tools

Requires Python 3.15.

## Placement statistics

The `boardgame_stats` package counts how many times each player finished in
each place. Names are matched exactly as recorded in the dataset. To calculate
counts for one player:

```python
import json
from pathlib import Path

from boardgame_stats import count_player_placements

dataset = json.loads(Path("data/everdell-batch-results-v3.json").read_text())
counts = count_player_placements(dataset["games"], "Corviurge")
print(counts)  # For example: {1: 12, 2: 8, 3: 4, 4: 2}
```

Generate a standalone HTML summary for all players:

```bash
python -m boardgame_stats.everdell_report
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
