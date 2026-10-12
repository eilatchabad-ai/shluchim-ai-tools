# Shabbat Message Agent

Every week, many Chabad Houses send the same message: candle lighting,
Shabbos ends, and davening times. It is short, it is read by more people
than almost anything else the Chabad House sends, and one wrong number sends
people to shul an hour late.

This agent prepares that message for **any city**, in **Hebrew, English
and/or French**, from real sources only:

- candle lighting and Shabbos ends from **your Rav's luach** if you give it
  as a table, cross-checked against **Hebcal**; or from Hebcal alone, and then
  the report says so plainly;
- davening times from **your own rules** in one config file, with the
  arithmetic shown for every line;
- parasha, special Shabbos, Mevorchim and Rosh Chodesh from Hebcal, with
  names from a fixed table (an unknown name stops the run; nothing is guessed).

It **never sends anything**. It prints a draft and a certainty report, and
waits for you. It **stops and asks** on a holiday or fast week, a clock
change, a gap between your luach and Hebcal, or any missing data.

Optional: **a thought for Shabbat** ("✨ מחשבה לשבת"), at most three short
lines from the Rebbe's Torah on the parasha, written for a traditional Jew
with no background in Chassidus, so the message people already read every
week also carries a word of Chassidus. The idea is found through the
[Torah MCP](https://mcp.shluchimexchange.ai/) shared by Shluchim Exchange,
or the shliach's own notebook of the Rebbe's Torah, and **read in the source
itself** before use. The message carries no citation; the full source is
given to the shliach under the draft. No checked source, no paragraph.

Built and used at Chabad Eilat; the default rules were verified against
123 real weekly messages (`RULES.md`).

## Three ways to use it

| You have | Do this |
|---|---|
| Claude Code or Codex | Open this folder, type `I want to start` (or `אני רוצה להתחיל`). The agent fills `config.json` with you. See `START_HERE.md`. |
| Python only | Fill `config.json` by hand (below), then run `python tools/build_message.py` (Windows) or `python3 tools/build_message.py` (Mac/Linux). |
| Just a chat assistant | Paste `PASTE-PROMPT.md` into ChatGPT, Claude or Gemini with web search on. |

## Quick try, no setup

```
python tools/build_message.py --config examples/new-york.json 2026-10-16
python tools/build_message.py --config examples/jerusalem.json 2026-10-16
python tools/build_message.py --config examples/eilat.json 2026-10-16
```

The davening times in the New York and Jerusalem examples are illustrative
rules, not a real shul's schedule. Eilat's rules are real.

## Filling `config.json`

| Field | What to put |
|---|---|
| `community.name`, `community.city` | Per language, e.g. `{"en": "Chabad of Midtown", "he": "בית חב״ד מידטאון"}` |
| `location.geonameid` | Hebcal's city number. Find it: `python tools/build_message.py --find-city "Midtown"`, or search the city on hebcal.com/shabbat and take the `geonameid` from the address bar |
| `languages` | Any of `"he"`, `"en"`, `"fr"` |
| `candle_lighting_minutes` | Minutes before sunset. 18 is common; Jerusalem is 40 (Hebcal fixes it); follow your Rav. The script checks that Hebcal really used your number |
| `havdalah` | `{"mode": "tzeit_8.5"}` (nightfall, sun 8.5° below the horizon) or `{"mode": "minutes", "minutes": 50}` |
| `clock` | Per language: `"24h"` (17:45), `"12h"` (5:45 pm) or `"h"` (17h45) |
| `english_style` | `"ashkenazi"` (Parshas, Shabbos) or `"sephardic"` (Parashat, Shabbat) |
| `own_table.csv` | Path to your luach as CSV: `date,candle,havdalah,label`, where `date` is the Friday. It becomes the authority; Hebcal is the check. `max_gap_minutes` (default 3) stops the run on a bigger gap. Name it `data/my-zmanim.csv` to keep it out of git |
| `times.friday`, `times.shabbat`, `times.weekdays` | Lists of davening times (below) |
| `closing` | Closing lines per language: `always`, `chol_hamoed` (replaces `always` when Chol HaMoed days follow), `elul`, `rosh_chodesh_on_shabbat`, `nisan` |
| `carry_max_age_days` | Default 21. A carried time unchanged for longer gets a WARNING above the draft |
| `title_overrides` | Your spelling of a parasha, per language, keyed by Hebcal's English name: `{"he": {"Ki Tavo": "כי תבא"}}` |
| `weekly_thought` | `enabled` (default `false`), `title` per language, `max_lines` (3), `max_line_chars`, `audience`, `sources`. The paragraph itself comes from a thought file (`--thought`, format in `examples/thought-noach-5787.json`) |

### Each davening time

Every item has an `id`, a `label` per language, and **one** of:

```json
{"id": "shacharis", "label": {"en": "Shacharis"}, "fixed": "10:00"}

{"id": "mincha", "label": {"en": "Mincha"},
 "rule": {"from": "candle", "offset": 0, "round_to": 5, "round": "down", "not_after": "19:00"}}

{"id": "mincha", "label": {"en": "Mincha"},
 "carry": {"initial": "18:30"}}
```

- `fixed`: the same time every week.
- `rule`: computed from `candle`, `havdalah`, `sunset_fri`, `sunset_sat`,
  `sunrise_sat`, `sunset_sun` (Sunday after Shabbat, for weekday times),
  `tzeit_sun` (Sunday nightfall, 7.083 degrees) or `tzeit85_sun` (8.5
  degrees), plus `offset` minutes, rounded `down`, `up` or `nearest` to
  `round_to` minutes, optionally limited by `not_after` / `not_before`.
  Optional `hold: {"duration": 25, "end_within": 5}`: when the rule moves the
  time earlier, keep last week's approved time while a service of
  `duration` minutes starting then still ends within `end_within` minutes
  after the rule's base time (never across a clock change).
- `carry`: set by hand; the agent repeats last week's approved time and flags
  it. `initial` is the first week's value; `suggest` can hold a rule used only
  as a first-week suggestion; `watch` + `alert_minutes` flag drift against
  sunrise or sunset.

Optional on any item: `"languages": ["he"]` (only in some messages),
`"only_in_months": ["Elul"]` or `"not_in_months": [...]` (Hebcal month names),
`"blank_before": true`, `"cross_check": {"with": "friday/mincha", "max_minutes": 20}`
(stop when this time is further than that from another one; a printed
poster is checked like anything else), `"optional": true` (a carried line with no value is
left out instead of blocking), and `"evidence"` (your own note; ignored by
the script).

## What it checks every week

| Check | Result |
|---|---|
| Own luach vs Hebcal, more than 3 minutes apart | Stop; a ~60-minute gap is named as a probable clock change |
| Clocks change during the coming week | Stop; weekday times need confirming |
| Clock changed since last approved week | Stop; every carried time needs confirming |
| Holiday or fast in the week, or no parasha | Stop; holiday messages are not built here |
| Hebcal did not use your candle-lighting minutes | Stop |
| Parasha, special Shabbos or month name not in `data/names.json` | Stop; never guessed |
| A time with no source | `[MISSING]` and stop |
| Carried time drifted 8+ minutes against sunrise | Flag for approval |
| Carried time unchanged for 3+ weeks | WARNING above the draft |
| A time outside its `cross_check`, or a `--set` value far from its rule | Stop / flag |
| One-day Yom Tov from Friday night to Shabbat night | Normal message with a Yom Tov title, "Chol HaMoed" weekday block when it follows |

## Files

```
AGENTS.md          instructions for Claude Code / Codex (CLAUDE.md points here)
START_HERE.md      first run
WORKFLOW.md        the weekly procedure, including the Torah MCP line
OUTPUT_FORMAT.md   what the message looks like in each language
RULES.md           the default rules and the evidence behind them
PASTE-PROMPT.md    the same job as one prompt for any chat assistant
config.json        the one file you fill
examples/          Eilat (he+fr), Jerusalem (he+en), New York (en),
                   and a thought file (Noach 5787)
tools/build_message.py   standard-library Python 3.8+, no install
data/names.json    parasha / special Shabbos / month names in he, en, fr
data/own-table.template.csv   the header for your own luach table
PRIVACY-CHECK.md   what was removed from the private original, and the check
SUBMISSION.md      the ChabadLabs Promptathon entry
```

Sources: [Hebcal](https://www.hebcal.com/home/developer-apis) Shabbat,
Zmanim, Jewish calendar and date-converter APIs (free, no key; Hebcal's
content is licensed CC BY 4.0). Optional:
[Torah MCP](https://mcp.shluchimexchange.ai/).

---

## בעברית

סוכן שמכין את הודעת זמני השבת השבועית של בית חב״ד, לכל עיר, בעברית,
באנגלית או בצרפתית. זמני הכניסה והיציאה נלקחים מהלוח של הרב המקומי כשיש
טבלה כזו, ונבדקים מול Hebcal; כשאין לוח, Hebcal הוא המקור ודוח הוודאות
אומר זאת במפורש. זמני התפילות מחושבים לפי כללים שנקבעים פעם אחת בקובץ
`config.json`, וליד כל זמן מוצג החשבון שהוביל אליו.

הסוכן אינו שולח דבר לשום מקום ואינו ממציא אף מספר. בשבוע של חג או צום,
במעבר שעון, בפער בין הלוח ל-Hebcal או בכל נתון חסר, הוא עוצר ושואל.

כדי להתחיל: יש לפתוח את התיקייה ב-Claude Code או ב-Codex ולכתוב
**אני רוצה להתחיל**. בלי Claude Code אפשר להדביק את `PASTE-PROMPT.md`
לכל עוזר צ׳אט עם חיפוש ברשת.

אפשרות להוסיף "✨ מחשבה לשבת": עד שלוש שורות קצרות מתורת הרבי על הפרשה,
כתובות ליהודי מסורתי בלי רקע בחסידות, וכל צעד בהן מוסבר. בהודעה עצמה אין
מקור; המקור המלא (ספר, כרך, שיחה, עמוד) נמסר לשליח בנפרד, מתחת לטיוטה.
את הרעיון מוצאים דרך ה-Torah MCP או מחברת אישית של תורת הרבי, ואת המקור
יש לקרוא בספר עצמו לפני השימוש. כשאין מקור שנבדק, אין פסקה.

---

Mendel Slonim, Chabad Eilat. MIT License (see the repository root).
