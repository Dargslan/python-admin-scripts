# dargslan-process-killer

Zombie and runaway process hunter — detect resource hogs, zombie processes, and long-running orphans.

## Installation

```bash
pip install dargslan-process-killer
```

## Usage

```bash
dargslan-prockill report    # Full process analysis
dargslan-prockill zombies   # Find zombie processes
dargslan-prockill hogs      # Resource hog processes
dargslan-prockill topcpu    # Top CPU consumers
dargslan-prockill topmem    # Top memory consumers
dargslan-prockill long      # Long-running (>24h)
dargslan-prockill audit     # Issues only
dargslan-prockill json      # JSON output
```

## Features

- Zombie process detection with parent PID
- CPU and memory resource hog finder
- Top CPU/memory consumer listing
- Long-running process detection (configurable threshold)
- Read-only by default (no processes killed without confirmation)
- Zero dependencies — pure Python

## Part of dargslan-toolkit

Install all 54 Linux sysadmin tools: `pip install dargslan-toolkit`

## Links

- [Free Linux Cheat Sheets](https://dargslan.com/cheat-sheets)
- [Linux & DevOps Books](https://dargslan.com/books)

## License

MIT
