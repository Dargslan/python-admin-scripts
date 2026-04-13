# dargslan-nfs-health

**NFS Mount Health Checker** — Detect stale mounts, measure latency, audit exports, and monitor NFS statistics. Zero external dependencies.

[![PyPI version](https://img.shields.io/pypi/v/dargslan-nfs-health)](https://pypi.org/project/dargslan-nfs-health/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install dargslan-nfs-health
```

## CLI Usage

```bash
dargslan-nfs report           # Full NFS health report
dargslan-nfs mounts           # List NFS mounts with status
dargslan-nfs exports          # Show NFS exports
dargslan-nfs stats            # NFS client statistics
dargslan-nfs throughput -m /mnt/nfs  # I/O throughput test
dargslan-nfs json             # JSON output
```

## Python API

```python
from dargslan_nfs_health import NFSHealth
nh = NFSHealth()
mounts = nh.check_all_mounts()
issues = nh.audit()
nh.print_report()
```

## More from Dargslan

- [Dargslan.com](https://dargslan.com) — Linux & DevOps eBook Store
- [Free Cheat Sheets](https://dargslan.com/cheat-sheets)
- [Blog & Tutorials](https://dargslan.com/blog)

## License

MIT — see [LICENSE](LICENSE)
