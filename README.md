# Machine Downtime Tracker

A small Python CLI that records machine downtime events in SQLite and calculates downtime duration.

## Features

- Record machine name, reason, start time and end time
- Calculate downtime automatically in minutes
- Store records in SQLite
- List all downtime events
- Calculate total downtime
- Filter total downtime by machine
- Validate invalid timestamps and input
- Automated tests with `unittest`
- GitHub Actions test workflow

## Why this project?

Downtime tracking is a common industrial maintenance task. This project introduces a lightweight relational database workflow while staying small enough to understand and extend.

## Example

Add a downtime event:

```bash
python downtime_tracker.py add CNC-01 "Hydraulic fault" "2026-09-23 14:20" "2026-09-23 14:47"
```

List events:

```bash
python downtime_tracker.py list
```

Example:

```text
#1 | CNC-01 | 2026-09-23 14:20 -> 2026-09-23 14:47 | 27 min | Hydraulic fault
```

Show total downtime:

```bash
python downtime_tracker.py total
```

Filter by machine:

```bash
python downtime_tracker.py total --machine CNC-01
```

## Run tests

```bash
python -m unittest -v
```

## Concepts practiced

- `sqlite3`
- SQL tables, inserts and queries
- `datetime`
- `pathlib`
- `argparse`
- validation and exceptions
- unit testing
- GitHub Actions

This project uses only Python's standard library.
