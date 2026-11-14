# AI-Assisted Result Screenshot Workflow

## Direction

Reading a result screen with an AI agent is a simpler first step than designing
and maintaining a local OCR and image-recognition pipeline. The agent can
inspect the screenshot directly, but it needs a clear, reusable prompt attached
to every image so that it reads the same fields, follows the same rules, and
reports uncertainty instead of guessing.

The first application should therefore solve a narrower problem: find result
screenshots among a collection of photos. It should identify and present likely
matches for review; it does not need to extract player names, scores, or other
game data. Once this screening step is usable, pass selected screenshots to an
AI agent together with the prepared prompt. The next product focus can then be
the mathematical model for game statistics and the user interface.

This direction updates the implementation order in
[the main plan](result-image-parsing.md). Its local OCR, geometry-normalization,
and avatar-matching pipeline is deferred; those details remain useful if local
parsing is later needed.

## Initial Workflow

1. Select or scan a directory of photos.
2. Run the lightweight result-screen filter. It recursively scans image files,
   moves likely matches into `everdell_results`, and prints their source paths
   and heuristic confidence.
3. Review the collected candidates and adjust the filter if it misses or
   incorrectly selects screenshots. The first version does not need a separate
   confirmation interface and does not parse result fields.
4. Attach each confirmed screenshot to an AI-agent request with the same
   versioned prompt.
5. Review the returned values and uncertain fields before using them in the
   game's statistics model.

The screening mechanism can be chosen independently. It may use simple visual
signals or a small classifier, but its output should be a candidate image and
confidence, not a `ParsedGame`. Do not alter image contents; report the source
path when moving a candidate.

The first script implementation uses a quick Tesseract OCR pass with
English language data to find either the `VICTORY` or `DEFEAT` heading. It uses
placement labels (`1ST` through `4TH`) as recovery evidence when the heading is
hard to read, then tries larger and alternate OCR passes only for those
ambiguous images. This is an initial screening heuristic; it does not extract
player fields and should be refined against a real photo collection.

## Prompt Requirements

The prompt sent with every screenshot should:

- state that the task is to read an Everdell Digital result screen;
- list the fields and their expected types;
- preserve player names exactly as shown;
- require `null` for unreadable or absent values and prohibit guessing;
- distinguish a result screen from an unrelated or ambiguous image;
- return one machine-readable JSON object with no extra prose;
- include warnings and identify fields that need human review.

Keep the prompt under version control and record its version with each parsed
result. Refine it against varied screenshots before relying on its output for
statistics.

## Prompt Draft

Attach this instruction with each candidate screenshot and adjust the schema
only through a versioned prompt change. This handoff format is an initial
agent response format; it does not have to match the eventual database schema.

```text
Read the attached image. It may show an Everdell Digital game result screen.

The status value must be "parsed", "not_result", or "needs_review".
Return exactly one JSON object with this shape:
{
  "status": "parsed",
  "results": [
    {
      "place": 1,
      "player_name": "exact text shown",
      "score": 95,
      "events_completed": 3,
      "resources_left": 2,
      "character_description": "brief visible description",
      "uncertain_fields": []
    }
  ],
  "warnings": []
}

Rules:
- If the image is not clearly a game result screen, return status
  "not_result", an empty results array, and a short warning.
- Read only values visible in the image. Do not infer missing values from game
  rules, context, or another source.
- Copy each player name exactly, including capitalization and punctuation.
- Return numeric fields as integers only when they are clearly legible;
  otherwise return null and include the field name in uncertain_fields.
- List player rows from top to bottom. Do not invent rows that are not visible.
- Do not guess a canonical character name or ID. Give only a brief description
  of the visible avatar, or null if it cannot be described confidently.
- Use status "needs_review" if any result field is uncertain or the screen is
  incomplete. Explain the issue in warnings.
- Return valid JSON only. Use null for unknown values; do not use comments,
  markdown fences, or text before or after the JSON object.
```

The draft is a starting point, not a claim that agent output is always correct.
Initially, all output should be reviewable, and corrections should be kept
separate from the agent's original response.

## First Milestone

The screenshot-screening tool is ready for the next stage when it can process a
photo collection, move likely result-screen candidates to the output folder,
and report what it selected. Structured extraction, SQLite persistence, local
OCR of player fields, and avatar identification are not requirements for this
milestone. Once candidates can be gathered reliably, work can move to the
mathematical model and the user interface, using the AI-agent workflow to read
result screenshots in the meantime.
