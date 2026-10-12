# Privacy check

This folder is a public, generalized version of a private agent built for one
community in Eilat. This file records what was left out and the check that
was run before publishing.

## Not carried over from the private agent

| Item in the private agent | What happened |
|---|---|
| Archive of 123 real weekly messages | Removed. Only statistics remain, in `RULES.md`, with no message text |
| Table of the times in those messages | Removed |
| The community's yearly zmanim table (a transcription of the local Rav's printed luach) | Removed. Each community supplies its own; `data/my-*.csv` is git-ignored |
| Saved state (last week's approved times) | Removed. `data/state*.json` is git-ignored and created only by `--save` |
| Hebcal cross-check cache and sunrise cache for the archive dates | Removed (rebuilt live from Hebcal) |
| Memory, run log and user-profile files | Removed, contents not copied |
| Integration notes (a messaging-service setup and a mail connector) | Removed. The public agent has no sending channel at all |
| Local permission settings of the private agent | Removed |
| The name of the shul and of every person mentioned in the private files (the user, a congregant, the local Rav) | Removed. The only name in this folder is the author credit |
| A user quote explaining the summer floor | Replaced by a neutral sentence in `RULES.md` |
| A closing line in quotation marks that paraphrased a Talmud passage | Replaced by the passage's exact wording with its source, checked against the Talmud text |
| Second pass (12 October 2026), against the current private agent: its saved state with the user's approval note, the corrections log with the user's own words, the run log, the yearly sunset table, and the holiday posters, schedules and their images for Rosh Hashanah, Yom Kippur, Hoshana Raba and Simchat Torah | Not copied. The rules learned from them were ported as configurable logic with neutral wording (`RULES.md` sections 4, 4a, 4b, 7a, 7b); sunset comes live from Hebcal |

Kept, because they carry no personal data: the davening rules and their
statistics, the French transliteration table for parasha and Yom Tov names,
the spelling preferences for a few parasha names (as `title_overrides` in
`examples/eilat.json`), and one example thought file
(`examples/thought-noach-5787.json`) with its published source. The shul's
name is not used in the Eilat example (it reads "בית חב״ד").

There are no API keys, tokens or passwords anywhere: Hebcal needs none, and
the Torah MCP signs in through the user's own client.

## Final check

Run from inside `shabbat-message/` on 12 October 2026 (again after the second
pass), over every file in the folder:

```
# phone-like digit runs (8+ digits, dates excluded)
grep -rnEo '(\+?[0-9][0-9 ()-]{7,}[0-9])' . | grep -vE '[0-9]{4}-[0-9]{2}-[0-9]{2}'
# e-mail addresses and handles
grep -rn '@' .
# messaging services, keys, donors
grep -rniE 'whatsapp|callmebot|gmail|api[_ -]?key|token|password|parnas|donor' .
# every personal name and the shul name from the private agent
grep -rniE '<the names, kept off this public page>' .
```

Results of the final run (every hit, with why it is fine):

| Check | Hits | Verdict |
|---|---|---|
| Phone-like numbers | 2: `RULES.md` line 6 and this file, both "2026 (122", a year followed by a count | Not a phone number |
| `@` | 3: `CLAUDE.md` (`@AGENTS.md`, the Claude Code include line) and this file's own grep command and table | No addresses |
| Services, keys, donors | "WhatsApp" as a place the agent never sends to (`AGENTS.md`, quoted again in `SUBMISSION.md`) and as a text format (`OUTPUT_FORMAT.md`); this file's own sentences and grep command | No keys, no accounts, no donor or parnas names |
| Personal names and the shul name | 2: the author credit in `README.md` and `SUBMISSION.md` | Author credit only, as intended |

The names that do appear elsewhere are of the Torah sources themselves
(the Rebbe, the Baal Shem Tov, Rashi, Rabbi Yehoshua in the Gemara), not
of private people.

Test files written during development (saved state, the luach copy used for
the parity test, test configs and a mechanics-only thought file) were kept
outside this folder and are not part of it. `output/` contains only `.gitkeep`.
