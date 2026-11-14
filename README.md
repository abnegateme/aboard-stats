# Everdell result screenshot filter

Requires Python 3.15.

The first utility scans a folder recursively for likely Everdell result
screenshots. A quick OCR pass looks for a `VICTORY` or `DEFEAT` heading.
Placement labels (`1ST` through `4TH`) help recover difficult cases. The tool
does not read or save game results.
Likely matches are moved into an `everdell_results` folder inside the input
folder. If two images have the same name, the later one gets a numeric suffix.

The first pass supports BMP, GIF, JPEG, PNG, TIFF, and WebP images. The output
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
