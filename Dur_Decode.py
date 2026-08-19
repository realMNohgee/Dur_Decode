#!/usr/bin/env python3
"""
Dur_Decode — Duration string parser, converter, and calculator.

Zero-dependency Python stdlib CLI. Parse and convert duration strings between
formats: human shorthand (1h30m), ISO 8601 (PT1H30M), colon (1:30:00), and
plain seconds.

Subcommands:
    parse     Parse a duration string and output all equivalent formats.
    add       Sum multiple duration strings.
    compare   Check whether two durations are equal.
    format    Convert raw seconds into a target display format.

https://hermtica.com/marketplace
"""

from __future__ import annotations

import argparse
import re
import sys
from typing import Tuple

__version__ = "1.0.0"

# ---------------------------------------------------------------------------
#  Unit constants (in seconds)
# ---------------------------------------------------------------------------
SECOND = 1
MINUTE = 60
HOUR = 60 * MINUTE
DAY = 24 * HOUR
WEEK = 7 * DAY

# ---------------------------------------------------------------------------
#  Parsers — each returns (total_seconds: int) or raises ValueError
# ---------------------------------------------------------------------------

# ISO 8601 duration: P[nW][nD]T[nH][nM][nS]  (we also accept the weeks-only variant)
_ISO_RE = re.compile(
    r"^P(?:(\d+)W)?(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?)?$"
)

# Human shorthand: e.g.  2w3d1h30m15s  (any subset of units, any order)
_HUMAN_RE = re.compile(r"(\d+)\s*(w|d|h|m|s)", re.IGNORECASE)

# Colon format:  H:MM:SS  or  M:SS
_COLON_RE = re.compile(r"^(\d+):([0-5]?\d):([0-5]?\d)$|^(\d+):([0-5]?\d)$")

# Plain number (seconds), optionally suffixed with 's'
_PLAIN_RE = re.compile(r"^(\d+)\s*s?$")


def parse_duration(text: str) -> int:
    """Parse *any* supported duration string into total seconds."""
    text = text.strip()

    # --- ISO 8601 -----------------------------------------------------------
    m = _ISO_RE.match(text)
    if m and any(m.groups()):
        weeks = int(m.group(1) or 0)
        days = int(m.group(2) or 0)
        hours = int(m.group(3) or 0)
        minutes = int(m.group(4) or 0)
        seconds = int(m.group(5) or 0)
        return weeks * WEEK + days * DAY + hours * HOUR + minutes * MINUTE + seconds * SECOND

    # --- Colon format -------------------------------------------------------
    m = _COLON_RE.match(text)
    if m:
        if m.group(1) is not None and m.group(3) is not None:
            # H:MM:SS
            hours = int(m.group(1))
            minutes = int(m.group(2))
            seconds = int(m.group(3))
        else:
            # M:SS
            hours = 0
            minutes = int(m.group(4))
            seconds = int(m.group(5))
        return hours * HOUR + minutes * MINUTE + seconds * SECOND

    # --- Human shorthand ----------------------------------------------------
    parts = _HUMAN_RE.findall(text)
    if parts:
        total = 0
        unit_map = {"w": WEEK, "d": DAY, "h": HOUR, "m": MINUTE, "s": SECOND}
        for value, unit in parts:
            total += int(value) * unit_map[unit.lower()]
        return total

    # --- Plain seconds ------------------------------------------------------
    m = _PLAIN_RE.match(text)
    if m:
        return int(m.group(1))

    raise ValueError(f"Unrecognised duration format: {text!r}")


# ---------------------------------------------------------------------------
#  Formatters — each takes total_seconds and returns a string
# ---------------------------------------------------------------------------

def format_human(total: int) -> str:
    """e.g. 2h30m15s, 45m, 0s"""
    if total == 0:
        return "0s"
    weeks, r = divmod(total, WEEK)
    days, r = divmod(r, DAY)
    hours, r = divmod(r, HOUR)
    minutes, seconds = divmod(r, MINUTE)
    parts = []
    if weeks:
        parts.append(f"{weeks}w")
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if seconds:
        parts.append(f"{seconds}s")
    return "".join(parts) if parts else "0s"


def format_iso(total: int) -> str:
    """ISO 8601 duration, e.g. PT2H30M15S"""
    if total == 0:
        return "PT0S"
    weeks, r = divmod(total, WEEK)
    days, r = divmod(r, DAY)
    hours, r = divmod(r, HOUR)
    minutes, seconds = divmod(r, MINUTE)
    date_part = ""
    if weeks:
        date_part += f"{weeks}W"
    if days:
        date_part += f"{days}D"
    time_part = ""
    if hours:
        time_part += f"{hours}H"
    if minutes:
        time_part += f"{minutes}M"
    if seconds:
        time_part += f"{seconds}S"
    if not time_part:
        time_part = "0S"
    return f"P{date_part}T{time_part}"


def format_colon(total: int) -> str:
    """H:MM:SS or M:SS"""
    if total < 0:
        raise ValueError("Negative durations not supported for colon format")
    hours, r = divmod(total, HOUR)
    minutes, seconds = divmod(r, MINUTE)
    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"


def format_seconds(total: int) -> str:
    """Plain integer seconds."""
    return str(total)


# ---------------------------------------------------------------------------
#  Output helpers
# ---------------------------------------------------------------------------

def emit_all_formats(total: int) -> None:
    """Print total seconds and all format representations."""
    print(f"{'seconds':>8} : {format_seconds(total)}")
    print(f"{'human':>8} : {format_human(total)}")
    print(f"{'iso':>8} : {format_iso(total)}")
    print(f"{'colon':>8} : {format_colon(total)}")


# ---------------------------------------------------------------------------
#  Subcommand handlers
# ---------------------------------------------------------------------------

def cmd_parse(args: argparse.Namespace) -> None:
    """Parse one duration string → all formats."""
    total = parse_duration(args.input)
    emit_all_formats(total)


def cmd_add(args: argparse.Namespace) -> None:
    """Sum multiple durations → all formats."""
    total = 0
    for dur in args.durations:
        total += parse_duration(dur)
    emit_all_formats(total)


def cmd_compare(args: argparse.Namespace) -> None:
    """Compare two durations for equality."""
    a = parse_duration(args.a)
    b = parse_duration(args.b)
    if a == b:
        print(f"EQUAL: both are {format_human(a)} ({a} seconds)")
        sys.exit(0)
    else:
        a_fmt = format_human(a)
        b_fmt = format_human(b)
        print(f"NOT EQUAL: {args.a!r} → {a_fmt} ({a}s)  ≠  {args.b!r} → {b_fmt} ({b}s)")
        sys.exit(1)


def cmd_format(args: argparse.Namespace) -> None:
    """Format raw seconds into a specific style."""
    total = args.seconds
    style = args.style.lower()
    formatters = {
        "human": format_human,
        "iso": format_iso,
        "colon": format_colon,
        "seconds": format_seconds,
    }
    if style not in formatters:
        print(f"Unknown style: {style!r}. Choose from: human, iso, colon, seconds", file=sys.stderr)
        sys.exit(2)
    print(formatters[style](total))


# ---------------------------------------------------------------------------
#  CLI entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="dur-decode",
        description="Parse, convert, and compare duration strings.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  dur-decode parse --input '2h30m15s'
  dur-decode parse --input 'PT2H30M15S'
  dur-decode parse --input '9015s'
  dur-decode add --durations 1h30m 45m 2h
  dur-decode compare --a 2h --b 120m
  dur-decode format --seconds 9015 --style human
        """.strip(),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # parse
    p = sub.add_parser("parse", help="Parse a duration string → all formats")
    p.add_argument("--input", required=True, help="Duration string (e.g. 2h30m15s, PT2H30M15S, 9015s)")
    p.set_defaults(func=cmd_parse)

    # add
    p = sub.add_parser("add", help="Sum multiple duration strings")
    p.add_argument("--durations", nargs="+", required=True, help="One or more duration strings")
    p.set_defaults(func=cmd_add)

    # compare
    p = sub.add_parser("compare", help="Check if two durations are equal")
    p.add_argument("--a", required=True, help="First duration")
    p.add_argument("--b", required=True, help="Second duration")
    p.set_defaults(func=cmd_compare)

    # format
    p = sub.add_parser("format", help="Convert raw seconds into a target style")
    p.add_argument("--seconds", type=int, required=True, help="Total seconds")
    p.add_argument("--style", required=True, choices=["human", "iso", "colon", "seconds"],
                   help="Output format")
    p.set_defaults(func=cmd_format)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
