# Privacy check

The bot this folder describes is private. It handles real payments, receipts and family records. Before publishing, we checked that nothing here identifies a person, an account or a system.

## What we left out

| Left out | Why |
|---|---|
| **All source code**, including the WhatsApp edge (the Cloudflare Worker) | The edge is small and fairly generic, but on its own it does nothing. It forwards every message to our private app, through an interface that only that app implements. It also contains our institution's contact address and our own Hebrew system messages. A cleaned copy would be code no one can run without rebuilding the app behind it. Instead, [`HOW-WE-BUILT-IT.md`](HOW-WE-BUILT-IT.md) describes the design so a developer can rebuild the edge in a day. |
| Configuration files, environment files, the database schema | They hold or name account IDs, database IDs and secret names. |
| Internal tool names and the bot's own system prompt | The prompt in [`PROMPT.md`](PROMPT.md) is a new text, written from the real one's rules. It doesn't copy the real prompt's tool names, internal fields or vendor names. |
| Domain names, endpoint URLs, app and account IDs, the test phone number | Identifiers of the private system. |
| The names of the database, receipt and payment vendors | Identifiers of the private system. The write-up says "our app", "the payment provider", "the receipt system". |
| Names of shluchim, donors and families, amounts, receipt numbers, dates of specific payments | Personal data. The status notes we worked from contain some of these. None of it was copied. |
| Email addresses and phone numbers | Personal data. The facts template uses `<placeholders>`. |

What *is* named: the author (Mendel Slonim, Chabad Eilat), public products (Claude, the Anthropic API, the WhatsApp Cloud API, Cloudflare Workers and D1), and the public Torah MCP address. The name "David Cohen" in [`TESTS.md`](TESTS.md) is an invented example of a request for someone else's receipt. It is not a real donor. The sample facts in `TESTS.md` (an example city, an example street and times) are labeled as made up.

## The screenshots

The three images in [`screenshots/`](screenshots/) are real conversations with our bot. Before publishing:

- **Hidden:** the two draft page links, the names and mobile numbers of the mikvah attendants and of the person responsible for the mikvaos, and the photographed sign, which also shows those numbers and is blurred.
- **Left visible on purpose:** the public phone numbers of the mikvaos, the branch names, and the event's invitation text and prices.
- **Not included:** a fourth screenshot of the receipt lookup. Even redacted, it showed a real donation by another person.

## The searches we ran

We ran these on every `.md` file in this folder except this one (this file lists the patterns themselves, so it always matches). We used `grep -rniE`, case-insensitive, on 12 October 2026.

| Pattern | Looking for | Result |
|---|---|---|
| `05[0-9]` | Israeli mobile numbers | **0 matches** |
| `972` | Israeli country code | **0 matches** |
| `\+[0-9]{6,}` | international phone numbers | **0 matches** |
| `[0-9]{7,}` | any long number (IDs, phones, accounts) | **0 matches** |
| `@` | email addresses | **0 matches** |
| `chabad\.onl` | our private site's domain | **0 matches** |
| `supabase` | database vendor and project IDs | **0 matches** |
| `jaffa` | receipt and CRM system | **0 matches** |
| `cardcom` | payment provider | **0 matches** |
| `vercel`, `workers\.dev` | hosting domains | **0 matches** |
| `gmail`, `555` | the office mailbox and Meta's test number | **0 matches** |
| `wa_contacts`, `branches\.authorized`, `/api/` | internal table names and endpoint paths | **0 matches** |
| `Bearer` | auth headers | **0 matches** |
| `account_id` | Cloudflare and Meta account IDs | **0 matches** |
| `token` | secrets | **2 matches**, both in `HOW-WE-BUILT-IT.md`, both the sentence "the WhatsApp token never leaves the edge". This is a design principle, not a value. |
| `secret` | secrets | **3 matches**, all in `HOW-WE-BUILT-IT.md`: "shared secret" twice in the diagram, and "shared-secret gates" once. They describe a mechanism, not a value. |
| `NIS`, `₪`, `shekel` | amounts | **0 real matches.** The case-insensitive search for `nis` matched the word "va**nis**hed". |
| Surnames of our branch operators and of the donor in our test notes, in English and Hebrew | personal names | **0 matches** |
| `Slonim`, `Mendel` | author name | 2 matches, the author line in `README.md` and in `SUBMISSION.md`, as intended |
| `http` | any URL | 4 matches, all `https://mcp.shluchimexchange.ai`, the public Torah MCP |

To repeat the check yourself:

```bash
cd chabad-house-assistant
grep -rniE '05[0-9]|972|\+[0-9]{6,}|[0-9]{7,}|@|chabad\.onl|supabase|jaffa|cardcom|bearer|account_id' \
  --include=*.md --exclude=PRIVACY-CHECK.md .
```

It should print nothing.
