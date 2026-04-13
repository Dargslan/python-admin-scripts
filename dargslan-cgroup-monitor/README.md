# dargslan-cgroup-monitor

**Linux Cgroup Resource Monitor** — Track CPU, memory, and I/O limits for containers and system slices. Supports cgroups v1 and v2. Zero external dependencies.

[![PyPI version](https://img.shields.io/pypi/v/dargslan-cgroup-monitor)](https://pypi.org/project/dargslan-cgroup-monitor/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install dargslan-cgroup-monitor
```

## CLI Usage

```bash
dargslan-cgroup report        # Full cgroup resource report
dargslan-cgroup list          # List all active cgroups
dargslan-cgroup slices        # System slices and services
dargslan-cgroup containers    # Container cgroups only
dargslan-cgroup issues        # Resource limit issues
dargslan-cgroup json          # JSON output
```

## Python API

```python
from dargslan_cgroup_monitor import CgroupMonitor
cm = CgroupMonitor()
cgroups = cm.list_cgroups()
containers = cm.get_container_cgroups()
cm.print_report()
```

## More from Dargslan

- [Dargslan.com](https://dargslan.com) — Linux & DevOps eBook Store
- [Free Cheat Sheets](https://dargslan.com/cheat-sheets)
- [Blog & Tutorials](https://dargslan.com/blog)

## License

MIT — see [LICENSE](LICENSE)
