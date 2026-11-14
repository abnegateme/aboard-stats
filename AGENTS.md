# AGENTS.md

## Project

Python 3.15 application.

## Development

Run tests with:

    pytest

Run linting with:

    ruff check .

Run formatting with:

    ruff format .

Run type checking with:

    mypy src

## Code style

- Use Python 3.15 syntax.
- Add type annotations to public functions.
- Prefer pathlib over os.path.
- Keep functions small.
- Use Python tooling to apply changes from inside the devcontainer.
- Do not create temporary files or backup copies, including files with `.bak` or `.orig` suffixes.
- Do not modify tests merely to make failing code pass.
- Add tests for new behavior.

## Commit Messages

When the user asks for a commit message, format it with:
- one concise summary line;
- a blank line;
- a bulleted list of concrete changes or additions.

## Before completing a task

Run:

    ruff check .
    pytest
