# Start here

## 1. Open the folder in Claude Code (or Codex)

**Windows (PowerShell):**

```powershell
cd <path>\shabbat-message
claude
```

**Mac or Linux:**

```bash
cd <path>/shabbat-message
claude
```

For Codex, run `codex` instead of `claude` in the same folder. In the Claude
desktop app: open the `shabbat-message` folder itself (not the folder above it).

Then type in the chat, not in the terminal:

```
I want to start
```

or

```
אני רוצה להתחיל
```

## 2. What the agent does on "I want to start"

All of this is read-only until you approve:

1. **Checks Python.** Windows: `python --version`. Mac/Linux:
   `python3 --version`. Needs 3.8 or newer. If missing: install from
   python.org and tick "Add Python to PATH". No libraries are needed.
2. **Checks `config.json`.** If it is still the template, the agent asks you,
   one question at a time:
   - the community's name and city, in each language you want
     (Hebrew, English, French);
   - the city for Hebcal; the agent finds the number with
     `python tools/build_message.py --find-city "<city>"` and shows you the
     matches to choose from;
   - candle-lighting minutes before sunset (18 is common; Jerusalem 40;
     follow your Rav);
   - when Shabbat ends: nightfall at 8.5 degrees (Hebcal's default), or a
     fixed number of minutes after sunset;
   - every davening time: is it fixed (e.g. Shacharis 10:00), a rule (e.g.
     Mincha = candle lighting rounded down to 5 minutes), or set by hand each
     week (then it is carried from the last approved week);
   - whether you have the Rav's printed luach as a table (it then becomes the
     authority and Hebcal only the cross-check; format in
     `data/own-table.template.csv`);
   - whether to turn on the optional "thought for Shabbat" from the Rebbe's
     Torah (needs the Torah MCP or your own notebook of the Rebbe's Torah,
     see below).
3. **Shows you the filled `config.json`** and waits for a yes before saving it.
4. **Runs the first draft** for the coming Friday and shows it with the
   certainty report. Nothing is sent.

## 3. Scheduling (optional)

A weekly reminder can be set up in the host (for example a Claude Code
scheduled task on Friday morning). The scheduled prompt is:

```
Prepare this week's Shabbat message by WORKFLOW.md. Show the drafts and the
certainty report. Send nothing and save nothing. If there is a blocker, show
it first and stop.
```

A schedule written in a file is not a schedule. Only what the host shows as
registered is active; ask the agent to list the registered tasks to check.

## 4. Sources for the optional thought for Shabbat

The Torah MCP at `https://mcp.shluchimexchange.ai/` asks you to sign in.
In Claude Code:

```
claude mcp add --transport http torah https://mcp.shluchimexchange.ai/
```

then type `/mcp` inside Claude Code and sign in. In Codex, add the same URL
as a remote MCP server in the Codex MCP settings.

To check that it works, open a NEW session (a session started before the
sign-in does not load the server) and ask it to list the tools of the server
named `torah`, then to search `בא אל התיבה` in Likkutei Sichos. Short
queries work and long ones time out; see WORKFLOW.md step 4.

A notebook of the Rebbe's Torah that you keep yourself (for example in
NotebookLM) can be used to find an idea too. Whatever the search tool, the
passage is then read in the book itself before it is used: a notebook once
attributed Rashi's words to the Rebbe. Without any of these, everything else
works; the thought paragraph is simply left out and the report says why.

## Always needs your separate approval

- Saving a week (`--save`)
- Any change to `config.json` or to your own zmanim table
- Sending the message anywhere: you do that yourself

---

## בעברית, בקצרה

יש לפתוח את התיקייה `shabbat-message` ב-Claude Code (הפקודה `claude` בתוך
התיקייה) או ב-Codex, ולכתוב בצ׳אט: **אני רוצה להתחיל**.

הסוכן בודק שפייתון מותקן, ממלא איתך את `config.json` בשאלה אחת בכל פעם
(שם הקהילה, העיר, דקות הדלקת נרות, זמני התפילות), מציג את הקובץ לאישור,
ומכין טיוטה ראשונה לשבת הקרובה עם דוח ודאות. שום דבר לא נשלח ושום דבר לא
נשמר לפני אישור מפורש. ב-Windows הפקודה היא `python`, ב-Mac ובלינוקס
`python3`.
