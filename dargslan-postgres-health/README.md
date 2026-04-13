# dargslan-postgres-health

**PostgreSQL Health Checker** — Monitor connections, bloat, vacuum status, locks, replication lag, and long-running queries. Zero external dependencies.

[![PyPI version](https://img.shields.io/pypi/v/dargslan-postgres-health)](https://pypi.org/project/dargslan-postgres-health/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install dargslan-postgres-health
```

## CLI Usage

```bash
dargslan-pg report            # Full health report
dargslan-pg connections       # Connection stats
dargslan-pg databases         # Database sizes
dargslan-pg bloat             # Table bloat analysis
dargslan-pg vacuum            # Vacuum status
dargslan-pg locks             # Waiting locks
dargslan-pg queries           # Long-running queries
dargslan-pg replication       # Replication status
dargslan-pg json              # JSON output
```

## Python API

```python
from dargslan_postgres_health import PostgresHealth
ph = PostgresHealth(host="localhost", user="postgres")
conn = ph.connection_status()
bloat = ph.table_bloat()
ph.print_report()
```

## More from Dargslan

- [Dargslan.com](https://dargslan.com) — Linux & DevOps eBook Store
- [Free Cheat Sheets](https://dargslan.com/cheat-sheets)
- [Blog & Tutorials](https://dargslan.com/blog)

## License

MIT — see [LICENSE](LICENSE)
