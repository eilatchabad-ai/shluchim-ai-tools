# The weekly run

## Inputs

- The Friday date (default: the coming Friday; on a Friday, today)
- `config.json` (or another config with `--config`)
- The own zmanim table, if `own_table.csv` is set
- `data/state.json` (or `data/state-<config name>.json`): the times the user
  approved last week. Created by the first `--save`.
- Hebcal, live: four requests, all printed in the report

## Steps

1. **Run the script.**
   `python tools/build_message.py [YYYY-MM-DD]` (Windows) or
   `python3 tools/build_message.py [YYYY-MM-DD]` (Mac/Linux).
   Exit code 0 = clean draft, 2 = blockers, 3 = no draft (config or data).

2. **Read the certainty report before anything else.** If there is a blocker
   (exit code 2), show the blockers to the user first, in plain words, and
   stop. Do not "fix" a blocker by choosing a time yourself. Typical blockers
   and what to ask:

   | Blocker | What to ask the user |
   |---|---|
   | Own table and Hebcal differ by more than the limit | Which is right? A gap of about 60 minutes is almost always a clock change missed in the table |
   | The clocks change during the week | Which weekday times move, and to what? |
   | The clock changed since the saved week | Confirm each carried time on the new clock |
   | Holiday or fast in the week | Is this week a holiday message? (Not built here. A one-day Yom Tov from Friday night to Shabbat night is not a blocker: it gets a normal message with a Yom Tov title, and "Chol HaMoed" on the weekday block when those days follow) |
   | Own table has no row for this Friday | The row from the printed luach |
   | Name not in `data/names.json` | The spelling the community uses |
   | Carried time with no saved value | The time, or a rule to put in `config.json` |
   | A time does not fit its `cross_check` (e.g. weekday Mincha more than 20 min from Friday Mincha) | Where did the time come from? A printed poster is checked like any other value: one was 35 minutes off and looked right |
   | WARNING: a carried time unchanged for 3+ weeks | Is it still right after the change of season? |

3. **Check the title.** If the community spells a parasha differently, offer
   to add it to `title_overrides` in `config.json` (show the exact line first).

4. **Optional: a thought for Shabbat.** Only if `weekly_thought.enabled` is
   `true`. Otherwise skip to step 5.
   1. Find an idea on this week's parasha in the Rebbe's Torah, with the
      Torah MCP (`https://mcp.shluchimexchange.ai/`, START_HERE.md section 4)
      or the shliach's own notebook of the Rebbe's Torah.
   2. **Read the passage itself** (the sicha or maamar in the book or its
      scan), not only the search result or the notebook's answer. Confirm
      who says what: a notebook once put Rashi's words in the Rebbe's mouth.
      If the passage cannot be read, stop here: no paragraph this week, and
      say why.
   3. Write at most 3 short lines for a traditional Jew with no background
      in Chassidus: one line of background on the parasha, then the idea,
      with every step explained ("תיבה", the ark, is also "a word"). Your own
      words; never a published translation's wording. Gender-neutral Hebrew.
   4. No source inside the lines. The source goes in the file, for the
      shliach.
   5. Save `output/thought-YYYY-MM-DD.json` (format: `examples/thought-noach-5787.json`):

      ```json
      {
        "he": ["<line 1>", "<line 2>"],
        "en": ["<line 1>", "<line 2>"],
        "source": {
          "work": "<book and volume>",
          "location": "<sicha or section, page>",
          "builds_on": "<an earlier source the idea builds on, if any>",
          "found_via": "<Torah MCP query, or the notebook>",
          "checked": "<how the passage itself was read>"
        }
      }
      ```

   6. Run the script again with `--thought output/thought-YYYY-MM-DD.json`.
      The script refuses more than 3 lines, a missing `work`, `location` or
      `checked`, and the book's name inside the message lines. It prints the
      source under the draft, marked "for the shliach only".

5. **Show the user:** each draft in full, then the certainty report: where
   candle lighting and Shabbat ends came from (own table or Hebcal, with the
   gap), which davening times were computed, fixed, carried or suggested, and
   the "for approval" notes. If Hebcal was the only source this week, say so
   in one plain sentence. If there is a thought paragraph, give its full
   source under the draft, separately from the message text.

6. **Wait.** Do not send, do not save, do not continue.

7. **After an explicit approval:**
   - Corrections for this week: run with `--set section/id=HH:MM` for each,
     and show the corrected draft again if anything changed.
   - Then run with `--save` (plus the same `--set` options). This stores the
     approved times for next week and writes `output/YYYY-MM-DD-<config>-<lang>.txt`.
   - `--save` refuses while there are blockers. Add `--confirmed` only if the
     user explicitly approved the draft with its blockers in view.

## Done means

The user saw the drafts and the report, approved them, the times were saved,
and the text files were written. Sending is the user's own step.
