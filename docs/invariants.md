# Game Result Invariants

These models define the shared contract for persistence adapters and statistical
calculations. They contain no database or JSON serialization logic. Validation
runs when a model is constructed.

## Game name

`GameResult.game_name` is a non-empty title. Its spelling and capitalization are
preserved. The title participates in the persisted game identity; it is not a
foreign key to a separate catalog yet.

## Game finish time

`GameResult.ended_at` is the time the game finished, when its result can be
collected. It defaults to the current UTC time for immediate entry. A timezone-
aware value is normalized to UTC. A naive value is preserved as a wall-clock time
for sources, such as the existing Everdell JSON dataset, that do not provide a
timezone. No timezone is inferred for a naive value.

Persistence requires an unambiguous, timezone-aware value. The SQLite adapter
stores it in UTC. Statistical ordering rejects a mixture of naive and aware times
for the same player.

## Game identity

A persisted game is uniquely identified by `(game_name, ended_at)`. Different
games can share a timestamp; a duplicate title and timestamp cannot be saved
twice. This is a collection-level invariant enforced by the persistence adapter's
unique constraint.

## Player count

`GameResult.player_count` is derived from the number of player result records; it
is not independently supplied. A game must contain at least one result. This
prevents the stored count from disagreeing with the participant rows.

## Player name and occupied place

Each `PlayerResult` has a non-empty `player_name` and a positive integer `place`.
The place cannot exceed the game's player count. Equal places are valid for ties.
Names are display labels rather than stable player identities; identical names
within one game remain separate participant records.

## Extensions

Game-specific attributes such as scores, characters, resources, or rule versions
are extensions to the shared contract. They may be represented by specialized
models, but they do not change the shared game identity, participant count, or
place rules. The initial SQLite schema persists only the shared contract.
