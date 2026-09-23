from __future__ import annotations

import argparse
import sqlite3
from datetime import datetime
from pathlib import Path

DEFAULT_DB = Path("downtime.sqlite3")
TIME_FORMAT = "%Y-%m-%d %H:%M"


def connect_db(path: str | Path = DEFAULT_DB) -> sqlite3.Connection:
    connection = sqlite3.connect(Path(path))
    connection.row_factory = sqlite3.Row
    return connection


def init_db(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS downtime_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            machine_name TEXT NOT NULL,
            reason TEXT NOT NULL,
            started_at TEXT NOT NULL,
            ended_at TEXT NOT NULL,
            duration_minutes INTEGER NOT NULL
        )
        """
    )
    connection.commit()


def parse_time(value: str) -> datetime:
    try:
        return datetime.strptime(value, TIME_FORMAT)
    except ValueError as exc:
        raise ValueError(
            f"Invalid date/time: {value!r}. Expected format: YYYY-MM-DD HH:MM"
        ) from exc


def calculate_duration_minutes(started_at: str, ended_at: str) -> int:
    start = parse_time(started_at)
    end = parse_time(ended_at)

    if end <= start:
        raise ValueError("End time must be after start time.")

    return int((end - start).total_seconds() // 60)


def add_event(
    connection: sqlite3.Connection,
    machine_name: str,
    reason: str,
    started_at: str,
    ended_at: str,
) -> int:
    machine_name = machine_name.strip()
    reason = reason.strip()

    if not machine_name:
        raise ValueError("Machine name cannot be empty.")
    if not reason:
        raise ValueError("Reason cannot be empty.")

    duration = calculate_duration_minutes(started_at, ended_at)

    cursor = connection.execute(
        """
        INSERT INTO downtime_events (
            machine_name,
            reason,
            started_at,
            ended_at,
            duration_minutes
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (machine_name, reason, started_at, ended_at, duration),
    )
    connection.commit()
    return int(cursor.lastrowid)


def list_events(connection: sqlite3.Connection) -> list[sqlite3.Row]:
    return list(
        connection.execute(
            """
            SELECT id, machine_name, reason, started_at, ended_at, duration_minutes
            FROM downtime_events
            ORDER BY id DESC
            """
        )
    )


def total_downtime(
    connection: sqlite3.Connection,
    machine_name: str | None = None,
) -> int:
    if machine_name:
        row = connection.execute(
            """
            SELECT COALESCE(SUM(duration_minutes), 0) AS total
            FROM downtime_events
            WHERE machine_name = ? COLLATE NOCASE
            """,
            (machine_name.strip(),),
        ).fetchone()
    else:
        row = connection.execute(
            """
            SELECT COALESCE(SUM(duration_minutes), 0) AS total
            FROM downtime_events
            """
        ).fetchone()

    return int(row["total"])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Track machine downtime events with SQLite."
    )
    parser.add_argument(
        "--db",
        default=str(DEFAULT_DB),
        help="SQLite database path (default: downtime.sqlite3)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a downtime event")
    add_parser.add_argument("machine")
    add_parser.add_argument("reason")
    add_parser.add_argument("start", help="YYYY-MM-DD HH:MM")
    add_parser.add_argument("end", help="YYYY-MM-DD HH:MM")

    subparsers.add_parser("list", help="List downtime events")

    total_parser = subparsers.add_parser(
        "total",
        help="Show total downtime in minutes",
    )
    total_parser.add_argument(
        "--machine",
        default=None,
        help="Optional machine name filter",
    )

    return parser


def main() -> None:
    args = build_parser().parse_args()

    try:
        connection = connect_db(args.db)
        init_db(connection)

        if args.command == "add":
            event_id = add_event(
                connection,
                args.machine,
                args.reason,
                args.start,
                args.end,
            )
            print(f"Downtime event added with ID {event_id}.")

        elif args.command == "list":
            events = list_events(connection)

            if not events:
                print("No downtime events recorded.")

            for event in events:
                print(
                    f"#{event['id']} | {event['machine_name']} | "
                    f"{event['started_at']} -> {event['ended_at']} | "
                    f"{event['duration_minutes']} min | {event['reason']}"
                )

        elif args.command == "total":
            total = total_downtime(connection, args.machine)
            if args.machine:
                print(f"Total downtime for {args.machine}: {total} minutes")
            else:
                print(f"Total downtime: {total} minutes")

    except (sqlite3.Error, ValueError) as exc:
        raise SystemExit(f"Error: {exc}") from exc
    finally:
        if "connection" in locals():
            connection.close()


if __name__ == "__main__":
    main()
