#!/usr/bin/env python3
import os
import re
import sys
from datetime import date

SOURCE_FILE = "/storage/emulated/0/Notes/Personal/Birthday"
CACHE_FILE = "birthdays.txt"

MONTHS = {
    "january": 1, "jan": 1,
    "february": 2, "feb": 2,
    "march": 3, "mar": 3,
    "april": 4, "apr": 4,
    "may": 5,
    "june": 6, "jun": 6,
    "july": 7, "jul": 7,
    "august": 8, "aug": 8,
    "september": 9, "sept": 9, "sep": 9,
    "october": 10, "oct": 10,
    "november": 11, "nov": 11,
    "december": 12, "dec": 12,
}


def parse_date(text):
    """Return (day, month, year) from a messy date string, or None if incomplete."""
    m = re.search(r"\(\s*(\d{1,2})/(\d{1,2})/(\d{4})\s*\)", text)
    if m:
        day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 1 <= day <= 31 and 1 <= month <= 12:
            return day, month, year
        return None

    tokens = re.findall(r"[A-Za-z]+|\d+", text)
    month = None
    day = None
    year = None
    for tok in tokens:
        lower = tok.lower()
        if lower in MONTHS and month is None:
            month = MONTHS[lower]
        elif tok.isdigit():
            if len(tok) == 4 and year is None:
                year = int(tok)
            elif day is None and 1 <= int(tok) <= 31:
                day = int(tok)

    if month is None or day is None:
        return None
    return day, month, year


def parse_source(path):
    entries = []
    with open(path, "r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or ":" not in line:
                continue
            name, _, datestr = line.partition(":")
            name = name.strip()
            datestr = datestr.strip().lstrip("-").strip()
            if not name or not datestr:
                continue
            parsed = parse_date(datestr)
            if parsed is None:
                continue
            day, month, year = parsed
            entries.append((name, day, month, year))
    return entries


def load_cache(path):
    entries = []
    with open(path, "r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line:
                continue
            parts = line.split("|")
            if len(parts) != 4:
                continue
            name = parts[0].strip()
            try:
                day, month = int(parts[1]), int(parts[2])
            except ValueError:
                continue
            year = int(parts[3]) if parts[3].strip() else None
            entries.append((name, day, month, year))
    return entries


def write_cache(path, entries):
    with open(path, "w", encoding="utf-8") as fh:
        for name, day, month, year in entries:
            fh.write(f"{name}|{day:02d}|{month:02d}|{year if year else ''}\n")


def next_occurrence(day, month, today):
    year = today.year
    candidate = make_date(year, month, day)
    if candidate < today:
        candidate = make_date(year + 1, month, day)
    return candidate


def make_date(year, month, day):
    try:
        return date(year, month, day)
    except ValueError:
        return date(year, month, 28)


def format_birthday(day, month, year):
    if year:
        return f"{day:02d}/{month:02d}/{year}"
    return f"{day:02d}/{month:02d}"


def main():
    cache_path = os.path.join(os.getcwd(), CACHE_FILE)

    if os.path.exists(cache_path):
        entries = load_cache(cache_path)
    else:
        if not os.path.exists(SOURCE_FILE):
            print(f"Error: source file not found: {SOURCE_FILE}", file=sys.stderr)
            return 1
        entries = parse_source(SOURCE_FILE)
        if not entries:
            print("Error: no valid birthdays found in source file.", file=sys.stderr)
            return 1
        write_cache(cache_path, entries)

    if not entries:
        print(f"Error: no valid entries in {CACHE_FILE}.", file=sys.stderr)
        return 1

    today = date.today()
    today_str = today.strftime("%d/%m/%Y")

    rows = []
    for name, day, month, year in entries:
        days_until = (next_occurrence(day, month, today) - today).days
        rows.append((name, day, month, year, days_until))

    today_people = [r for r in rows if r[4] == 0]
    upcoming = sorted((r for r in rows if r[4] > 0), key=lambda r: r[4])

    out = []
    for name, *_ in today_people:
        out.append(f"Today is {name}'s Birthday - {today_str}")
    if today_people:
        out.append("")

    headers = ("Name", "Birthday", "Days Until")
    table = [(name, format_birthday(day, month, year), str(days))
             for name, day, month, year, days in upcoming]

    name_w = max([len(headers[0])] + [len(r[0]) for r in table]) if table else len(headers[0])
    bday_w = max([len(headers[1])] + [len(r[1]) for r in table]) if table else len(headers[1])
    days_w = max([len(headers[2])] + [len(r[2]) for r in table]) if table else len(headers[2])

    out.append(f"{headers[0]:<{name_w}}  {headers[1]:<{bday_w}}  {headers[2]:>{days_w}}")
    out.append(f"{'-' * name_w}  {'-' * bday_w}  {'-' * days_w}")
    for name, bday, days in table:
        out.append(f"{name:<{name_w}}  {bday:<{bday_w}}  {days:>{days_w}}")

    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
