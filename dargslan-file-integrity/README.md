# dargslan-file-integrity

File integrity checker — hash-based change detection, baseline comparison, and tamper alerting for critical system files.

## Installation

```bash
pip install dargslan-file-integrity
```

## Usage

```bash
dargslan-fim baseline         # Create baseline snapshot
dargslan-fim check            # Compare with baseline
dargslan-fim report           # Full integrity report
dargslan-fim scan             # Scan and list hashes
dargslan-fim hash /etc/passwd # Hash a single file
dargslan-fim audit            # Issues only
dargslan-fim json             # JSON output
```

## Features

- SHA-256 hash-based file integrity monitoring
- Baseline snapshot creation and comparison
- Detect modified, added, and removed files
- Permission change tracking
- World-writable file detection
- Default monitoring of critical system files (/etc/passwd, /etc/shadow, etc.)
- Zero dependencies — pure Python

## Part of dargslan-toolkit

Install all 48 Linux sysadmin tools: `pip install dargslan-toolkit`

## Links

- [Free Linux Cheat Sheets](https://dargslan.com/cheat-sheets)
- [Linux & DevOps Books](https://dargslan.com/books)
- [Blog & Tutorials](https://dargslan.com/blog)

## License

MIT
