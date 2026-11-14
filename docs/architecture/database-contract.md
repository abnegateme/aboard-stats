# SQLite Persistence Adapter

## Dependency direction

The package is organized in layers:

- `invariants` owns database-independent `GameResult` and `PlayerResult` models
  and validates the shared result contract.
- `interfaces` defines the required `GameDataset` and `GameRepository`
  protocols, plus the `ResultImageRecognizer` extension point. Applications
  keep one active dataset object and switch it when another export is selected.
- `database` contains SQLite adapters for the default writable repository and
  read-only company exports. They map rows to invariant models and back.
- `statistics` calculates summaries from invariant models without depending on
  a repository, SQLite, or JSON.
- Other `interfaces` modules adapt external formats and user-facing output. The
  Everdell JSON reader creates specialized models that extend the shared
  invariants.

The invariant contract is specified in [`../invariants.md`](../invariants.md).

## SQLite schema

The SQLite adapters use Python's standard library; no separate server or
third-party dependency is required. An active dataset is mandatory. If no
company export is selected, `create_default_repository` creates the local
`data/aboard-stats.sqlite3` database when absent and resumes it while it remains
the active dataset. An application can instead select a `SQLiteGameArchive` for
a company export. The schema version is stored in `PRAGMA user_version`.

The `games` table stores `game_name`, `ended_at`, and the derived `player_count`.
Its unique constraint on `(game_name, ended_at)` enforces persisted game identity.
The `game_results` table stores `player_name` and `place`, with a foreign key to
the game. Participant order is retained for stable output and does not affect
statistics. Equal places are allowed.

`SQLiteGameRepository.save_game` stores the game and all participant results
in one transaction. `load_games` reconstructs validated invariant models. The
adapter implements `GameRepository`; SQLite serialization is kept in
`aboard_stats.database.sqlite`, outside the invariant classes.

Writable persistence requires a timezone-aware `ended_at` and stores a
canonical UTC ISO 8601 timestamp with a `Z` suffix and microsecond precision. It
rejects naive wall-clock times because their UTC instant cannot be derived
safely. The current Everdell JSON interface keeps its timezone-naive source
times for reporting and does not import them into SQLite automatically.

The initial schema persists only the shared invariants. Saving a specialized
model stores only its shared projection; game-specific extension fields are not
persisted by this adapter. A game that needs those fields persisted will require
a game-specific repository or a later schema extension. Player-only views
and merged company datasets are not implemented in this version.
