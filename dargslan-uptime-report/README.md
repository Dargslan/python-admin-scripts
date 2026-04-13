# dargslan-uptime-report

System uptime and availability reporter — reboot history, crash analysis, OOM kill detection, and availability percentage.

## Installation

```bash
pip install dargslan-uptime-report
```

## Usage

```bash
dargslan-uptime report        # Full uptime & availability report
dargslan-uptime uptime        # Current uptime
dargslan-uptime reboots       # Reboot history
dargslan-uptime crashes       # Crash event analysis
dargslan-uptime load          # Current load average
dargslan-uptime audit         # Issues only
dargslan-uptime json          # JSON output
```

## Features

- Current uptime with boot time
- 30-day availability percentage calculation
- Reboot history with kernel versions
- Kernel panic and OOM kill detection
- Load average monitoring vs CPU count
- Frequent reboot detection
- Zero dependencies — pure Python

## Part of dargslan-toolkit

Install all 48 Linux sysadmin tools: `pip install dargslan-toolkit`

## Links

- [Free Linux Cheat Sheets](https://dargslan.com/cheat-sheets)
- [Linux & DevOps Books](https://dargslan.com/books)
- [Blog & Tutorials](https://dargslan.com/blog)

## License

MIT
