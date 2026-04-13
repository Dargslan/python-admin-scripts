# dargslan-log-rotate

**Linux Log Rotation Analyzer** — Analyze logrotate configuration, find large/unrotated logs, monitor log disk usage. Zero external dependencies.

[![PyPI version](https://img.shields.io/pypi/v/dargslan-log-rotate)](https://pypi.org/project/dargslan-log-rotate/)

## Installation

```bash
pip install dargslan-log-rotate
```

## CLI Usage

```bash
dargslan-logrot report         # Full log rotation report
dargslan-logrot configs        # Show logrotate configurations
dargslan-logrot usage          # Log directory usage
dargslan-logrot large -m 50    # Find logs > 50MB
dargslan-logrot issues         # Show issues
dargslan-logrot json           # JSON output
```

## Python API

```python
from dargslan_log_rotate import LogRotateAudit

lr = LogRotateAudit()
lr.print_report()

configs = lr.parse_logrotate_entries()
large = lr.find_large_logs(min_size_mb=50)
usage = lr.log_dir_usage()
issues = lr.audit()
```

## More Resources

- [Linux eBooks](https://dargslan.com/books) | [Cheat Sheets](https://dargslan.com/cheat-sheets) | [Blog](https://dargslan.com/blog)

## License

MIT — [Dargslan](https://dargslan.com)
