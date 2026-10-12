# Shluchim AI Tools

Tools we built and use every week at Chabad Eilat, packaged so any Chabad House can install them, or paste the prompt, and get the same result.

| Folder | What it does | How to use it |
|---|---|---|
| [`chabad-house-assistant/`](chabad-house-assistant/) | A WhatsApp or website assistant for the Chabad House. It answers from facts you enter, quotes Torah sources through the Torah MCP, and sends any "what should I do" question to the shliach. | Paste [`PROMPT.md`](chabad-house-assistant/PROMPT.md) and fill in the facts template. |
| [`shabbat-message/`](shabbat-message/) | Builds the weekly Shabbat times message for your community: candle lighting, Shabbos ends and davening times, in Hebrew, English or French. It can add a short "thought for Shabbat" from the Rebbe's Torah, written in plain words. Every time and every source is real, and nothing is sent without your approval. | Open the folder in Claude Code or Codex and type "I want to start". You can also paste [`PASTE-PROMPT.md`](shabbat-message/PASTE-PROMPT.md) into ChatGPT, Claude or Gemini. |

Coming soon: shiurim turned into audio.

## The rules every tool here follows

- **It never invents a time, a fact or a source.** Missing data stops the tool, and the tool says what is missing.
- **It never sends anything on its own.** You see the draft first and decide.
- **It keeps no personal data.** There are no phone numbers, donor names or keys in this repository.

## ב״ה, בעברית

כלים שאנחנו משתמשים בהם בחב״ד אילת, ארוזים כך שכל בית חב״ד יוכל להתקין אותם או
להדביק את הפרומפט. בכל תיקייה יש הוראות בעברית ובאנגלית. יש לפתוח את התיקייה
ב-Claude Code ולכתוב "אני רוצה להתחיל".

---

Mendel Slonim, Chabad Eilat. Entered in the ChabadLabs Promptathon, *Chutzah*.
Released under the MIT License: free to use, copy and adapt.
