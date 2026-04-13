# dargslan-backup-monitor

**Linux Backup Monitor** — Monitor backup status, check freshness, verify checksums, and track backup disk usage. Zero external dependencies.

[![PyPI version](https://img.shields.io/pypi/v/dargslan-backup-monitor)](https://pypi.org/project/dargslan-backup-monitor/)

## Installation

```bash
pip install dargslan-backup-monitor
```

## CLI Usage

```bash
dargslan-backup report /backup        # Full backup report
dargslan-backup check /backup --max-age 48  # Check freshness
dargslan-backup list /var/backups     # List backup files
dargslan-backup checksum /backup/db.sql.gz  # Verify integrity
dargslan-backup json                  # JSON output
```

## Python API

```python
from dargslan_backup_monitor import BackupMonitor

bm = BackupMonitor(backup_dirs=["/backup", "/var/backups"])
bm.print_report()

backups = bm.find_backups("/backup")
freshness = bm.check_freshness(max_age_hours=24)
checksum = bm.verify_checksum("/backup/db.tar.gz")
usage = bm.disk_usage_trend()
```

## Supported Formats

.tar, .tar.gz, .tgz, .tar.bz2, .tar.xz, .zip, .sql, .sql.gz, .dump, .bak, .backup

## More Resources

- [Linux eBooks](https://dargslan.com/books) | [Cheat Sheets](https://dargslan.com/cheat-sheets) | [Blog](https://dargslan.com/blog)

## License

MIT — [Dargslan](https://dargslan.com)
