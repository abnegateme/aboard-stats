# Everdell Digital batch result extraction prompt — v2

> Superseded by [batch prompt v3](everdell-batch-result-extraction-v3.md) and
> [schema v3](../schemas/everdell-batch-result-extraction-v3.schema.json).

Use this prompt for a set of screenshots, whether they are supplied as separate
images or as image files inside one or more archives. Provide the agent with the
complete source manifest and the
[`everdell-batch-result-extraction-v2.schema.json`](../schemas/everdell-batch-result-extraction-v2.schema.json)
as a structured-output schema (or include its contents in the request). The
response is one JSON document for the whole batch.

Provide a manifest in this form alongside the images (with one `sources` entry
per image):

```json
{
  "expected_image_count": 2,
  "sources": [
    {
      "input_order": 1,
      "source_ref": "photo_2026-10-10_10-57-49.jpg",
      "source_filename": "photo_2026-10-10_10-57-49.jpg"
    },
    {
      "input_order": 2,
      "source_ref": "results.zip!/2026/photo_2026-10-11.jpg",
      "source_filename": "photo_2026-10-11.jpg"
    }
  ]
}
```

The manifest's `expected_image_count` and `sources` list must enumerate every
image supplied directly or contained in an archive; non-image archive members
do not count. Each `source_ref` must uniquely identify one image. The prompt's
output `images` array mirrors that list. If the complete manifest is unavailable,
use null for `expected_image_count` and set `batch_status` to `needs_review`.

```text
You extract Everdell Digital result data from a batch of images for later
statistical analysis. The input may contain many separate images and/or one or
more archives containing many images. Inspect every image in the supplied
source manifest and return exactly one JSON object conforming to the supplied
Everdell batch result extraction v2 schema. Do not return one response per
image. Return one combined JSON object only, with no Markdown or prose.

The source manifest provides the expected image count, an input order, a
source_ref for each image, and its source_filename when available. Copy these
identifiers exactly. For an image in an archive, source_ref must identify both
the archive and its internal relative path, for example
"results.zip!/2026/photo_2026-10-10_10-57-49.jpg". Use the image's basename as
source_filename. Do not invent filenames, paths, or identifiers.

Return one images entry for every image in the manifest, in the same order,
including unrelated images and images that cannot be read. Keep the supplied
expected_image_count and set processed_image_count to the number of images
entries you return. Never silently omit an image. If an archive cannot be
opened, its contents cannot be inspected, or the response limit prevents
processing every image, set batch_status to "needs_review", explain the issue
in warnings, and include a needs_review placeholder for every known source.
Non-image archive members may be skipped; mention their count in warnings when
it can be determined. If an archive or image source cannot be enumerated, add
it to unprocessed_sources with a reason, set batch_status to "needs_review",
and explain it in top-level warnings. Do not represent an archive itself as an
image.

For each image:
- If it is a clear, complete result screen, set status to "parsed" and put its
  extracted data in game.
- If it is not an Everdell Digital result screen, set status to "not_result",
  set game to null, and explain briefly in warnings.
- If it is unreadable, incomplete, ambiguous, or has a visible value that
  cannot be read, set status to "needs_review" and explain the problem in
  review_reasons. Keep any data that can still be read in game; use game = null
  only when no useful game record can be extracted.
- Preserve every player row from top to bottom. Do not drop ties or reorder
  rows. Extract place, player name, character label if visibly written, avatar
  appearance, score, completed events, remaining resources, and every other
  visible table column or metric.
- Copy all visible result-table column headings into table_headers_raw in their
  left-to-right order, including headings for standard fields when shown.
- Preserve extra game- or player-level columns in
  additional_visible_fields, with the exact visible label and value. Do not
  restrict extraction to the currently known standard fields.
- Capture useful game-level details visible on the result screen, including
  result heading, outcome, duration, mode, and expansion where present. Ignore
  decorative scenery and unrelated controls.

Date handling is important for statistics:
- Extract an unambiguous date from the image's source_filename as
  filename_date_raw and normalize it to filename_date (YYYY-MM-DD). Support
  clear forms such as YYYY-MM-DD, YYYY_MM_DD, and YYYYMMDD, including names
  such as photo_2026-10-10_10-57-49.jpg. Do not interpret ambiguous numeric
  sequences as dates unless the source manifest specifies their format. If the
  filename contains multiple different date tokens, set filename_date_raw and
  filename_date to null, mark them ambiguous, and require review instead of
  choosing one.
- Also extract a date visibly printed on the result screen as screen_date_raw
  and normalize it to screen_date (YYYY-MM-DD) only when unambiguous.
- Set game_date to the only available unambiguous date when just one source has
  a date. If both sources have the same date, use that date and set
  game_date_source to "both". If the dates conflict, set game_date to null,
  preserve both source dates, set game_date_source to "conflict", and require
  review. If neither provides a date, use null and "unknown" and require
  review because the game's date is needed for chronological statistics. Never
  infer a date from the current date, file modification time, archive name, or
  outside context.

Extraction rules:
- Read values only from the image, plus the supplied source manifest for its
  identifiers and filename. Do not use game rules, prior examples, file
  metadata, or outside knowledge to fill result values.
- Copy names, labels, headings, and displayed values exactly where legible.
  Do not correct spelling or normalize player names.
- Return standard numeric fields as JSON integers only when legible. For extra
  fields, preserve value_raw and set numeric_value only when it is an
  unambiguous integer.
- Use null for a data value that is not shown, unreadable, or ambiguous. Add a
  corresponding path to unavailable_fields with reason not_shown, unreadable,
  or ambiguous. A null numeric_value is expected for visible nonnumeric text
  and does not need an unavailable_fields entry when value_raw is present.
- Use place_source = "visible_label" for a displayed place. Infer place from
  row order only when the table clearly ranks the rows; then use
  place_source = "row_order". Otherwise set place to null and source to
  "unknown".
- Copy character names into character_label_raw only if text naming the
  character is visible. Describe the avatar in character_description, but do
  not assign a canonical character name or ID from resemblance alone.
- For additional_visible_fields use scope = "game" and row_order = null for
  game-level values; use scope = "player" and that player's 1-based row_order
  for player values.
- Compare images within the batch for likely duplicate screenshots. Do not
  remove either record. Put the other image's source_ref in
  possible_duplicate_sources and require review. Do not flag screenshots as
  duplicates merely because they show the same players or similar scores; they
  must appear to show the same game result.

Batch status:
- Use "complete" only if every expected image has an images entry, all result
  images have a clear game_date, all entries have status parsed or not_result,
  and no possible duplicates need review.
- Otherwise use "needs_review" and summarize missing, unreadable, uncertain,
  or duplicate items in top-level warnings. Put image-specific details in the
  affected entry's review_reasons.
- Do not calculate averages, win rates, rankings across games, or other
  aggregate statistics. Return the underlying per-image game records so the
  application can calculate statistics from the full dataset.

Return valid JSON only. Preserve all source images and extracted game records
in this single response.
```

The batch contract supersedes the single-image v1 contract for multi-image
work. Keep the original extraction and later human corrections separate.
