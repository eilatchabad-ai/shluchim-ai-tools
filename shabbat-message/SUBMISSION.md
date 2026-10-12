# ChabadLabs Promptathon entry

**Entry title:** Weekly Shabbat Times Message Agent

**Category:** Apps, tools and agents

**Author:** Mendel Slonim, Chabad Eilat

## What it is

An agent that prepares the weekly Shabbat-times message a Chabad House
sends to its community (candle lighting, Shabbos ends, davening times) for
any city, in Hebrew, English and/or French. Every time has a named source
(the Rav's luach, Hebcal, or the shliach's own rule with the arithmetic
shown), the agent stops and asks on holiday weeks, clock changes, stale or
suspicious times and missing data, and it never sends anything by itself.
It reaches the widest circle a Chabad House has, the people who read
nothing else but the weekly times, and it can add a short "thought for
Shabbat" from the Rebbe's Torah, written for a traditional Jew with no
background in Chassidus, from a source the shliach has read in the book
itself.

## Output

Real output of the tested runs on 12 October 2026, for Shabbat Parshas
Noach (Friday 16 October 2026). Not edited.

### Hebrew: Eilat, Israel, Friday 16 October 2026

The times are per the luach and the community's rules; the final times are
confirmed by the author before the message goes out.

```
python tools/build_message.py --config <examples/eilat.json, thought enabled> --table <luach.csv> --state <state.json> --thought examples/thought-noach-5787.json 2026-10-16
```

```
שבת פרשת נח

🕯️ זמני שבת – אילת:
הדלקת נרות: 17:49
צאת השבת: 18:44

📍 זמני תפילות – בית חב״ד

ערב שבת:
מנחה: 17:45

שבת קודש:
שחרית מוקדם (נץ): 05:20
שחרית שני: 08:30
מנחה: 17:15

⏰ ימי חול:
שחרית מוקדם: 06:00
שחרית שני: 08:00

מנחה: 17:45
ערבית: 18:35

✨ מחשבה לשבת
ה' הביא מבול על העולם, ונח ומשפחתו ניצלו בתיבה. "תיבה" היא גם מילה, ולכן הבעל שם טוב מסביר: כשסוער סביבנו, נכנסים אל המילים של התפילה והתורה.
והרבי מוסיף: נח לא נכנס לבד. גם אנחנו מביאים איתנו את כל מי שסביבנו, ואפילו את מי שנראה רחוק.

שבת שלום!
```

Printed under the draft, for the shliach only (not part of the message):

```
SOURCE OF THE THOUGHT - for the shliach only, not in the message:
   work: Torat Menachem – Hisvaaduyos 5743, vol. 1
   location: Shabbos Parshas Noach (unedited), pp. 426–427
   builds_on: The Baal Shem Tov's reading of the verse "בא אתה וכל ביתך אל התבה" (Genesis 7:1): תיבה is also a word of Torah and prayer
   found_via: a NotebookLM notebook of the Rebbe's Torah
   checked: the passage was read in the book itself before use (...)
```

From its certainty report:

```
Candle lighting 17:49 <- own table row 2026-10-16 "נח"; Hebcal says 17:48 (gap +1 min, limit 3).
Shabbat ends 18:44 <- own table row 2026-10-16 "נח"; Hebcal says 18:43 (gap +1 min, limit 3).
[rule] friday/mincha = 17:45: candle lighting 17:49, rounded down to 5 min, not after 19:00 -> 17:45
[rule] shabbat/mincha = 17:15: Shabbat ends 18:44 - 90 min, rounded nearest to 15 min, not after 18:45 -> 17:15
[rule-held] weekdays/mincha = 17:45: sunset Sunday 18:07 - 25 min, rounded down to 15 min, not after 19:15 -> 17:30; HELD at last approved 17:45: a 25-min service starting then ends by 18:10, within 5 min of sunset Sunday
[rule] weekdays/arvit = 18:35: nightfall Sunday (sun 7.083 degrees down) 18:36, rounded down to 5 min -> 18:35
[carried] shabbat/shacharit_early = 05:20: copied from the approved message of 2026-10-09
For approval: weekdays/arvit changes this week: 18:40 -> 18:35 (-5 min).
```

Candle lighting and Shabbat ends come from the local Rav's printed luach
(kept as a table), cross-checked against Hebcal; early Shacharit is the
community's last approved time. The luach and the saved times stay on the
shliach's computer and are not in the repository. Every time matches, to the
minute, what the community's own private agent produces for the same
Shabbat. Run without them (`--config examples/eilat.json 2026-10-16`), the
agent uses Hebcal (17:48 / 18:43), says so in the report, and marks the
hand-set times as suggestions for approval.

### English: New York, USA, Friday 16 October 2026

```
python tools/build_message.py --config examples/new-york.json 2026-10-16
```

```
*Parshas Noach*

🕯️ Shabbos times – New York:
Candle lighting: 5:56 pm
Shabbos ends: 6:53 pm

📍 Davening times – Chabad House

Friday:
Mincha & Kabbalas Shabbos: 5:55 pm

Shabbos:
Chassidus class: 9:00 am
Shacharis: 10:00 am
Mincha: 5:40 pm

⏰ Weekdays:
Shacharis (Sun): 8:00 am
Shacharis (Mon-Fri): 7:00 am

Mincha & Maariv: 6:00 pm

Good Shabbos!
```

Candle lighting and Shabbos ends are Hebcal's values for New York City
(geonameid 5128581), checkable at
https://www.hebcal.com/shabbat?cfg=json&geonameid=5128581&date=2026-10-16&b=18&M=on .
The davening times come from the example rules in `examples/new-york.json`
(for instance Mincha = candle lighting rounded down to 5 minutes); they show
how rules work and are not the schedule of a real shul. The thought for
Shabbat is off in this example: there is no English text for it, and the
agent does not machine-translate.

## The prompt / workflow

Tools: **Claude Code or Codex** (open the folder, type "I want to start" or
"אני רוצה להתחיל"); the **Hebcal API** (free, no key); for the optional
thought, the **Torah MCP** (https://mcp.shluchimexchange.ai/) or the
shliach's own notebook of the Rebbe's Torah, always followed by reading the
passage itself. No Claude Code? `PASTE-PROMPT.md` does the same job in
ChatGPT, Claude or Gemini with web search.

The start of `AGENTS.md`:

```
# Weekly Shabbat Message Agent

You prepare one thing: the weekly Shabbat-times message of one Chabad House,
in the languages set in config.json (Hebrew, English, French). The shliach or
shlucha reads the draft, approves or corrects it, and sends it. You never send.

Activation: when the user writes `I want to start` or `אני רוצה להתחיל`,
follow START_HERE.md. For the weekly run, follow WORKFLOW.md.

## The three lines that are never crossed

1. Nothing is sent anywhere. Not to a WhatsApp group, a mailing list, an
   email, a bot, or any person other than the user in this chat. Not in a
   scheduled run either: a scheduled run prepares the draft and stops.
2. No number is invented. Every time in the message has a source you can
   name: the community's own zmanim table, Hebcal, a rule in config.json, a
   fixed time in config.json, or a time the user approved last week. If there
   is no source, the line shows [MISSING] and you say what is needed.
3. Stop and ask instead of guessing when: a holiday or fast falls in the
   week; the clocks change; the own table and Hebcal differ by more than the
   limit (3 minutes by default); a parasha, special Shabbat or month name is
   not in data/names.json; a time from an outside source (poster, photo,
   message) does not fit its cross-check; any data is missing.
```

Full agent: https://github.com/eilatchabad-ai/shluchim-ai-tools/tree/main/shabbat-message

## Sources

- **Hebcal** (hebcal.com), Jewish calendar REST APIs: Shabbat times
  (`/shabbat`), Zmanim (`/zmanim`, including Sunday sunset and nightfall at
  7.083 degrees for the weekday rules), Jewish calendar (`/hebcal`) and date
  converter (`/converter`). Every run prints the exact URLs it used. Hebcal
  content is licensed CC BY 4.0.
- **Default davening rules**: measured against 123 real weekly messages of
  the Chabad shul in Eilat, January 2024 to August 2026, plus the weekday
  rules the community set in October 2026; the statistics are in `RULES.md`,
  the messages themselves are not published.
- **The thought for Shabbat** in the Hebrew sample: Torat Menachem –
  Hisvaaduyos 5743, vol. 1, Shabbos Parshas Noach (unedited), pp. 426–427,
  drawing on the Baal Shem Tov's reading of "בא אתה וכל ביתך אל התבה"
  (Genesis 7:1; תיבה = a word of Torah and prayer). Found through a
  NotebookLM notebook of the Rebbe's Torah and checked by the author by
  reading the passage itself. The verse wording was checked against the
  text of Genesis on Sefaria; the passage in Torat Menachem was not
  re-checked by the tool.
- **Nisan closing line** in the Eilat example: ״בניסן נגאלו, בניסן עתידין
  ליגאל״, Talmud Bavli, Rosh Hashanah 11a (the view of Rabbi Yehoshua),
  checked against the Talmud text on Sefaria.
- **Torah MCP**: tested on 12 October 2026, after the author signed in. The
  short query "בא אל התיבה", limited to Likkutei Sichos, returned the Baal
  Shem Tov's reading in Likkutei Sichos vol. 1, Parshas Noach, sicha 1, in
  Yiddish: "מען זאל אריינגיין אין די אותיות פון תורה און תפלה". This gives
  the first half of the sample thought an edited source. The second half
  ("Noach did not go in alone") comes from the Torat Menachem passage above.
  The MCP gave no page number, and longer queries timed out; WORKFLOW.md
  step 4 now carries those lessons.
