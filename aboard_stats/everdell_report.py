"""Compatibility entry point for the Everdell report interface."""

from aboard_stats.interfaces.everdell_json import load_everdell_games
from aboard_stats.interfaces.everdell_report import (
    DEFAULT_INPUT,
    DEFAULT_OUTPUT,
    generate_everdell_report,
    main,
)

__all__ = [
    "DEFAULT_INPUT",
    "DEFAULT_OUTPUT",
    "generate_everdell_report",
    "load_everdell_games",
    "main",
]

if __name__ == "__main__":
    raise SystemExit(main())
