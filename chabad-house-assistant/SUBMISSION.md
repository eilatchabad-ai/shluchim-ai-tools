# Promptathon entry: Chabad House Assistant

**Entry title:** The Chabad House Assistant: a WhatsApp helper that answers from your facts, quotes only real sources, and sends every "is it allowed?" to the shliach

**Category:** Apps, tools and agents

**Author:** Mendel Slonim, Chabad Eilat

## What it is

An assistant for the Chabad House WhatsApp number or website chat. It answers davening times, Shabbos times, events and the address only from facts the shliach entered. It answers questions about Torah and Chassidus in plain words, with a real source through the Torah MCP, and it sends every practical halacha question to the shliach. It reaches people who would never call a rabbi but will send a WhatsApp message: tourists passing through Eilat, Israelis who have never walked into a Chabad House, and French, English and Russian speakers, who each get an answer in their own language.

## Output

Link: https://github.com/eilatchabad-ai/shluchim-ai-tools/tree/main/chabad-house-assistant/screenshots

Three real screenshots from our live bot, in Hebrew. Private names, private phone numbers and page links are hidden for publication. The mikvah phone numbers are public and were left in.

1. **A voice note becomes event pages.** A 26-second voice note about a first-night-of-Sukkos meal. The bot replies with two draft pages, one in Hebrew and one in French for the francophone Chabad House, plus a ready-to-forward invitation in both languages. It ends with "Say the word and I'll put them live", so nothing goes live without a person.
2. **A photo becomes saved facts.** A photo of a printed sign listing the city's mikvaos, with the note "Save this, it can help every Chabad House". The bot saves the facts, asks whether to copy them to the other branches, and writes a clean message to forward.
3. **A question answered from the facts only.** "Which mikvah is closest to the Dan hotel?" The bot answers from the saved list. It also says the full address isn't saved, so it should be checked before it is passed to a guest. It does not invent an address.

**What the live bot does today in Eilat.** One WhatsApp number serves three tiers, identified by the sender's phone number:

- **Shluchim of the Eilat branches** describe a donation or event page in a text or voice message, and the bot builds it as a draft, generates a cover image, and publishes it when asked. It also searches payments and donors, limited to their own branch. A live page changes only after a person sees the before/after and approves it in a later message.
- **The public tier** answers davening times, the address and hours only from what the shliach entered. It finds a person's own receipts by the number they are writing from, and never anyone else's.
- **The owner** gets everything above, plus a weekly Shabbos message queued until WhatsApp's 24-hour window opens.

Conversations are deleted after 90 days. The bot currently runs on Meta's test number, which delivers only to a small list of verified recipients, so today it serves the shluchim. The public tier is built and tested, but the general public can't reach it yet.

The Torah-question layer, which answers through the Torah MCP and refers halachic questions to the shliach, is new in the shareable version of this entry. It is not yet wired into our live bot.

## The prompt / workflow

The start of `PROMPT.md`:

```text
You are the assistant of {{CHABAD_HOUSE_NAME}}. You answer people who write to the Chabad House on WhatsApp or through the website chat. Most of them have never met the shliach. Some are tourists, some are neighbors who would never call a rabbi but will send a message late at night. Every answer should leave them feeling welcome and one step closer to something real: a minyan, a Shabbos meal, a class, a mitzvah, or a conversation with the shliach.

## 1. How to write: WhatsApp, not a document
- No Markdown ... Short. Two or three lines is a good answer ...
## 2. Facts about the Chabad House come only from FACTS
- Never invent, estimate or calculate a time ...
## 3. Torah and Chassidus questions: plain words, real sources
- If a Torah texts tool is connected (the Torah MCP), search it before you answer ...
- No quote without a source ...
## 4. "What should I do?" and "Is it allowed?" always go to the shliach
## 5. Money and personal data never go through this chat
...
```

Full prompt (English and Hebrew), facts template, six test conversations and an architecture write-up: https://github.com/eilatchabad-ai/shluchim-ai-tools/tree/main/chabad-house-assistant

**How to reuse it:** fill in `facts-template.md`, paste the prompt into a Claude Project, a custom GPT, or a WhatsApp bot platform, connect the Torah MCP, and run the six conversations in `TESTS.md`. You don't need to ask us anything.

**Tools used:**
- Claude, through the Anthropic API (the live bot; the prompt also works in a Claude Project or ChatGPT)
- WhatsApp Cloud API
- Cloudflare Workers (the WhatsApp edge in the live bot)
- Torah MCP from ShluchimExchange (https://mcp.shluchimexchange.ai/) for Torah and Chassidus sources

## Sources

- Every Torah or Chassidus source the assistant gives comes from the Torah MCP in that conversation. The prompt forbids quoting anything a tool didn't return, and forbids naming a sicha, maamar, chapter or page from memory. Without the MCP it gives no quote and no source, and says that it couldn't check one.
- The one source named in our test file (Tanya, Likkutei Amarim, chapters 1 and 2, where the two souls are introduced) is an example of the expected format, and anyone can check it in the Tanya.
- No source was invented for this entry.
