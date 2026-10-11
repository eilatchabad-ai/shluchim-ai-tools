# Chabad House Assistant

An assistant that answers people who write to your Chabad House on WhatsApp or through the website. It's for the tourist who wants to know when Mincha is, the neighbor who would never call a rabbi but will send a message at midnight, and the person who heard the word "Tanya" and is curious.

- **Times, address and events come only from facts you enter.** It never invents a time and never calculates one.
- **Torah and Chassidus questions get plain words and a real source**, through the [Torah MCP](https://mcp.shluchimexchange.ai/), with no quote unless it has a source. Without the MCP it still answers, but with no quote and no source, and it says that it couldn't check one.
- **"What should I do?" and "Is it allowed?" go to you.** It never gives a ruling, and every halachic question becomes a reason to talk to the shliach.
- **Money and personal data never go through the chat.** Donations go through your secure link. It never looks up or confirms anything about another person.

It comes from the WhatsApp bot we run at Chabad Eilat, with our private platform taken out.

## Files

| File | What it is |
|---|---|
| [`PROMPT.md`](PROMPT.md) | **The part to copy.** The full instructions in English and in Hebrew, setup in three steps, and why each rule is there. |
| [`facts-template.md`](facts-template.md) | The facts you fill in: davening times, this Shabbos, events, classes, the donation link, how to reach you. |
| [`TESTS.md`](TESTS.md) | Six conversations with the replies to expect. Run them before you share the number. |
| [`HOW-WE-BUILT-IT.md`](HOW-WE-BUILT-IT.md) | For a shliach with a developer: how our real WhatsApp bot is built, its three tiers, its safety rules, and what we learned. |
| [`PRIVACY-CHECK.md`](PRIVACY-CHECK.md) | What we removed before publishing this folder, and the searches we ran to check. |
| [`screenshots/`](screenshots/) | Three real conversations with our live bot: a voice note that becomes event pages, a photo that becomes saved facts, and a question answered from those facts. |
| [`SUBMISSION.md`](SUBMISSION.md) | Our promptathon entry text. |

## Start in five minutes

1. Fill in [`facts-template.md`](facts-template.md).
2. Paste the prompt from [`PROMPT.md`](PROMPT.md) into a Claude Project, a custom GPT, or your WhatsApp bot platform, with your facts where it says `PASTE YOUR FACTS HERE`.
3. Connect the Torah MCP: add `https://mcp.shluchimexchange.ai` as a connector and sign in with your shluchimexchange.ai account.
4. Run the conversations in [`TESTS.md`](TESTS.md).
5. Update "This Shabbos" in the facts every week.

## What it does not do

It doesn't send messages on its own, doesn't take payments, doesn't keep a donor list, and doesn't know who is writing. Those things need code that checks permissions on every call, and our real bot has it, as described in [`HOW-WE-BUILT-IT.md`](HOW-WE-BUILT-IT.md). A pasted prompt can't check permissions, so this version leaves all of them out.

---

## בעברית

עוזר שעונה למי שכותב לבית חב"ד בוואטסאפ או באתר: זמני תפילות, כתובת ואירועים, רק מתוך העובדות שהשליח מילא, ובלי להמציא או לחשב אף שעה. שאלה בתורה ובחסידות מקבלת תשובה במילים פשוטות עם מקור אמיתי דרך ה-Torah MCP, ובלי ציטוט כשאין מקור. כל שאלה של "מה לעשות" או "האם מותר" עוברת לשליח, ולעולם לא נענית על ידי העוזר. כסף ופרטים אישיים לא עוברים בצ'אט.

**איך מתחילים:** ממלאים את `facts-template.md`, מדביקים את הפרומפט בעברית מתוך `PROMPT.md` ל-Claude, ל-ChatGPT או לפלטפורמת הבוט, מחברים את ה-Torah MCP, ומריצים את שש השיחות שב-`TESTS.md`. את זמני השבת מעדכנים כל שבוע.

---

Mendel Slonim, Chabad Eilat. MIT License, see [`../LICENSE`](../LICENSE).
