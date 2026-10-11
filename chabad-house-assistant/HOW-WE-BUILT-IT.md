# How we built the real bot

This is a write-up for a shliach who has a developer, or who is one. It describes the WhatsApp bot we run at Chabad Eilat. The system itself stays private because it touches real payments and personal data, so this document gives the design and the lessons, not the code. [`PROMPT.md`](PROMPT.md) is the part anyone can reuse without a developer.

Everything here is written from the code and its own status notes, as they stood in October 2026.

## What it does

One WhatsApp number talks to three kinds of people and tells them apart by the number they write from.

| Tier | How someone gets it | What it may do |
|---|---|---|
| **Public** | Any number we don't know. This is the default. | Prayer times, address and hours, only from what a shliach entered and never invented. Find *their own* payments and a link to the receipt, matched by the number they are writing from. Anything else is passed on to a person. |
| **Shliach** | A single-use, expiring join code issued by the owner | Build a donation or event page from a free-text or voice description, generate a cover image, check that payments are set up, publish and unpublish, search payments and donors, update the public branch info. **All of it limited to their own branches.** |
| **Owner** | The number is listed in the edge's configuration | Everything above, plus issuing join codes and reading the requests the bot logged. |

A shliach can send a voice note ("make a page for the Lag BaOmer bonfire, families, free, registration required") and get back a draft page link, and then "add a picture" and "put it live".

## How it's put together

```
  phone
    |
    v
  WhatsApp Cloud API (Meta)
    |   webhook, signed by Meta
    v
  +-----------------------------------------------------------+
  | EDGE: Cloudflare Worker (small, separate deployment)      |
  |  - verifies Meta's signature on the raw body              |
  |  - dedup on Meta's message id (Meta re-delivers)          |
  |  - looks up the tier (a cache, not the authority)         |
  |  - daily message cap for public numbers                   |
  |  - "received" acknowledgement for the slow tiers          |
  |  - splits long replies, proxies media files               |
  |  - holds the WhatsApp token. Nothing else does.           |
  |  - small SQLite (D1): message log, tier cache, counters   |
  +-----------------------------------------------------------+
    |   HTTPS + shared secret: { sender, tier, message, recent history }
    |   the app answers 202 at once and keeps working
    v
  +-----------------------------------------------------------+
  | BRAIN: our web app (the same one the shluchim use in      |
  | the browser)                                              |
  |  - agent loop with Claude (Anthropic API)                 |
  |  - tools offered by tier; every tool re-checks permission |
  |  - the same code paths the browser editor uses            |
  +-----------------------------------------------------------+
    |   HTTPS + a different shared secret: { to, text }
    v
  EDGE -> WhatsApp -> phone

  Scheduled job (e.g. the weekly Shabbos message for the owner)
    |   its own key, can address only the owner
    v
  EDGE: send now if the 24-hour window is open, otherwise queue
```

Why two parts: Meta wants a 200 within a few seconds and re-delivers anything that doesn't get one. Building a page with an AI can take a minute or more. So the edge only authenticates, acknowledges and forwards. The app answers "accepted" immediately and does the real work on its own time, then calls back to the edge to send the reply.

## The four principles

**1. The WhatsApp token never leaves the edge.** The app reads voice notes and photos through the edge's media proxy, not directly from Meta. Someone who breaks into the app still cannot send messages as the Chabad House number.

**2. The edge has no opinion on permissions.** It knows a number's tier only to decide how to greet it and when to throttle it. Who may do what is decided in the app, against the same permission list the browser admin uses. A shliach removed from a branch loses the bot's access to it in the same moment, with no second step.

**3. The bot has no permission the person writing to it lacks.** Every tool call re-checks the sender's rights against the record it touches, every time. An id that the model asks for is a request, not a permission. The public tier is shown only three read-only tools, and the dispatcher also refuses any tool that wasn't offered to the tier, even if the model asks for it by name. We test that by calling the tools directly as a public sender, not by trusting the model not to ask.

**4. Conversations are forgotten after 90 days.** A daily scheduled run deletes message history, delivery reports and per-number counters older than 90 days. The bot itself reads only the last 20 messages of a conversation, so keeping more only kept names, amounts and private questions around for no reason. The cleanup logs counts only, never a number or a text. The text of a scheduled message is blanked, but its key is kept, so that a retry of an old message is still refused and never sent twice.

## Two models, two budgets

A visitor asking "when is Mincha" needs a fast, cheap answer. A shliach building a page needs a stronger model. So the public tier uses a small model and a daily cap per number, and the expensive model is kept for people we have identified. A personal Claude subscription can't legally power a service that answers other people, so this runs on a pay-per-use API key, and the cap on the public tier is what keeps the bill predictable.

## What we learned, most of it the hard way

**The 24-hour window.** WhatsApp lets a business send free text to someone only within 24 hours of that person's last message. Outside the window Meta *accepts* the request and then silently does not deliver it. A weekly Shabbos message from a scheduled job would have vanished every week while reporting success. Messages for the owner are now queued and go out the moment the owner next writes to the bot, which reopens the window. The window is measured on Meta's timestamp for the owner's message, not on when we processed it, and we treat it as 23.5 hours so a send never races the edge of the window. The scheduled job's key can address only the owner, so a job that leaks its key, or is talked into something by a web page it read, can still only write to the owner. Every request carries a key, and the same key never sends twice. When a send's outcome is lost, it is marked "unknown" and never retried automatically. A duplicate Shabbos message is the one mistake that can't be taken back.

**"Accepted" is not "delivered".** Our send endpoint used to answer `ok` whatever Meta said. Meta's delivery reports were thrown away on arrival, so a message that failed left no trace. Now refusals are an error the caller can't misread, and delivery reports are stored.

**A failure message must look like a failure.** When the app was unreachable, the edge sent a polite Hebrew sentence right after "received", and we read it as the bot's answer. It now opens with an unmistakable failure marker.

**Log only what actually left.** The message log is the bot's memory. A reply recorded as sent that Meta refused made the bot "remember" saying things the person never saw.

**A live page changes only after a person approved it, in a later message.** Our bot once edited a donation page that was live and reported a change that never happened: the field it wrote to isn't even shown on that kind of page. Now any change to a live page shows a before/after and stops. The change runs only in a *different* agent run, which means only after a new message from a person. A model can't approve its own change. Pages are always created as drafts.

**"Not found" must come from a search that actually ran.** The worst answer is "there's no such payment" from a search the model never made, because a person who hears "there isn't one" stops looking. The prompt forbids stating an absence without a tool result from this conversation. In code, a database error is returned as an error, never as an empty list.

**Someone else's payment gets the same answer as a missing one.** "That payment belongs to someone else" already tells the person that the payment exists.

**Identifiers lie.** A receipt number is not unique, because each receipt book is numbered on its own. A bank reference stored in the same column nearly fetched a *different person's real receipt* under the current donor's name, with no visible error. Never look something up by a number that only looks like the right kind of number.

**Removing an emoji reaction is a webhook too.** It arrives as a reaction with no emoji. Treating it as a message produced "received" followed by silence.

**Setup traps on Meta's side.** An app that isn't published gets no real data at all. The WhatsApp business account must be subscribed to your app, which is a hidden step that you can check through the API. The dashboard's "Test" button proves nothing. And the free test number delivers only to five verified recipients.

**Cover images.** Generated images are still-life only, with no people and no text, and a separate check runs before an image is placed on a page.

## Shabbos

Our bot does not have a Shabbos pause. It only replies and never starts a conversation, except for the scheduled message to the owner. Whether an automatic assistant should answer people on Shabbos, and what it should say if it doesn't, is a question for your Rav. If you add a pause, do it at the edge, and keep returning a 200 to Meta while paused, otherwise Meta queues the messages and delivers them all at once when you resume. Our edge's kill switch already works this way.

## Where it stands

- **Proven on the live system:** signature checking, the shared-secret gates, the full round trip from phone to app and back, separation between branches, voice transcription, and receipt lookup by phone. For the receipt lookup we wrote down the expected name and date before sending the request, and the same name and date came back.
- **Built and tested outside production:** the tier gate (public senders can't reach page tools), live-page confirmation, the owner-notification queue, and the 90-day retention.
- **Not yet public:** the bot runs on Meta's test number, which delivers only to a handful of verified recipients. The public tier is built and tested, but the general public can't reach it until we move to a real number.

## If you want to build your own

You don't need our app. The shortest working path:

1. A WhatsApp Cloud API number and a small webhook service (any serverless platform) that verifies Meta's signature, deduplicates on the message id, answers 200 at once, and rate-limits unknown numbers.
2. A call to Claude with [`PROMPT.md`](PROMPT.md) as the system prompt and your facts file inside it. Pass the last 10 to 20 messages of the conversation as history.
3. Optionally, the Torah MCP as a tool for the Torah questions. It signs in with a shluchimexchange.ai account, so check its own guide at chabadlabs.ai/torah-mcp for connecting it from code rather than from the Claude or ChatGPT apps. We have not wired it into our bot yet.
4. A daily job that deletes conversations older than the retention period you choose.

Add tools that touch payments or personal data only once permissions are checked in code on every call. A rule in the prompt is not a permission check.
