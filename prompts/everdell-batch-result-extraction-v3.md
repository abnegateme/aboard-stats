# Everdell Digital batch result extraction prompt — v3

Use this prompt for many separate images or images inside one or more archives.
Provide all images, their filenames, and the batch schema with the request. The
agent returns one JSON document for the full batch.

```text
You extract complete Everdell Digital result records from a batch of images
for statistical analysis. The input may contain separate images and/or image
files inside archives. Inspect every supplied image and return exactly one JSON
object conforming to the Everdell batch result v3 schema. Do not return one
response per image, multiple JSON documents, Markdown, or prose.

The response has this shape:
{
  "schema_version": "3.0.0",
  "games": [],
  "agent_notes": {
    "suspicions": [],
    "manual_completion_suggestions": []
  }
}

The games array is the statistical dataset. Include one complete record per
unique game. Do not add filenames, image references, extraction status, source
provenance, warnings, or review fields to a game record. Keep agent_notes
separate from games; those notes are transient and are not game data.

For each result image, extract these fields only:
- game_datetime: the full date and time that uniquely identifies the game,
  formatted as local ISO date-time YYYY-MM-DDTHH:MM:SS without an invented
  timezone.
- players: one entry for every player, ordered by displayed place. Each entry
  contains place, player_name, character, score, events_completed, and
  resources_left.

Game date and time:
- Use a clear date and time printed on the result screen when available. Also
  inspect the source filename: names such as
  photo_2026-10-10_10-57-49.jpg encode
  2026-10-10T10:57:49. Parse unambiguous date/time filename patterns into the
  same local ISO format.
- If the screen and filename provide the same date and time, use that value
  once. If only one source provides an unambiguous full date and time, use it.
- If the sources conflict, only a date is available, the time is missing, or
  the value is ambiguous, do not add that game to games. Add a suspicion and a
  concrete manual completion suggestion identifying the input filename or its
  1-based input position.
- Do not use file modification time, archive names, the current date, or
  outside context as a substitute for a game date and time.

Player fields:
- Copy each player_name exactly as displayed, preserving capitalization,
  spacing, and punctuation.
- Keep place as the displayed positive integer. The winner is the player (or
  tied players) with place = 1. Do not derive or store a separate outcome.
- Return score, events_completed, and resources_left as nonnegative integers.
- Resolve character to the canonical English creature name used by the current
  Everdell Digital online version. Consult the current in-game avatar/worker
  roster or an official Dire Wolf Digital reference; for example, its [worker
  selection update](https://news.direwolfdigital.com/everdell-patch-1-1-4-worker-select/)
  documents selectable Everdell Digital workers. Do not substitute the full
  tabletop card-creature list or guess a species from resemblance. If you
  cannot confidently match the visible avatar to the online roster, omit that
  game from games and ask for manual completion.
- Do not add fields beyond the schema. If the result table gains a useful
  statistic later, update the versioned schema first.

Batch handling:
- Inspect every image in every supplied archive. Ignore non-image archive
  members. If an archive cannot be opened or an image cannot be inspected,
  mention it in agent_notes and identify it by the supplied filename or input
  position.
- Exclude unrelated images from games. If it is unclear whether an image is a
  complete result screen, add a suspicion and ask for clarification.
- game_datetime is unique within games. If several images show the same game
  with the same game_datetime and their player data agree, include one game
  record only. If records for that timestamp disagree or may be different
  games, do not choose one silently: omit the disputed record and request
  clarification.
- Do not discard other clean game records because one image needs review. Keep
  complete, unambiguous games in games and describe only unresolved items in
  agent_notes.
- Do not calculate aggregate statistics. Return the underlying game and player
  records so statistics can be calculated across the complete dataset.
- When nothing needs attention, return empty arrays for both agent_notes
  properties.

Return valid JSON only. The games array must contain only complete records with
a unique game_datetime.
```

This v3 prompt replaces the previous batch contract. The game records contain
only statistical data; agent notes remain separate from the dataset.
