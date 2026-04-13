# dargslan-cron-audit

**Linux Crontab Auditor** — Audit crontab entries, detect security issues, validate schedules, find misconfigurations. Zero external dependencies.

[![PyPI version](https://img.shields.io/pypi/v/dargslan-cron-audit)](https://pypi.org/project/dargslan-cron-audit/)

## Installation

```bash
pip install dargslan-cron-audit
```

## CLI Usage

```bash
dargslan-cron report    # Full cron audit report
dargslan-cron list      # List all cron entries
dargslan-cron issues    # Show issues only
dargslan-cron json      # JSON output
```

## Python API

```python
from dargslan_cron_audit import CronAudit

ca = CronAudit()
ca.print_report()

entries = ca.get_user_crontab()
sys_entries = ca.get_system_crontabs()
issues = ca.audit()
```

## What It Checks

- Missing output redirection (cron mail accumulation)
- Commands pointing to non-existent paths
- High-frequency jobs (every minute)
- Root-running jobs
- Dangerous commands (rm -rf, chmod 777)
- Schedule validation

## More Resources

- [Linux eBooks](https://dargslan.com/books) | [Cheat Sheets](https://dargslan.com/cheat-sheets) | [Blog](https://dargslan.com/blog)

## License

MIT — [Dargslan](https://dargslan.com)
