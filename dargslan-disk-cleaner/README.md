# dargslan-disk-cleaner

**Linux Disk Usage Analyzer & Cleaner** — Find large files, analyze disk usage, scan temp directories, and identify cleanup opportunities. Zero external dependencies.

[![PyPI version](https://img.shields.io/pypi/v/dargslan-disk-cleaner)](https://pypi.org/project/dargslan-disk-cleaner/)

## Installation

```bash
pip install dargslan-disk-cleaner
```

## CLI Usage

```bash
dargslan-disk report           # Full disk usage report
dargslan-disk large /home -m 50  # Files > 50MB
dargslan-disk old /var/log -d 60 # Files older than 60 days
dargslan-disk dirs /            # Directory sizes
dargslan-disk temp              # Temp directory usage
dargslan-disk json              # JSON output
```

## Python API

```python
from dargslan_disk_cleaner import DiskCleaner

dc = DiskCleaner()
dc.print_report()

large = dc.find_large_files("/home", min_size_mb=50)
old = dc.find_old_files("/var/log", days=90)
dirs = dc.dir_sizes("/")
dupes = dc.find_duplicates("/home", min_size_mb=1)
```

## More Resources

- [Linux eBooks](https://dargslan.com/books) | [Cheat Sheets](https://dargslan.com/cheat-sheets) | [Blog](https://dargslan.com/blog)

## License

MIT — [Dargslan](https://dargslan.com)
