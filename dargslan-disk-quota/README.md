# dargslan-disk-quota

Linux disk quota monitor — user and group quota tracking, usage alerts, and filesystem capacity reporting.

## Installation

```bash
pip install dargslan-disk-quota
```

## Usage

```bash
dargslan-quota report    # Full quota and disk report
dargslan-quota users     # User quota listing
dargslan-quota groups    # Group quota listing
dargslan-quota disk      # Filesystem usage
dargslan-quota audit     # Issues only
dargslan-quota json      # JSON output
```

## Features

- User and group quota monitoring (repquota)
- Over-limit detection (soft and hard limits)
- Filesystem capacity monitoring with visual bars
- High-usage alerting (85% warning, 95% critical)
- Zero dependencies — pure Python

## Part of dargslan-toolkit

Install all 54 Linux sysadmin tools: `pip install dargslan-toolkit`

## Links

- [Free Linux Cheat Sheets](https://dargslan.com/cheat-sheets)
- [Linux & DevOps Books](https://dargslan.com/books)

## License

MIT
