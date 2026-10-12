# What the message looks like

One message per language in `config.json`. The languages are separate
messages, not translations of each other: a line can be limited to some
languages with `"languages": ["he"]` on that time in `config.json`. Labels are
never machine-translated: a missing label for a language is a blocker.

The text uses WhatsApp formatting (`*bold*`, `_italic_`) and is meant to be
pasted as is.

## Hebrew

```
שבת פרשת <name>[ / <special Shabbat>][ / ראש חודש <month>]
[שבת מברכים חודש <month>]

🕯️ זמני שבת – <city>:
הדלקת נרות: HH:MM
צאת השבת: HH:MM

📍 זמני תפילות – <community>

ערב שבת:
<label>: HH:MM

שבת קודש:
<label>: HH:MM
...

⏰ ימי חול:            (חול המועד: when Chol HaMoed days follow)
<label>: HH:MM
...

[✨ מחשבה לשבת
<up to 3 short lines, no source>]

שבת שלום!            (חג שמח ושבת שלום! in Chol HaMoed, from closing.chol_hamoed)
[<Elul line>]
[<Rosh Chodesh line>]
[<Nisan line>]
```

## English

```
*Parshas <name>[ | <special Shabbos>][ | Rosh Chodesh <month>]*
[Shabbos Mevorchim Chodesh <month>]

🕯️ Shabbos times – <city>:
Candle lighting: 5:56 pm
Shabbos ends: 6:53 pm

📍 Davening times – <community>

Friday:
<label>: <time>

Shabbos:
<label>: <time>

⏰ Weekdays:
<label>: <time>

[✨ A thought for Shabbos
<up to 3 short lines, no source>]

Good Shabbos!
```

`english_style: "sephardic"` writes Parashat / Shabbat instead of
Parshas / Shabbos. `clock.en: "12h"` gives 5:56 pm; `"24h"` gives 17:56.

## French

Follows the model the Eilat community uses: no emoji, no Mevarchim line.

```
_*Chabat <name>[ - <special>][ - Roch Hodech <month>]*_

*Horaires à <city>*

Allumage des bougies de Chabat : 17h49
Sortie du Chabat : 18h44

Horaires des tfilot à <community>

*Vendredi :*
<label> 17h45

*Chabat :*
<label> 8h30

*Jours de semaine*
<label> 6h00

Chabat chalom !
```

French parasha names follow `data/names.json` (ch for shin, h for chet, no
apostrophes). They come from one community's usage and should be checked
locally; correct them through `title_overrides.fr`.

## The thought for Shabbat (optional)

A titled paragraph of at most 3 short lines before the closing, for a
traditional Jew with no background in Chassidus: one line of background on
the parasha, then the idea, every step explained. **No source in the
message.** The full source (book, volume, sicha or section, page, how it
was checked) is printed under the draft for the shliach only. A language
with no lines in the thought file simply has no paragraph; nothing is
machine-translated. Example, Noach 5787:

```
✨ מחשבה לשבת
ה' הביא מבול על העולם, ונח ומשפחתו ניצלו בתיבה. "תיבה" היא גם מילה, ולכן הבעל שם טוב מסביר: כשסוער סביבנו, נכנסים אל המילים של התפילה והתורה.
והרבי מוסיף: נח לא נכנס לבד. גם אנחנו מביאים איתנו את כל מי שסביבנו, ואפילו את מי שנראה רחוק.
```

## A Yom Tov that is also Shabbat

A one-day Yom Tov that begins Friday night and ends on Shabbat night (in
Israel: Sukkot, Shemini Atzeret / Simchat Torah, Shabbat Chol HaMoed, the
seventh day of Pesach, Shavuot) is a Shabbat for every time rule: same
candle lighting, same end, same Mincha rules. It gets a normal message with
a Yom Tov title from `data/names.json` (`yom_tov_shabbat`), for example
`שבת חג הסוכות`. When Chol HaMoed days follow, the weekday block is headed
`חול המועד` / `Chol HaMoed` / `Hol Hamoed`, and `closing.chol_hamoed`
replaces the usual closing. Yom Tov additions (Hakafot, Yizkor) are not
built. Yom Kippur and Rosh Hashanah are never treated this way, and a
two-day Yom Tov stops the run.

## The title rules

- **Rosh Chodesh** goes in the title only when it falls on Shabbat itself.
  When it touches the weekend without falling on Shabbat, the report says so
  and leaves the decision to the user. (In the Eilat archive, the only two
  messages with Rosh Chodesh in the title were both Rosh Chodesh on Shabbat.)
- **Mevarchim** gets its own second line, and does not by itself add a
  "Chodesh Tov" closing.
- **Special Shabbatot** (Shuva, Shirah, Shekalim, Zachor, Parah, HaChodesh,
  HaGadol, Chazon, Nachamu) come from Hebcal and are added after the parasha.

## Closing lines

From `closing` in `config.json`, each optional and per language:

| Key | When it is added |
|---|---|
| `always` | Every week |
| `elul` | When Shabbat is in Elul |
| `rosh_chodesh_on_shabbat` | When Rosh Chodesh is on Shabbat itself |
| `nisan` | When Shabbat is in Nisan (after a blank line) |

The Eilat example's Nisan line is the Gemara's own wording with its source:
״בניסן נגאלו, בניסן עתידין ליגאל״ (ראש השנה יא, א), checked against the
text of the Talmud.

## The certainty report (never part of the message)

Printed after the drafts:

1. **Blockers**, first, if any: the draft must not be sent.
2. **Where the Shabbat times come from**: own table row and the gap to
   Hebcal, or "Hebcal is the SOURCE this week" when there is no own table.
3. **Each davening time** with its kind: `rule` (and the arithmetic),
   `rule-held` (the rule moved it earlier, but last week's time still fits
   the `hold` condition), `fixed`, `carried` (from which approved week),
   `suggested` (needs approval), or `set` (given by the user this week, and
   compared with the rule).
   Before the drafts: **WARNING** lines for a carried time unchanged for
   more than `carry_max_age_days`.
   Above the report: **the source of the thought**, for the shliach only.
4. **For approval**: notes that need a human decision.
5. **Every Hebcal URL** that was used, so anyone can check a number.

## When there is no result

If candle lighting or Shabbat ends has no valid source, the draft shows
`[MISSING]` in its place and the run is blocked. A message with a wrong time
is worse than no message.
