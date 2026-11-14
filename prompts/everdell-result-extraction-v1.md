# Everdell Digital result extraction prompt — v1

> For the current multi-image and archive workflow, use the
> [batch extraction prompt v3](everdell-batch-result-extraction-v3.md) with its
> [batch schema](../schemas/everdell-batch-result-extraction-v3.schema.json).
> This v1 prompt remains for historical single-image responses.

Attach this prompt and the image to the vision agent. The response must follow
[`everdell-result-extraction-v1.schema.json`](../schemas/everdell-result-extraction-v1.schema.json).
The schema is the data contract; change it only with a versioned contract
update.

```text
You extract structured data from Everdell Digital result screenshots for later
statistical analysis. Read the attached image and return exactly one JSON object
that conforms to the Everdell result extraction v1 schema provided with this
prompt. Return JSON only: no Markdown, comments, or surrounding prose.

Capture the complete visible result table. Every visible player row must appear
once, in its top-to-bottom order. For each row, extract the displayed place,
player name, avatar appearance, score, completed events, remaining resources,
any visible character label, and every other visible statistic or column value.
The standard fields do not limit what should be collected: put additional
table columns and metrics in additional_visible_fields, preserving each visible
label and value. Also record
useful game-level information visible on the result screen, such as its title,
result heading, outcome, date, duration, mode, or expansion. Do not include
decorative scenery, unrelated interface controls, or information from outside
the result screen.

Extraction rules:
- Read only the attached image. Never use prior examples, game rules, a file
  name, image metadata, or outside knowledge to fill a value.
- Copy names, labels, headings, and other text exactly as displayed, including
  capitalization, punctuation, and spacing where it is legible. Do not correct
  spelling or normalize a player's name.
- Return numeric standard fields as JSON integers only when the displayed value
  is legible. Preserve the exact displayed text in additional_visible_fields
  for other metrics; set numeric_value only when it is unambiguous.
- Set a data value to null when it is not displayed, unreadable, or ambiguous.
  Add that value's JSON path to unavailable_fields with the corresponding
  reason: not_shown, unreadable, or ambiguous. For example, record a null
  additional_visible_fields[i].value_raw, but do not report a null
  additional_visible_fields[i].numeric_value as unavailable when value_raw is
  visible text that is not an unambiguous integer.
- Use place_source = visible_label when the place is shown. If no place label is
  shown, infer place from row order only when the table clearly ranks rows from
  first to last; set place_source = row_order. Otherwise set place to null and
  place_source = unknown.
- Copy a character name or label into character_label_raw only if text naming
  it is visible. Describe the avatar's appearance in character_description.
  Do not assign a canonical character name or ID based only on resemblance.
- For additional_visible_fields, use scope = game for a game-level value and
  scope = player for a row value. Set row_order to the player's 1-based row
  position for player fields and null for game fields. Preserve the visible
  column/metric name in label_raw and its displayed value in value_raw.
- Do not omit a row because some of its fields are obscured. Keep the row and
  mark only unavailable fields.

Status rules:
- parsed: this is clearly a complete result screen and all visible result rows
  and their standard fields can be read. A field that is genuinely not shown is
  recorded as not_shown and does not by itself make the screen incomplete.
- needs_review: this appears to be a result screen, but it is cropped,
  ambiguous, or any visible result-table value is unreadable or ambiguous.
  Explain each issue in review_reasons.
- not_result: the image is not clearly an Everdell Digital result screen. Return
  no players and explain why in warnings.

Do not treat the screen heading alone as proof that every table value was read.
Do not drop ties or reorder rows by your own interpretation. Keep all rows as
shown. Keep warnings for relevant observations that do not fit the contract;
use additional_visible_fields for extra data that could matter to statistics.
```

The model's output is an extraction, not a verified database record. Preserve it
as returned and keep any later human correction separately.
