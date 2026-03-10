"""CLI for viewing local LLMSpend data.

Usage:
    llmspend stats                  # Last 24h summary
    llmspend stats --last 7d        # Last 7 days
    llmspend stats --by model       # Group by model
    llmspend stats --by feature     # Group by feature
    llmspend top                    # Top 10 most expensive calls
"""

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timedelta, timezone


def get_db_path() -> str:
    return os.environ.get("LLMSPEND_DB", os.path.expanduser("~/.llmspend/events.db"))


def parse_duration(s: str) -> timedelta:
    """Parse duration string like '7d', '24h', '30m'."""
    if not s:
        return timedelta(hours=24)
    unit = s[-1].lower()
    value = int(s[:-1])
    if unit == "d":
        return timedelta(days=value)
    if unit == "h":
        return timedelta(hours=value)
    if unit == "m":
        return timedelta(minutes=value)
    return timedelta(hours=24)


def cmd_stats(args):
    """Show cost summary."""
    db_path = get_db_path()
    if not os.path.exists(db_path):
        print("No data yet. Start using LLMSpend to track API calls.")
        return

    conn = sqlite3.connect(db_path)
    duration = parse_duration(args.last)
    since = (datetime.now(timezone.utc) - duration).isoformat()

    group_by = args.by or "project"
    valid_groups = {"model", "feature", "project", "provider", "user_id"}
    if group_by not in valid_groups:
        print(f"Invalid --by value. Choose from: {', '.join(valid_groups)}")
        return

    rows = conn.execute(f"""
        SELECT {group_by}, COUNT(*) as calls,
               SUM(tokens_in) as total_in, SUM(tokens_out) as total_out,
               SUM(cost_usd) as total_cost,
               AVG(latency_ms) as avg_latency
        FROM events
        WHERE timestamp >= ?
        GROUP BY {group_by}
        ORDER BY total_cost DESC
    """, (since,)).fetchall()

    if not rows:
        print(f"No calls in the last {args.last or '24h'}.")
        return

    total_cost = sum(r[4] or 0 for r in rows)
    total_calls = sum(r[1] for r in rows)

    print(f"\n  LLMSpend — Last {args.last or '24h'}")
    print(f"  {'─' * 50}")
    print(f"  Total: ${total_cost:.4f} across {total_calls} calls\n")
    print(f"  {'Group':<25} {'Calls':>6} {'Cost':>10} {'Avg ms':>8}")
    print(f"  {'─' * 25} {'─' * 6} {'─' * 10} {'─' * 8}")

    for row in rows:
        name = row[0] or "(none)"
        calls = row[1]
        cost = row[4] or 0
        latency = int(row[5] or 0)
        print(f"  {name:<25} {calls:>6} ${cost:>9.4f} {latency:>7}ms")

    print()
    conn.close()


def cmd_top(args):
    """Show most expensive individual calls."""
    db_path = get_db_path()
    if not os.path.exists(db_path):
        print("No data yet.")
        return

    conn = sqlite3.connect(db_path)
    limit = args.n or 10

    rows = conn.execute("""
        SELECT timestamp, model, tokens_in, tokens_out, cost_usd, latency_ms, feature
        FROM events
        ORDER BY cost_usd DESC
        LIMIT ?
    """, (limit,)).fetchall()

    if not rows:
        print("No calls recorded.")
        return

    print(f"\n  Top {limit} most expensive calls")
    print(f"  {'─' * 70}")
    print(f"  {'Time':<20} {'Model':<25} {'Tokens':>10} {'Cost':>10} {'Feature':<12}")
    print(f"  {'─' * 20} {'─' * 25} {'─' * 10} {'─' * 10} {'─' * 12}")

    for row in rows:
        ts = row[0][:19] if row[0] else "?"
        model = (row[1] or "?")[:24]
        tokens = (row[2] or 0) + (row[3] or 0)
        cost = row[4] or 0
        feature = (row[6] or "-")[:11]
        print(f"  {ts:<20} {model:<25} {tokens:>10} ${cost:>9.6f} {feature:<12}")

    print()
    conn.close()


def cmd_export(args):
    """Export events as JSON."""
    db_path = get_db_path()
    if not os.path.exists(db_path):
        print("No data yet.")
        return

    conn = sqlite3.connect(db_path)
    rows = conn.execute("SELECT raw_json FROM events ORDER BY timestamp DESC").fetchall()
    events = [json.loads(r[0]) for r in rows if r[0]]
    print(json.dumps(events, indent=2))
    conn.close()


def main():
    parser = argparse.ArgumentParser(prog="llmspend", description="LLM cost tracker CLI")
    sub = parser.add_subparsers(dest="command")

    stats_p = sub.add_parser("stats", help="Show cost summary")
    stats_p.add_argument("--last", default="24h", help="Time window (e.g. 7d, 24h, 30m)")
    stats_p.add_argument("--by", default="model", help="Group by: model, feature, project, provider, user_id")

    top_p = sub.add_parser("top", help="Most expensive calls")
    top_p.add_argument("-n", type=int, default=10, help="Number of results")

    sub.add_parser("export", help="Export all events as JSON")

    args = parser.parse_args()

    if args.command == "stats":
        cmd_stats(args)
    elif args.command == "top":
        cmd_top(args)
    elif args.command == "export":
        cmd_export(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
