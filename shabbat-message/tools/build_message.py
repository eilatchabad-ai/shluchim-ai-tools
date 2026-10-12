#!/usr/bin/env python3
"""
Weekly Shabbat-times message builder for any Chabad House.

Run from the shabbat-message folder:

    python tools/build_message.py                         # coming Friday, config.json
    python tools/build_message.py 2026-10-16              # a specific Friday
    python tools/build_message.py --config examples/new-york.json 2026-10-16
    python tools/build_message.py --json                  # structured output
    python tools/build_message.py --find-city "Melbourne" # look up a Hebcal geonameid
    python tools/build_message.py --thought output/thought-2026-10-16.json
    python tools/build_message.py --save                  # ONLY after the draft was approved
    python tools/build_message.py --state PATH            # use another saved-times file
    python tools/build_message.py --table PATH            # use another own-zmanim CSV
    python tools/build_message.py --set weekdays/mincha=18:30   # a correction from the user

On Windows the command is `python`; on Mac/Linux it is usually `python3`.
Standard library only. Python 3.8 or newer.

This script never sends anything anywhere. It prints a draft and a
certainty report. Exit codes: 0 = clean draft, 2 = draft has blockers
(do not send), 3 = no draft could be built (config or data problem).
"""
import csv
import datetime
import json
import math
import os
import re
import sys
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = "shabbat-message-agent/1.1 (python-urllib; open-source Chabad tool)"
LANGS = ("he", "en", "fr")
MISSING = "[MISSING]"
SECTIONS = ("friday", "shabbat", "weekdays")

# Minor dates that never change a Shabbat message and are not even mentioned.
QUIET_MINOR = {"Rosh Hashana LaBehemot"}

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


class Stop(Exception):
    """No draft can be built. The message explains what is missing."""


# ------------------------------------------------------------------ helpers
def rel(path):
    if not path:
        return None
    return path if os.path.isabs(path) else os.path.join(ROOT, path)


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def to_min(hhmm_s):
    if hhmm_s is None or str(hhmm_s).strip() == "":
        return None
    h, m = str(hhmm_s).strip().split(":")
    return int(h) * 60 + int(m)


def hhmm(x):
    x = int(x)
    return f"{x // 60:02d}:{x % 60:02d}"


def norm(s):
    return (s or "").replace("’", "'").replace("‘", "'").strip()


def parse_iso(s):
    """'2026-10-16T17:48:00+03:00' -> (date 'YYYY-MM-DD', minutes, '+03:00')."""
    dt = datetime.datetime.fromisoformat(s)
    off = s[19:] if len(s) > 19 else ""
    return s[:10], dt.hour * 60 + dt.minute, off


def days_between(a, b):
    return (datetime.date.fromisoformat(b) - datetime.date.fromisoformat(a)).days


SOURCES_USED = []


def fetch(url):
    SOURCES_USED.append(url)
    last = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # network or JSON error
            last = e
            time.sleep(1 + attempt)
    raise Stop(f"Hebcal could not be reached ({url}): {last}. No times are shown "
               f"without a source. Check location.geonameid in the config and the internet "
               f"connection, then run again.")


def fmt_time(minutes, lang, cfg):
    if minutes is None:
        return MISSING
    style = cfg.get("clock", {}).get(lang, "24h")
    h, m = divmod(int(minutes), 60)
    if style == "12h":
        suffix = "am" if h < 12 else "pm"
        h12 = h % 12 or 12
        return f"{h12}:{m:02d} {suffix}"
    if style == "h":
        return f"{h}h{m:02d}"
    return f"{h:02d}:{m:02d}"


def round_to(x, step, mode):
    if not step or step <= 1:
        return int(x)
    if mode == "down":
        return int(math.floor(x / step)) * step
    if mode == "up":
        return int(math.ceil(x / step)) * step
    return int(math.floor(x / step + 0.5)) * step  # nearest, halves round up


# ------------------------------------------------------------------ config
def load_config(path):
    if not os.path.exists(path):
        raise Stop(f"Config file not found: {path}")
    try:
        cfg = load_json(path)
    except json.JSONDecodeError as e:
        raise Stop(f"{path} is not valid JSON: {e}")
    errs = []
    langs = cfg.get("languages") or []
    if not langs or any(l not in LANGS for l in langs):
        errs.append(f"'languages' must be a non-empty list drawn from {list(LANGS)}.")
    gid = (cfg.get("location") or {}).get("geonameid")
    if not isinstance(gid, int):
        errs.append("'location.geonameid' is not filled. Find it with: "
                    "python tools/build_message.py --find-city \"<your city>\"")
    for key in ("name", "city"):
        vals = (cfg.get("community") or {}).get(key) or {}
        for l in langs:
            v = (vals.get(l) or "").strip()
            if not v or v.upper().startswith("FILL"):
                errs.append(f"'community.{key}.{l}' is not filled.")
    b = cfg.get("candle_lighting_minutes")
    if not isinstance(b, int) or not (0 <= b <= 60):
        errs.append("'candle_lighting_minutes' must be a whole number of minutes before sunset "
                    "(18 is the common default; Jerusalem 40; ask the local Rav).")
    hv = cfg.get("havdalah") or {}
    if hv.get("mode") not in ("tzeit_8.5", "minutes") or (
            hv.get("mode") == "minutes" and not isinstance(hv.get("minutes"), int)):
        errs.append("'havdalah' must be {\"mode\": \"tzeit_8.5\"} or "
                    "{\"mode\": \"minutes\", \"minutes\": 50} (minutes after sunset).")
    if not isinstance(cfg.get("times"), dict):
        errs.append("'times' with 'friday', 'shabbat' and 'weekdays' lists is missing.")
    else:
        for section in SECTIONS:
            for item in cfg["times"].get(section, []):
                iid = item.get("id", "?")
                vals = [("fixed", item.get("fixed"))] if "fixed" in item else []
                if "carry" in item and (item["carry"] or {}).get("initial") is not None:
                    vals.append(("carry.initial", item["carry"]["initial"]))
                for k, v in vals:
                    try:
                        to_min(v)
                    except Exception:
                        errs.append(f"'times.{section}' item '{iid}': {k} is \"{v}\", not a time "
                                    f"like 08:30. Fill in the real time.")
                for r in (item.get("rule"), (item.get("carry") or {}).get("suggest")):
                    if r and r.get("from") not in BASE_NAMES:
                        errs.append(f"'times.{section}' item '{iid}': rule base '{r.get('from')}' "
                                    f"is unknown. Use one of: {', '.join(BASE_NAMES)}.")
    if errs:
        raise Stop("config is not ready:\n   - " + "\n   - ".join(errs))
    return cfg


# ------------------------------------------------------------------ Hebcal
def hebcal_week(cfg, friday):
    gid = cfg["location"]["geonameid"]
    fri = datetime.date.fromisoformat(friday)
    sat = (fri + datetime.timedelta(days=1)).isoformat()
    nxt = (fri + datetime.timedelta(days=7)).isoformat()
    hv = cfg["havdalah"]
    hv_q = "M=on" if hv["mode"] == "tzeit_8.5" else f"m={hv['minutes']}"
    sh = fetch(f"https://www.hebcal.com/shabbat?cfg=json&geonameid={gid}&date={friday}"
               f"&b={cfg['candle_lighting_minutes']}&{hv_q}&leyning=off")
    loc = sh.get("location", {})
    out = {"location": loc, "candle": None, "havdalah": None, "parasha": None,
           "special": [], "mevarchim": None, "roshchodesh": [], "saturday": sat}
    for it in sh.get("items", []):
        cat, when = it.get("category"), it.get("date", "")
        if cat == "candles" and when[:10] == friday:
            out["candle"] = parse_iso(when)
        elif cat == "havdalah" and when[:10] == sat:
            out["havdalah"] = parse_iso(when)
        elif cat == "parashat" and when[:10] == sat:
            out["parasha"] = norm(it.get("title", "")).replace("Parashat ", "", 1)
        elif cat == "mevarchim" and when[:10] == sat:
            out["mevarchim"] = norm(it.get("title", "")).replace("Mevarchim Chodesh ", "", 1)
        elif cat == "roshchodesh":
            out["roshchodesh"].append((when[:10], norm(it.get("title", "")).replace("Rosh Chodesh ", "", 1)))
        elif cat == "holiday" and it.get("subcat") == "shabbat" and when[:10] == sat:
            out["special"].append(norm(it.get("title", "")))

    il = "on" if loc.get("cc") == "IL" else "off"
    cal = fetch(f"https://www.hebcal.com/hebcal?v=1&cfg=json&geonameid={gid}&start={friday}"
                f"&end={(fri + datetime.timedelta(days=6)).isoformat()}"
                f"&maj=on&min=on&mod=off&nx=off&mf=on&ss=off&s=off&c=off&i={il}")
    out["holidays"] = [(it.get("date", "")[:10], norm(it.get("title", "")), it.get("subcat"))
                       for it in cal.get("items", []) if it.get("category") == "holiday"]

    zm = fetch(f"https://www.hebcal.com/zmanim?cfg=json&geonameid={gid}&start={friday}&end={nxt}")
    t = zm.get("times", {})
    for key, src in (("sunset", "sunset"), ("sunrise", "sunrise"), ("tzeit85", "tzeit85deg"),
                     ("tzeit7083", "tzeit7083deg")):
        out[key] = {d: parse_iso(v) for d, v in (t.get(src) or {}).items()}

    conv = fetch(f"https://www.hebcal.com/converter?cfg=json&date={sat}&g2h=1&strict=1")
    out["hmonth"], out["hday"] = norm(conv.get("hm", "")), conv.get("hd")
    out["hebrew_date"] = f"{conv.get('hd')} {conv.get('hm')} {conv.get('hy')}"
    return out


def find_city(q):
    url = "https://www.hebcal.com/complete.php?q=" + urllib.parse.quote(q)
    res = fetch(url)
    if not res:
        print(f"No city found for '{q}'. Try the English name, or a nearby larger city.")
        return
    print(f"Hebcal locations matching '{q}' (put the number in config.json -> location.geonameid):")
    for r in res[:10]:
        print(f"   {r.get('id'):>9}  {r.get('value')}")


# ------------------------------------------------------------------ own table
def load_own_table(path):
    with open(path, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    table = {}
    for r in rows:
        d = (r.get("date") or "").strip()
        if d:
            table[d] = {"candle": (r.get("candle") or "").strip(),
                        "havdalah": (r.get("havdalah") or r.get("tzeit") or "").strip(),
                        "label": (r.get("label") or "").strip()}
    return table


# ------------------------------------------------------------------ rules
BASE_NAMES = {"candle": "candle lighting", "havdalah": "Shabbat ends",
              "sunset_fri": "sunset Friday", "sunset_sat": "sunset Shabbat",
              "sunrise_sat": "sunrise Shabbat", "sunset_sun": "sunset Sunday",
              "tzeit_sun": "nightfall Sunday (sun 7.083 degrees down)",
              "tzeit85_sun": "nightfall Sunday (sun 8.5 degrees down)"}


def apply_rule(rule, bases):
    b = rule.get("from")
    base = bases.get(b)
    if base is None:
        return None, f"{BASE_NAMES.get(b, b)} is not available, so this time cannot be computed"
    off = int(rule.get("offset", 0))
    step = int(rule.get("round_to", 1))
    mode = rule.get("round", "nearest")
    v = round_to(base + off, step, mode)
    expl = f"{BASE_NAMES[b]} {hhmm(base)}"
    if off:
        expl += f" {'+' if off > 0 else '-'} {abs(off)} min"
    if step > 1:
        expl += f", rounded {mode} to {step} min"
    na, nb = to_min(rule.get("not_after")), to_min(rule.get("not_before"))
    if na is not None:
        expl += f", not after {hhmm(na)}"
        v = min(v, na)
    if nb is not None:
        expl += f", not before {hhmm(nb)}"
        v = max(v, nb)
    return v, expl + f" -> {hhmm(v)}"


def holiday_key(title):
    """Hebcal holiday title on Shabbat -> key in names.json 'yom_tov_shabbat'."""
    t = norm(title)
    if "CH''M" in t:
        return t.split()[0] + " Chol HaMoed"
    if t.startswith("Pesach VII"):
        return "Pesach VII"
    return re.sub(r"\s+[IVX]+$", "", t.split(" (")[0])


# ------------------------------------------------------------------ build
def build(cfg, friday, state_path, table_override=None, thought_path=None, user_set=None):
    user_set = dict(user_set or {})
    try:
        fri = datetime.date.fromisoformat(friday)
    except ValueError:
        raise Stop(f"'{friday}' is not a date in the form YYYY-MM-DD.")
    if fri.weekday() != 4:
        raise Stop(f"{friday} is a {fri.strftime('%A')}, not a Friday. Give the date of Erev Shabbat.")
    langs = cfg["languages"]
    names = load_json(os.path.join(ROOT, "data", "names.json"))
    blockers, warnings, notes, lines_report = [], [], [], []

    hc = hebcal_week(cfg, friday)
    sat = hc["saturday"]
    sun = (fri + datetime.timedelta(days=2)).isoformat()
    loc = hc["location"]
    lines_report.append(f"Location: {loc.get('title')} (Hebcal geonameid {loc.get('geonameid')}, "
                        f"time zone {loc.get('tzid')})")
    lines_report.append(f"Hebrew date of Shabbat: {hc['hebrew_date']} (Hebcal converter)")

    if not hc["candle"] or not hc["havdalah"]:
        raise Stop("Hebcal has no Friday candle lighting or no Saturday-night Shabbat end for "
                   "this date. Almost always this means Shabbat runs into a two-day Yom Tov (or "
                   "follows one), so it is a holiday week: holiday messages are not built by "
                   "this tool. Nothing was filled in.")

    # ---- candle lighting and Shabbat ends: own table decides, Hebcal checks
    hc_candle, hc_havdalah = hc["candle"][1], hc["havdalah"][1]
    offset = hc["candle"][2]
    own_cfg = cfg.get("own_table") or {}
    own_path = rel(table_override or own_cfg.get("csv"))
    max_gap = int(own_cfg.get("max_gap_minutes", 3))
    candle = havdalah = None
    if own_path:
        if not os.path.exists(own_path):
            blockers.append(f"The own zmanim table is configured ({own_path}) but the file does not "
                            f"exist. No times are shown until it is fixed or removed from config.json.")
        else:
            row = load_own_table(own_path).get(friday)
            if not row:
                blockers.append(f"The own zmanim table has no row for {friday}. The table is the "
                                f"authority, so this week stops: add the row from the printed luach.")
            else:
                candle, havdalah = to_min(row["candle"]), to_min(row["havdalah"])
                src = f"own table row {friday}" + (f" \"{row['label']}\"" if row["label"] else "")
                for nm, mine, theirs in (("Candle lighting", candle, hc_candle),
                                         ("Shabbat ends", havdalah, hc_havdalah)):
                    if mine is None:
                        blockers.append(f"{nm} is empty in the own table for {friday} "
                                        f"(often a Yom Tov row). No time is filled in.")
                        continue
                    gap = mine - theirs
                    lines_report.append(f"{nm} {hhmm(mine)} <- {src}; Hebcal says {hhmm(theirs)} "
                                        f"(gap {gap:+d} min, limit {max_gap}).")
                    if abs(gap) > max_gap:
                        hint = (" A gap of about an hour almost always means a daylight-saving "
                                "change that was not applied." if abs(gap) >= 50 else "")
                        blockers.append(f"{nm}: own table {hhmm(mine)}, Hebcal {hhmm(theirs)}, "
                                        f"gap {gap:+d} min (limit {max_gap}).{hint}")
    else:
        candle, havdalah = hc_candle, hc_havdalah
        hv = cfg["havdalah"]
        hv_desc = ("nightfall, sun 8.5 degrees below the horizon" if hv["mode"] == "tzeit_8.5"
                   else f"{hv['minutes']} minutes after sunset")
        lines_report.append(f"Candle lighting {hhmm(candle)} <- Hebcal, "
                            f"{cfg['candle_lighting_minutes']} min before sunset. "
                            f"No own table is configured, so Hebcal is the SOURCE this week, not a "
                            f"cross-check. Compare with the local Rav's luach if there is one.")
        lines_report.append(f"Shabbat ends {hhmm(havdalah)} <- Hebcal ({hv_desc}).")

    # ---- did Hebcal apply the configured candle-lighting minutes?
    ss_fri = hc["sunset"].get(friday)
    if ss_fri:
        actual = ss_fri[1] - hc_candle
        want = cfg["candle_lighting_minutes"]
        if abs(actual - want) > 1:
            blockers.append(f"Hebcal lit candles {actual} min before sunset, but config.json says "
                            f"{want}. Hebcal fixes some cities (Jerusalem is always 40). Set "
                            f"candle_lighting_minutes to the local custom, or use an own table.")
    tz85 = hc["tzeit85"].get(sat)
    if cfg["havdalah"]["mode"] == "tzeit_8.5" and tz85 and abs(tz85[1] - hc_havdalah) > 1:
        notes.append(f"Hebcal Shabbat-ends {hhmm(hc_havdalah)} differs from its own 8.5-degree "
                     f"nightfall {hhmm(tz85[1])}. Worth a look.")

    # ---- daylight-saving checks
    clock_change_week = False
    if len({v[2] for v in hc["sunset"].values()}) > 1:
        clock_change_week = True
        change = [d for d in sorted(hc["sunset"]) if hc["sunset"][d][2] != offset]
        blockers.append(f"The clocks change during the coming week (UTC{offset} -> "
                        f"UTC{hc['sunset'][change[0]][2]} from {change[0]}). Weekday times printed "
                        f"for after that date may be an hour off. Confirm each weekday time.")
    state = {}
    if state_path and os.path.exists(state_path):
        state = load_json(state_path)
    saved_vals = state.get("values") or {}
    saved_since = state.get("since") or {}
    same_clock = state.get("utc_offset") == offset

    # ---- base values for rules
    g = lambda d, k: (hc[k].get(d) or (None, None))[1]
    bases = {"candle": candle, "havdalah": havdalah,
             "sunset_fri": g(friday, "sunset"), "sunset_sat": g(sat, "sunset"),
             "sunrise_sat": g(sat, "sunrise"), "sunset_sun": g(sun, "sunset"),
             "tzeit_sun": g(sun, "tzeit7083"), "tzeit85_sun": g(sun, "tzeit85")}

    # ---- calendar: Yom Tov on Shabbat, holidays, fasts, Rosh Chodesh
    chag_key = None
    if not hc["parasha"]:
        sat_h = [t for d, t, s in hc["holidays"] if d == sat and s == "major"]
        fri_h = [t for d, t, s in hc["holidays"] if d == friday and s == "major"]
        fri_ok = all(t.startswith("Erev ") or "CH''M" in t or "Hoshana Raba" in t for t in fri_h)
        if sat_h and fri_ok and not any(t.startswith(("Yom Kippur", "Rosh Hashana")) for t in sat_h):
            chag_key = holiday_key(sat_h[0])
        else:
            blockers.append("Hebcal has no weekly parasha for this Shabbat, and it is not a one-day "
                            "Yom Tov that begins Friday night and ends Shabbat night. A holiday "
                            "message has a different structure and is not built here. What is "
                            "printed is a skeleton only.")
    if chag_key:
        notes.append(f"This Shabbat is also Yom Tov ({chag_key}). It enters Friday and ends "
                     f"Shabbat night, so every Shabbat time rule applies unchanged; only the title "
                     f"changes. Yom Tov additions (Hakafot, Yizkor, Kiddush times) are not built: "
                     f"add them by hand. In the Eilat archive Shabbat Mincha on such a Shabbat "
                     f"matched the rule in 2 of 4 cases, so confirm it.")
    chol_hamoed_week = any("CH''M" in t for d, t, s in hc["holidays"] if d > sat)
    seen, big = set(), {}
    for d, title, sub in hc["holidays"]:
        root = re.sub(r"\s+[IVX]+$", "", title.split(":")[0].split(" (")[0])
        if sub in ("major", "fast"):
            if chag_key and (d in (friday, sat) or "CH''M" in title):
                continue  # the Yom Tov itself and the Chol HaMoed days after it
            big.setdefault(root, []).append((d, title.split(" (")[0]))
            continue
        if root in seen:
            continue
        seen.add(root)
        if sub == "minor" and root not in QUIET_MINOR:
            notes.append(f"{root} ({d}) is in this week. Not a blocker; mention it if the community "
                         f"usually does.")
    if big:
        listed = "; ".join((f"{k} {v[0][0]} to {v[-1][0]}" if len(v) > 1 else f"{v[0][1]} {v[0][0]}")
                           for k, v in big.items())
        blockers.append(f"Holiday or fast in this message's week: {listed}. Holiday and fast-day "
                        f"schedules are not built by this tool; decide what to add, or send a "
                        f"separate holiday message.")
    hm = hc["hmonth"]
    rc_on_shabbat = [m for d, m in hc["roshchodesh"] if d == sat]
    rc_near = [(d, m) for d, m in hc["roshchodesh"] if d != sat]
    if rc_near and not rc_on_shabbat:
        d0, m0 = rc_near[0]
        notes.append(f"Rosh Chodesh {m0} is on {d0}, not on Shabbat itself, so it is not in the "
                     f"title (the Eilat archive rule). Add it by hand if your community does.")

    # ---- titles
    style = "en_ashkenazi" if cfg.get("english_style", "ashkenazi") == "ashkenazi" else "en_sephardic"
    ash = style == "en_ashkenazi"
    ov = cfg.get("title_overrides") or {}
    titles = {}
    par = names["parashiyot"].get(hc["parasha"]) if hc["parasha"] else None
    if hc["parasha"] and not par:
        blockers.append(f"Hebcal returned the parasha name '{hc['parasha']}', which is not in "
                        f"data/names.json. The name is not guessed: add a row there.")
    chag = names["yom_tov_shabbat"].get(chag_key) if chag_key else None
    if chag_key and not chag:
        blockers.append(f"Yom Tov '{chag_key}' is not in data/names.json (yom_tov_shabbat). "
                        f"The name is not guessed: add a row there.")
    specials = []
    for sp in hc["special"]:
        row = names["special_shabbatot"].get(sp)
        if not row:
            blockers.append(f"Special Shabbat '{sp}' from Hebcal is not in data/names.json. "
                            f"Not guessed: add a row there.")
        else:
            specials.append(row)
    rc_rows = []
    for m in rc_on_shabbat[:1]:
        row = names["months"].get(m)
        if not row:
            blockers.append(f"Month '{m}' is not in data/names.json.")
        else:
            rc_rows.append(row)
    mev_row = names["months"].get(hc["mevarchim"]) if hc["mevarchim"] else None
    if hc["mevarchim"] and not mev_row:
        blockers.append(f"Month '{hc['mevarchim']}' (Shabbat Mevarchim) is not in data/names.json.")
    key_for_ov = hc["parasha"] or chag_key
    for l in langs:
        src_row = par or chag
        pname = None
        if src_row:
            pname = (ov.get(l) or {}).get(key_for_ov) or src_row.get(style if l == "en" else l)
            if not pname:
                blockers.append(f"No {l} name for '{key_for_ov}' in data/names.json. Not guessed.")
        if l == "he":
            head = ("שבת " + ("פרשת " if par else "") + pname) if pname else "שבת"
            parts = [head] + [s["he"] for s in specials] + ["ראש חודש " + r["he"] for r in rc_rows]
            t = [" / ".join(parts)]
            if mev_row:
                t.append("שבת מברכים חודש " + mev_row["he"])
        elif l == "en":
            if pname and par:
                head = ("Parshas " if ash else "Parashat ") + pname
            elif pname:
                head = ("Shabbos " if ash else "Shabbat ") + pname
            else:
                head = "Shabbos" if ash else "Shabbat"
            parts = [head] + [s[style] for s in specials] + ["Rosh Chodesh " + r[style] for r in rc_rows]
            t = ["*" + " | ".join(parts) + "*"]
            if mev_row:
                t.append(("Shabbos Mevorchim Chodesh " if ash else "Shabbat Mevarchim Chodesh ")
                         + mev_row[style])
        else:
            head = ("Chabat " + pname) if pname else "Chabat"
            parts = [head] + [s["fr"] for s in specials] + ["Roch Hodech " + r["fr"] for r in rc_rows]
            t = ["_*" + " - ".join(parts) + "*_"]
        titles[l] = t

    # ---- prayer times
    times_out = {}
    new_state = {"friday": friday, "utc_offset": offset, "values": {}, "since": {},
                 "watch_gaps": {}}
    carried = []  # (skey, value) for carried values

    def remember(skey, value):
        if value is None:
            return
        new_state["values"][skey] = hhmm(value)
        prev = saved_vals.get(skey)
        new_state["since"][skey] = (saved_since.get(skey) or state.get("friday") or friday) \
            if prev == hhmm(value) else friday

    for section in SECTIONS:
        rows = []
        for item in cfg["times"].get(section, []):
            iid = item.get("id") or (item.get("label", {}).get("en") or "item")
            if item.get("only_in_months") and hm not in [norm(x) for x in item["only_in_months"]]:
                continue
            if item.get("not_in_months") and hm in [norm(x) for x in item["not_in_months"]]:
                continue
            skey = f"{section}/{iid}"
            value, kind, expl = None, None, ""
            saved = saved_vals.get(skey)
            if skey in user_set:
                value = to_min(user_set.pop(skey))
                kind, expl = "set", "given by the user for this week (--set)"
                if "rule" in item:
                    rv, rx = apply_rule(item["rule"], bases)
                    if rv is not None and rv != value:
                        notes.append(f"{skey}: set to {hhmm(value)}, the rule gives {hhmm(rv)} "
                                     f"({rx}). A time from outside (poster, photo, message) is "
                                     f"checked like any other value.")
                if "carry" in item or (item.get("rule") or {}).get("hold"):
                    remember(skey, value)
                elif "rule" not in item:
                    notes.append(f"{skey} was set to {hhmm(value)} for this week only. To make it "
                                 f"permanent, change its 'fixed' in config.json.")
            elif "fixed" in item:
                value, kind, expl = to_min(item["fixed"]), "fixed", "fixed in config.json"
            elif "rule" in item:
                rule = item["rule"]
                value, expl = apply_rule(rule, bases)
                kind = "rule"
                if value is None:
                    blockers.append(f"{skey}: {expl}.")
                hold = rule.get("hold")
                base = bases.get(rule.get("from"))
                if value is not None and hold and saved and base is not None:
                    sv = to_min(saved)
                    dur, tol = int(hold.get("duration", 0)), int(hold.get("end_within", 0))
                    if not same_clock:
                        expl += " (last week's time not held: the clock changed since it was saved)"
                    elif value < sv and sv + dur <= base + tol:
                        expl += (f"; HELD at last approved {saved}: a {dur}-min service starting "
                                 f"then ends by {hhmm(sv + dur)}, within {tol} min of "
                                 f"{BASE_NAMES[rule['from']]}")
                        value, kind = sv, "rule-held"
                if value is not None and saved and to_min(saved) != value:
                    diff = value - to_min(saved)
                    notes.append(f"{skey} changes this week: {saved} -> {hhmm(value)} ({diff:+d} min)."
                                 + (" About an hour: a clock change." if abs(diff) >= 45 else ""))
                remember(skey, value)
            elif "carry" in item:
                kind = "carried"
                c = item["carry"] or {}
                if saved:
                    value = to_min(saved)
                    carried.append(skey)
                    expl = (f"copied from the approved message of {state.get('friday')} "
                            f"(not computed; confirm it still holds)")
                elif c.get("initial"):
                    value = to_min(c["initial"])
                    expl = "initial value from config.json (no saved week yet; confirm)"
                elif c.get("suggest"):
                    value, sx = apply_rule(c["suggest"], bases)
                    kind = "suggested"
                    expl = f"SUGGESTED by rule, needs approval: {sx}"
                    if value is not None:
                        notes.append(f"{skey}: no saved time yet. Suggested {hhmm(value)} "
                                     f"by rule ({sx}). Approve or correct it.")
                    else:
                        blockers.append(f"{skey}: no saved time, and the suggestion rule "
                                        f"cannot run: {sx}.")
                if value is None and item.get("optional"):
                    notes.append(f"{skey}: no saved time, so the line is left out "
                                 f"(marked optional in config.json).")
                    continue
                if value is None and kind == "carried":
                    blockers.append(f"{skey}: no saved time, no 'initial' and no 'suggest' rule. "
                                    f"The time is not invented; it must be given.")
                w = c.get("watch")
                if value is not None and w in bases and bases[w] is not None:
                    gap = bases[w] - value
                    new_state["watch_gaps"][skey] = gap
                    prev = (state.get("watch_gaps") or {}).get(skey)
                    alert = int(c.get("alert_minutes", 8))
                    if saved and prev is not None and abs(gap - prev) >= alert:
                        notes.append(f"{skey}: {BASE_NAMES[w]} is {hhmm(bases[w])}; the gap to "
                                     f"{hhmm(value)} is {gap} min, against {prev} last time "
                                     f"({gap - prev:+d}). Time to move it by 5 minutes?")
                nb = to_min(c.get("not_before"))
                if value is not None and nb is not None and value < nb:
                    notes.append(f"{skey}: {hhmm(value)} is earlier than the floor "
                                 f"{hhmm(nb)} set in config.json.")
                remember(skey, value)
            else:
                blockers.append(f"{skey}: no 'fixed', 'rule' or 'carry' in config.json.")
            rows.append({"id": iid, "item": item, "value": value, "kind": kind, "explain": expl})
        times_out[section] = rows

    for k in user_set:
        blockers.append(f"--set {k}: no such time in config.json (use section/id, e.g. "
                        f"weekdays/mincha).")

    # ---- clock and age checks on carried values
    if carried and state.get("utc_offset") and not same_clock:
        blockers.append(f"The clock changed since the saved week ({state.get('friday')}: "
                        f"UTC{state.get('utc_offset')}, now UTC{offset}). Carried times were saved "
                        f"on the old clock: confirm each one. (This is the mistake that once sent "
                        f"Mincha an hour late.)")
    max_age = int(cfg.get("carry_max_age_days", 21))
    for skey in carried:
        since = saved_since.get(skey) or state.get("friday")
        if since and days_between(since, friday) > max_age:
            warnings.append(f"{skey} = {saved_vals.get(skey)} has been carried unchanged since "
                            f"{since} ({days_between(since, friday)} days). A change of season moves "
                            f"davening times by up to an hour: confirm it against this week's "
                            f"sunset before sending.")
    if state.get("friday") and carried and days_between(state["friday"], friday) > max_age:
        warnings.append(f"The last approved week is {state['friday']}, more than {max_age} days ago. "
                        f"Every carried time needs a fresh look.")

    # ---- cross-checks between values (an outside source is checked like any other)
    flat = {f"{s}/{r['id']}": r["value"] for s, rows in times_out.items() for r in rows}
    for section, rows in times_out.items():
        for r in rows:
            cc = r["item"].get("cross_check")
            if not cc or r["value"] is None:
                continue
            other = flat.get(cc.get("with"))
            if other is None:
                continue
            gap = r["value"] - other
            lim = int(cc.get("max_minutes", 20))
            if abs(gap) > lim:
                msg = (f"{section}/{r['id']} {hhmm(r['value'])} is {gap:+d} min from {cc['with']} "
                       f"{hhmm(other)}; the limit in config.json is {lim}.")
                if clock_change_week:
                    notes.append(msg + " Expected in a clock-change week; confirm.")
                else:
                    blockers.append(msg + " Check where this time came from.")

    # ---- weekly thought (written by the agent from a checked source, never by this script)
    wt = cfg.get("weekly_thought") or {}
    thought = None
    if wt.get("enabled"):
        if thought_path:
            thought = check_thought(load_json(rel(thought_path)), langs, wt)
            for l in langs:
                if not thought.get(l):
                    notes.append(f"Thought file has no '{l}' lines: no thought in the {l} message "
                                 f"(it is not machine-translated).")
            for l in langs:
                for line in thought.get(l) or []:
                    if len(line) > int(wt.get("max_line_chars", 200)):
                        notes.append(f"Thought ({l}): a line is {len(line)} characters; keep each "
                                     f"line short.")
        else:
            notes.append("The weekly thought is enabled but no --thought file was given, so there "
                         "is no thought paragraph. It is written only from a source that was read "
                         "in the source text itself (WORKFLOW.md, step 4).")
    elif thought_path:
        notes.append("--thought was given but weekly_thought.enabled is false: nothing was added.")

    # ---- labels must exist in every language; no machine translation of labels
    for section, rows in times_out.items():
        for r in rows:
            for l in (r["item"].get("languages") or langs):
                if l in langs and not (r["item"].get("label") or {}).get(l):
                    blockers.append(f"{section}/{r['id']}: no label for language '{l}' in config.json.")

    messages = {l: render(l, cfg, titles[l], candle, havdalah, times_out, hm, rc_rows,
                          thought, chol_hamoed_week)
                for l in langs}

    if candle is None or havdalah is None:
        blockers.insert(0, "Candle lighting or Shabbat ends has no valid source this week. "
                           "The draft shows [MISSING] in their place.")

    return {"friday": friday, "shabbat": sat, "languages": langs, "messages": messages,
            "blockers": blockers, "warnings": warnings, "notes": notes, "sources": lines_report,
            "times": {s: [{"id": r["id"], "value": hhmm(r["value"]) if r["value"] is not None else None,
                           "kind": r["kind"], "explain": r["explain"]} for r in rows]
                      for s, rows in times_out.items()},
            "hebcal_urls": list(SOURCES_USED), "state": new_state,
            "weekly_thought": {"enabled": bool(wt.get("enabled")), "included": bool(thought),
                               "source": (thought or {}).get("source")}}


def check_thought(t, langs, wt):
    """The thought file: up to max_lines short lines per language, and the full
    source for the shliach, which never goes into the message."""
    max_lines = int(wt.get("max_lines", 3))
    for l in LANGS:
        lines = t.get(l)
        if lines is None:
            continue
        if isinstance(lines, str):
            lines = [lines]
            t[l] = lines
        if not (1 <= len(lines) <= max_lines) or not all(isinstance(x, str) and x.strip() for x in lines):
            raise Stop(f"Thought file: '{l}' must be 1 to {max_lines} non-empty lines.")
    src = t.get("source") or {}
    need = [k for k in ("work", "location", "checked") if not str(src.get(k) or "").strip()]
    if need:
        raise Stop("Thought file: 'source' needs " + ", ".join(need) + ". 'location' is the volume, "
                   "sicha or section and page; 'checked' says how the passage itself was read. "
                   "A thought without a checked source is not added.")
    for l in LANGS:
        for line in t.get(l) or []:
            if src["work"].strip() and src["work"].strip() in line:
                raise Stop("Thought file: the source belongs in the report for the shliach, not "
                           "inside the message lines.")
    return t


# ------------------------------------------------------------------ render
TXT = {
    "he": {"times": "זמני שבת", "candle": "הדלקת נרות", "ends": "צאת השבת",
           "davening": "זמני תפילות", "friday": "ערב שבת:", "shabbat": "שבת קודש:",
           "weekdays": "ימי חול:", "chol_hamoed": "חול המועד:", "thought": "מחשבה לשבת"},
    "en": {"times": "Shabbos times", "candle": "Candle lighting", "ends": "Shabbos ends",
           "davening": "Davening times", "friday": "Friday:", "shabbat": "Shabbos:",
           "weekdays": "Weekdays:", "chol_hamoed": "Chol HaMoed:", "thought": "A thought for Shabbos"},
    "en_s": {"times": "Shabbat times", "ends": "Shabbat ends", "shabbat": "Shabbat:",
             "thought": "A thought for Shabbat"},
    "fr": {"times": "Horaires à", "candle": "Allumage des bougies de Chabat :",
           "ends": "Sortie du Chabat :", "davening": "Horaires des tfilot à",
           "friday": "*Vendredi :*", "shabbat": "*Chabat :*", "weekdays": "*Jours de semaine*",
           "chol_hamoed": "*Hol Hamoed*", "thought": "Une pensée pour Chabat"},
}


def render(lang, cfg, title_lines, candle, havdalah, times_out, hm, rc_rows, thought, chol_hamoed):
    tx = dict(TXT[lang])
    if lang == "en" and cfg.get("english_style", "ashkenazi") != "ashkenazi":
        tx.update(TXT["en_s"])
    emoji = cfg.get("use_emoji", True) and lang != "fr"
    e = (lambda s: s + " ") if emoji else (lambda s: "")
    name = cfg["community"]["name"][lang]
    city = cfg["community"]["city"][lang]
    ft = lambda v: fmt_time(v, lang, cfg)
    L = list(title_lines) + [""]
    if lang == "fr":
        L += [f"*{tx['times']} {city}*", "", f"{tx['candle']} {ft(candle)}",
              f"{tx['ends']} {ft(havdalah)}", "", f"{tx['davening']} {name}", ""]
    else:
        L += [f"{e('🕯️')}{tx['times']} – {city}:", f"{tx['candle']}: {ft(candle)}",
              f"{tx['ends']}: {ft(havdalah)}", "", f"{e('📍')}{tx['davening']} – {name}", ""]
    for section in SECTIONS:
        rows = [r for r in times_out[section]
                if lang in (r["item"].get("languages") or cfg["languages"])]
        if not rows:
            continue
        head = tx[section]
        if section == "weekdays":
            head = tx["chol_hamoed"] if chol_hamoed else head
            if lang != "fr":
                head = e("⏰") + head
        L.append(head)
        for r in rows:
            if r["item"].get("blank_before"):
                L.append("")
            label = (r["item"].get("label") or {}).get(lang) or "[label missing]"
            sep = " " if lang == "fr" else ": "
            L.append(f"{label}{sep}{ft(r['value'])}")
        L.append("")
    if thought and thought.get(lang):
        wt = cfg.get("weekly_thought") or {}
        title = (wt.get("title") or {}).get(lang) or tx["thought"]
        L.append(("✨ " if emoji else "") + (f"*{title}*" if lang == "fr" else title))
        L += list(thought[lang])
        L.append("")
    cl = cfg.get("closing") or {}
    closing = []
    first = (cl.get("chol_hamoed") or {}).get(lang) if chol_hamoed else None
    for key, cond in (("always", True), ("elul", hm == "Elul"),
                      ("rosh_chodesh_on_shabbat", bool(rc_rows)), ("nisan", hm == "Nisan")):
        txt = (cl.get(key) or {}).get(lang)
        if key == "always" and first:
            txt = first
        if cond and txt:
            if key == "nisan":
                closing.append("")
            closing.append(txt)
    L += closing
    while L and L[-1] == "":
        L.pop()
    return "\n".join(L)


# ------------------------------------------------------------------ main
def next_friday(today=None):
    d = today or datetime.date.today()
    return (d + datetime.timedelta(days=(4 - d.weekday()) % 7)).isoformat()


def arg_value(argv, flag):
    if flag in argv:
        i = argv.index(flag)
        if i + 1 < len(argv):
            return argv[i + 1]
        raise Stop(f"{flag} needs a value.")
    return None


def print_report(r):
    bar = "=" * 50
    if r["blockers"]:
        print(bar)
        print("STOP - DO NOT SEND. Blockers this week:")
        for b in r["blockers"]:
            print("   - " + b)
    if r["warnings"]:
        print(bar)
        print("WARNING - check before sending:")
        for w in r["warnings"]:
            print("   - " + w)
    for l in r["languages"]:
        print(bar)
        print(f"DRAFT [{l}]" + ("  (blocked - not for sending)" if r["blockers"] else ""))
        print(bar)
        print(r["messages"][l])
    print(bar)
    src = r["weekly_thought"].get("source")
    if src:
        print("SOURCE OF THE THOUGHT - for the shliach only, not in the message:")
        for k in ("work", "location", "builds_on", "found_via", "checked"):
            if src.get(k):
                print(f"   {k}: {src[k]}")
        print(bar)
    print(f"CERTAINTY REPORT - Shabbat {r['shabbat']} (not part of the message)")
    print("\nWhere the Shabbat times come from:")
    for s in r["sources"]:
        print("   - " + s)
    print("\nEach davening time:")
    for section, rows in r["times"].items():
        for t in rows:
            print(f"   [{t['kind']}] {section}/{t['id']} = {t['value'] or MISSING}: {t['explain']}")
    if r["notes"]:
        print("\nFor approval:")
        for n in r["notes"]:
            print("   - " + n)
    print("\nHebcal requests made:")
    for u in r["hebcal_urls"]:
        print("   " + u)
    print("\nNothing was sent anywhere. After the draft is approved: --save")


def main(argv):
    flags = {a for a in argv if a.startswith("--")}
    vals = {}
    for f in ("--config", "--state", "--table", "--thought", "--find-city"):
        vals[f] = arg_value(argv, f)
    user_set = {}
    for i, a in enumerate(argv):
        if a == "--set":
            if i + 1 >= len(argv) or "=" not in argv[i + 1]:
                raise Stop("--set needs section/id=HH:MM, e.g. --set weekdays/mincha=18:30")
            k, v = argv[i + 1].split("=", 1)
            try:
                to_min(v)
            except Exception:
                raise Stop(f"--set {argv[i + 1]}: '{v}' is not a time like 18:30.")
            user_set[k.strip()] = v.strip()
    skip = {v for v in vals.values() if v} | {argv[i + 1] for i, a in enumerate(argv)
                                              if a == "--set" and i + 1 < len(argv)}
    pos = [a for a in argv if not a.startswith("--") and a not in skip]
    if vals["--find-city"]:
        find_city(vals["--find-city"])
        return 0
    cfg_path = rel(vals["--config"] or "config.json")
    cfg = load_config(cfg_path)
    stem = os.path.splitext(os.path.basename(cfg_path))[0]
    state_path = rel(vals["--state"] or os.path.join(
        "data", "state.json" if stem == "config" else f"state-{stem}.json"))
    friday = pos[0] if pos else next_friday()
    r = build(cfg, friday, state_path, vals["--table"], vals["--thought"], user_set)
    if "--json" in flags:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print_report(r)
    if "--save" in flags:
        if r["blockers"] and "--confirmed" not in flags:
            print("\nNOT SAVED: there are blockers. Resolve them first (or, only if the user "
                  "explicitly approved the draft as is, add --confirmed).")
            return 2
        os.makedirs(os.path.dirname(state_path), exist_ok=True)
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(r["state"], f, ensure_ascii=False, indent=2)
        os.makedirs(os.path.join(ROOT, "output"), exist_ok=True)
        for l in r["languages"]:
            with open(os.path.join(ROOT, "output", f"{friday}-{stem}-{l}.txt"), "w",
                      encoding="utf-8") as f:
                f.write(r["messages"][l] + "\n")
        print(f"\nSaved: {state_path} and output/{friday}-{stem}-*.txt (still nothing was sent).")
    return 2 if r["blockers"] else 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Stop as e:
        print("STOP - no draft was built.\n   " + str(e))
        sys.exit(3)
