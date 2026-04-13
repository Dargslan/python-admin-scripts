# dargslan-mysql-health

**MySQL/MariaDB Health Checker** — Monitor connections, slow queries, replication status, and database sizes. Zero external dependencies (uses `mysql` CLI client).

[![PyPI version](https://img.shields.io/pypi/v/dargslan-mysql-health)](https://pypi.org/project/dargslan-mysql-health/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install dargslan-mysql-health
```

## CLI Usage

```bash
# Full health report
dargslan-mysql report

# Connection statistics
dargslan-mysql connections

# Slow query info
dargslan-mysql slow

# Database sizes
dargslan-mysql databases

# Replication status
dargslan-mysql replication

# All issues
dargslan-mysql issues

# JSON output
dargslan-mysql json

# Custom connection
dargslan-mysql report -H 10.0.0.5 -P 3306 -u admin
```

## Python API

```python
from dargslan_mysql_health import MySQLHealth

mh = MySQLHealth(host='localhost', user='root')

# Full audit
issues = mh.audit()

# Specific checks
conn = mh.connection_status()
slow = mh.slow_queries()
dbs = mh.database_sizes()
repl = mh.replication_status()

# Server info
info = mh.server_info()

# Formatted report
mh.print_report()
```

## Health Checks

| Check | Severity | Description |
|-------|----------|-------------|
| Connection usage >80% | Warning | Too many active connections |
| Connection usage >95% | Critical | Nearly maxed out connections |
| Slow query log off | Info | Slow query logging disabled |
| High slow queries | Warning | >1000 slow queries recorded |
| Replication broken | Critical | IO/SQL thread not running |
| Replication lag | Warning | >60 seconds behind master |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `MYSQL_USER` | Default MySQL username |
| `MYSQL_PASSWORD` | Default MySQL password |

## More from Dargslan

- [Dargslan.com](https://dargslan.com) — Linux & DevOps eBook Store
- [Free Cheat Sheets](https://dargslan.com/cheat-sheets) — 300+ downloadable PDFs
- [Blog & Tutorials](https://dargslan.com/blog) — 300+ in-depth articles
- [All Python Tools](https://pypi.org/user/dargslan/) — 20+ CLI packages

## License

MIT — see [LICENSE](LICENSE)
