# dargslan-redis-health

**Redis Server Health Checker** — Monitor memory, persistence (RDB/AOF), replication, slow log, and connected clients. Zero external dependencies.

[![PyPI version](https://img.shields.io/pypi/v/dargslan-redis-health)](https://pypi.org/project/dargslan-redis-health/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install dargslan-redis-health
```

## CLI Usage

```bash
dargslan-redis report         # Full health report
dargslan-redis memory         # Memory usage
dargslan-redis persistence    # RDB/AOF status
dargslan-redis replication    # Replication info
dargslan-redis clients        # Client connections
dargslan-redis json           # JSON output
```

## Python API

```python
from dargslan_redis_health import RedisHealth
rh = RedisHealth(host="localhost", port=6379)
mem = rh.memory_info()
issues = rh.audit()
rh.print_report()
```

## More from Dargslan

- [Dargslan.com](https://dargslan.com) — Linux & DevOps eBook Store
- [Free Cheat Sheets](https://dargslan.com/cheat-sheets)
- [Blog & Tutorials](https://dargslan.com/blog)

## License

MIT — see [LICENSE](LICENSE)
