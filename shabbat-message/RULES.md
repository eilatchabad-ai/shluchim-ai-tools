# Default rules and the evidence behind them

The davening rules in `examples/eilat.json`, and the defaults in the
`config.json` template, come from one real community: the Chabad shul in
Eilat, Israel. They were measured against **123 real weekly Shabbat messages**
sent between January 2024 and August 2026 (122 usable for the rules), with
sunrise for each date taken from Hebcal (geonameid 295277).

The messages themselves are not in this repository. Only the statistics are.

These are **examples, not halacha**. Every community sets its own times with
its Rav. The point of this file is to show what "a rule verified against the
archive" looks like, so you can do the same for yours.

---

## 1. Friday Mincha

**Rule:** candle lighting, rounded **down** to 5 minutes, **not after 19:00**.

```json
{"from": "candle", "offset": 0, "round_to": 5, "round": "down", "not_after": "19:00"}
```

| Measure | Result |
|---|---|
| Exact | 96 / 122 = 78% |
| Within 5 minutes | 120 / 122 = 98% |
| 2026 only | 29 / 33 = 87% |

The 19:00 cap is real: in June and July candle lighting in Eilat is
19:18 to 19:25, and Mincha stayed at 19:00 in all of those weeks.

## 2. Shabbat Mincha

**Rule:** Shabbat ends minus 90 minutes, rounded to the **nearest** quarter
hour, **not after 18:45**.

```json
{"from": "havdalah", "offset": -90, "round_to": 15, "round": "nearest", "not_after": "18:45"}
```

| Measure | Result |
|---|---|
| Exact | 102 / 122 = 83% |
| Within 15 minutes | **122 / 122 = 100%** |
| 2026 only | 23 / 33 = 69% |

Other offsets were tested; 90 was best in every window:

| Offset | Whole archive | Last 12 months | 2026 only |
|---|---|---|---|
| **90** | **83%** | **75%** | **69%** |
| 95 | 70% | 73% | 69% |
| 100 | 54% | 61% | 63% |
| 105 | 20% | 32% | 42% |

## 3. Early Shacharit on Shabbat: carried, not computed

The early minyan ("Shacharit at netz") is **not** at sunrise. Sunrise in
Eilat runs 05:40 to 06:44 over the year; the published time ran 04:30 to
05:30. It is a start time set by hand.

| Method | Exact |
|---|---|
| Best formula found (sunrise − 70, rounded to 5, floor 04:45, move only on an 8-minute drift) | 43% (77% within 5 minutes) |
| **Copy last week's time** | **71%** |

So the agent copies last week's approved time (`carry`) and uses sunrise only
to raise a flag when the gap drifts by 8 minutes or more (`watch`,
`alert_minutes`). The formula is used only as a first-week *suggestion* that
the user must approve.

**Summer floor 04:45:** in 18 of the 21 June–July Shabbatot over three years
the time was 04:45 (once 04:40, twice 04:50), though sunrise − 75 would have
given 04:25–04:45. The community's reason: earlier is too early for people.

## 4. Weekday Mincha: from Sunday's sunset, in quarter hours, with a hold

For most of the archive, weekday Mincha was carried by hand from week to
week, and no rule matched it well. That changed after a carried time went
out **an hour wrong**: summer values carried into the autumn (section 7a).
The community then set a rule (October 2026):

**Rule:** sunset on the Sunday after Shabbat, minus 25 minutes, rounded
**down** to the quarter hour, not after 19:15. Mincha takes about 25 minutes,
and it should end about at sunset, not too late.

```json
{"from": "sunset_sun", "offset": -25, "round_to": 15, "round": "down", "not_after": "19:15",
 "hold": {"duration": 25, "end_within": 5}}
```

**The hold:** when the rule moves the time earlier, last week's approved time
is kept as long as a Mincha starting then still ends within 5 minutes after
Sunday's sunset. So the time moves every two to four weeks instead of every
week (simulated over 5787: from November to January it stays at 16:15). The
hold is never applied across a clock change.

**Step size matters.** Three Minchas, two step sizes:

| | Multiple of 15 | Multiple of 5 |
|---|---|---|
| Shabbat Mincha | **100%** (123 / 123) | 100% |
| Weekday Mincha | **87%** (95 / 109) | 100% |
| Friday Mincha | 60% | **100%** |

Shabbat and weekday Mincha move in quarter hours; only Friday Mincha moves
in 5 minutes, because it follows candle lighting. Mixing them up costs about
30 points of accuracy.

**The cap is 19:15, not 19:00.** An earlier candidate (candle lighting
rounded to the nearest quarter hour, cap 19:15) matched 73% of 107 weeks
exactly and 100% within 15 minutes; with a 19:00 cap the same rule fell to
44%. The difference between weekday and Friday Mincha in the archive had two
peaks, 0 (46 weeks) and +15 (24 weeks), and all 24 of the +15 weeks were May
to August: Friday Mincha stops at its 19:00 cap, weekday Mincha goes on to
19:15. The second peak is the cap, not a season.

The new rule is earlier on purpose than most of the archive: about 40% exact
against it, 100% within a quarter hour. The difference is the earlier
ending the community asked for. In a clock-change week Sunday's sunset is
already on the new clock, so the rule moves by itself.

## 4a. Weekday Arvit

**Rule (approved October 2026):** nightfall on Sunday, sun 7.083 degrees
below the horizon, rounded down to 5 minutes.

```json
{"from": "tzeit_sun", "offset": 0, "round_to": 5, "round": "down"}
```

It moves 5 to 10 minutes at a time. Before this it appeared only in summer
(28 of its 29 archive appearances were May to August), as Mincha + 45 in 14
of 29 weeks, + 50 in 9 and + 55 in 6.

## 4b. A time from outside is checked like any other value

Once, weekday Mincha and Arvit were taken from the shul's printed poster
without a check. Both were 35 minutes off together: the poster was
consistent with itself (50 minutes between them), so nothing looked wrong.
In all 108 archive weeks weekday Mincha was within 10 minutes of Friday
Mincha, never 35; with the new rule the gap over 5787 stays within -15 to
+20, except in a clock-change week.

So the Eilat example has a cross-check, and a `--set` value is always
compared with its rule:

```json
"cross_check": {"with": "friday/mincha", "max_minutes": 20}
```

A printed source is not more right than a computed one.

## 5. Fixed times

| Time | Value | Evidence |
|---|---|---|
| Shabbat second Shacharit | 08:30 | 104 / 105 |
| Weekday second Shacharit | 08:00 | 108 / 108 |
| Weekday early Shacharit | 06:00 | 101 / 108 (four weeks at 06:15 in Elul 2025) |

## 6. How good is Hebcal against a Rav's printed luach?

Hebcal against the 123 published messages (whose times came from the local
Rav's luach):

| | Same minute | Within 1 minute |
|---|---|---|
| Candle lighting | 88 (71%) | 121 (98%) |
| Shabbat ends | 47 (38%) | 111 (91%) |

Good enough to catch a mistake of several minutes. Not good enough to be the
authority where a local luach exists. That is why the own table, when there
is one, decides, and Hebcal checks it (limit: 3 minutes).

## 7. The mistake the checks are built to catch

One message in the archive went out with Friday Mincha **an hour late**
(17:35 while candle lighting was 16:35) and early Shacharit 83 minutes
before sunrise instead of the usual ~60. Daylight saving had ended five days
earlier; last week's numbers were copied without moving them back an hour.
A correction had to be sent after the message.

Three checks in the script catch this:

- own table against Hebcal: more than 3 minutes apart stops the run, and a
  gap near 60 minutes is named as a probable clock change;
- the UTC offset saved with last week's approved times: if it changed,
  every carried time must be confirmed;
- the gap between sunrise and the carried early Shacharit: a jump of 8
  minutes or more is flagged.

## 7a. Carried times go stale with the seasons

The largest mistake the agent itself produced: a Shabbat message in
September went out with weekday Mincha 18:45 and Arvit 19:35, carried
unchanged from August. The right times were an hour earlier. Since then a
carried time unchanged for more than three weeks (`carry_max_age_days`,
default 21) gets an explicit WARNING above the draft, not only the quiet
"carried" mark, and weekday Mincha and Arvit are computed instead of carried.

## 7b. A Yom Tov that is also Shabbat

A Yom Tov that begins Friday and ends on Shabbat (Sukkot, Shemini Atzeret,
Shabbat Chol HaMoed in Israel) has the same candle lighting and the same end
as any Shabbat, so the Shabbat rules apply unchanged; only the title changes.
On the four archive Shabbatot that were also Yom Tov, Shabbat Mincha matched
the rule twice and was 15 minutes earlier twice: no pattern yet, so the rule
is not changed and the report asks for confirmation on such a Shabbat. Yom
Tov evening times (Arvit, Kiddush, Hakafot) do not shift by the change in
sunset from year to year: when it was tried, they were wrong. Ask instead.

## 8. Acceptance test, all of 2026

Running the Friday and Shabbat rules over the 33 Shabbatot of 2026, with real
week-to-week carry-over:

| Time | Exact | Within tolerance |
|---|---|---|
| Friday Mincha | 29 / 33 = 87% | 33 / 33 = 100% (±5 min) |
| Shabbat Mincha | 23 / 33 = 69% | 33 / 33 = 100% (±15 min) |
| Early Shacharit (carried) | 19 / 31 = 61% | 29 / 31 = 94% (±5 min) |

The two misses in early Shacharit are exactly the two weeks the time was
moved, which is what the drift flag is for.

## 9. Rosh Chodesh in the title

An early version added every Rosh Chodesh Hebcal returned for the coming
days to the title, and produced "Bereshit / Rosh Chodesh Cheshvan" for a
Shabbat when Rosh Chodesh was on Sunday. The rule now: Rosh Chodesh enters
the title only when it falls on Shabbat itself (the only two archive messages
with Rosh Chodesh in the title were both of that kind); otherwise it is
reported for a decision.
