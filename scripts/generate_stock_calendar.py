#!/usr/bin/env python3
"""Generate an Outlook-compatible ICS calendar for stock earnings calls."""

from __future__ import annotations

import argparse
import csv
import hashlib
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

CATEGORY_BY_MARKET = {
    "TW": "TW-Market",
    "US": "US-Market",
    "JP": "JP-Market",
    "CN": "CN-Market",
}


@dataclass
class Event:
    subject: str
    market: str
    start_local: datetime
    end_local: datetime
    description: str


def escape_ics_text(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace(";", r"\;")
        .replace(",", r"\,")
        .replace("\n", r"\n")
    )


def build_uid(subject: str, start_local: datetime, market: str) -> str:
    raw = f"{subject}|{start_local.isoformat()}|{market}"
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]
    return f"{digest}@stock-calendar"


def parse_csv(path: Path) -> list[Event]:
    events: list[Event] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        required = {
            "subject",
            "market",
            "date",
            "time",
            "timezone",
            "duration_minutes",
            "description",
        }
        if not required.issubset(set(reader.fieldnames or [])):
            missing = required - set(reader.fieldnames or [])
            raise ValueError(f"CSV missing required columns: {sorted(missing)}")

        for idx, row in enumerate(reader, start=2):
            market = (row["market"] or "").strip().upper()
            if market not in CATEGORY_BY_MARKET:
                raise ValueError(
                    f"Line {idx}: market must be one of {sorted(CATEGORY_BY_MARKET)}, got '{market}'"
                )

            tz_name = (row["timezone"] or "").strip()
            try:
                tz = ZoneInfo(tz_name)
            except Exception as exc:  # zone lookup errors vary by platform
                raise ValueError(f"Line {idx}: invalid timezone '{tz_name}'") from exc

            dt_str = f"{row['date'].strip()} {row['time'].strip()}"
            try:
                naive_start = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
            except ValueError as exc:
                raise ValueError(
                    f"Line {idx}: invalid date/time '{dt_str}', expected YYYY-MM-DD HH:MM"
                ) from exc

            try:
                duration = int((row["duration_minutes"] or "").strip())
            except ValueError as exc:
                raise ValueError(
                    f"Line {idx}: duration_minutes must be an integer"
                ) from exc

            start_local = naive_start.replace(tzinfo=tz)
            end_local = start_local + timedelta(minutes=duration)

            events.append(
                Event(
                    subject=(row["subject"] or "").strip(),
                    market=market,
                    start_local=start_local,
                    end_local=end_local,
                    description=(row["description"] or "").strip(),
                )
            )

    return events


def to_ics(events: list[Event], calendar_name: str) -> str:
    now_utc = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Local//Stock Earnings Calendar//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{escape_ics_text(calendar_name)}",
    ]

    for event in events:
        category = CATEGORY_BY_MARKET[event.market]
        tzid = event.start_local.tzinfo.key if hasattr(event.start_local.tzinfo, "key") else "UTC"
        uid = build_uid(event.subject, event.start_local, event.market)
        desc = escape_ics_text(event.description)
        summary = escape_ics_text(f"[{event.market}] {event.subject}")

        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:{uid}",
                f"DTSTAMP:{now_utc}",
                f"DTSTART;TZID={tzid}:{event.start_local.strftime('%Y%m%dT%H%M%S')}",
                f"DTEND;TZID={tzid}:{event.end_local.strftime('%Y%m%dT%H%M%S')}",
                f"SUMMARY:{summary}",
                f"DESCRIPTION:{desc}",
                f"CATEGORIES:{escape_ics_text(category)}",
                "END:VEVENT",
            ]
        )

    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate Outlook ICS calendar for TW/US/JP/CN earnings events"
    )
    parser.add_argument("--input", required=True, type=Path, help="Input CSV path")
    parser.add_argument("--output", required=True, type=Path, help="Output ICS path")
    parser.add_argument(
        "--calendar-name",
        default="Stock Earnings",
        help="Calendar display name in Outlook",
    )

    args = parser.parse_args()
    events = parse_csv(args.input)
    ics_content = to_ics(events, args.calendar_name)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(ics_content, encoding="utf-8", newline="")
    print(f"Generated {args.output} with {len(events)} events.")


if __name__ == "__main__":
    main()
