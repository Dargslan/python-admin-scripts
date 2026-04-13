# dargslan-raid-monitor

Linux RAID array health checker — monitor mdadm status, detect degraded arrays, track rebuild progress, and audit disk health.

## Installation

```bash
pip install dargslan-raid-monitor
```

## Usage

```bash
dargslan-raid report          # Full RAID health report
dargslan-raid arrays          # List all RAID arrays
dargslan-raid rebuild         # Show rebuild progress
dargslan-raid audit           # Issues only
dargslan-raid json            # JSON output
```

## Features

- Parse /proc/mdstat for RAID array status
- Detect degraded and inactive arrays
- Track rebuild/resync progress with ETA
- Identify faulty and spare disks
- Zero dependencies — pure Python

## Part of dargslan-toolkit

Install all 48 Linux sysadmin tools: `pip install dargslan-toolkit`

## Links

- [Free Linux Cheat Sheets](https://dargslan.com/cheat-sheets)
- [Linux & DevOps Books](https://dargslan.com/books)
- [Blog & Tutorials](https://dargslan.com/blog)

## License

MIT
