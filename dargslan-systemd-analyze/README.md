# dargslan-systemd-analyze

**Systemd Boot Time Analyzer** — Measure service startup times, find slow units, analyze critical chain, and optimize boot performance. Zero external dependencies.

[![PyPI version](https://img.shields.io/pypi/v/dargslan-systemd-analyze)](https://pypi.org/project/dargslan-systemd-analyze/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install dargslan-systemd-analyze
```

## CLI Usage

```bash
dargslan-boottime report       # Full boot analysis
dargslan-boottime time         # Boot time summary
dargslan-boottime blame        # Slowest units
dargslan-boottime chain        # Critical chain
dargslan-boottime slow -t 10   # Units over 10s threshold
dargslan-boottime timers       # Active timers
dargslan-boottime json         # JSON output
```

## Python API

```python
from dargslan_systemd_analyze import SystemdAnalyze
sa = SystemdAnalyze()
boot = sa.get_boot_time()
slow = sa.get_slow_units(threshold_sec=5.0)
sa.print_report()
```

## More from Dargslan

- [Dargslan.com](https://dargslan.com) — Linux & DevOps eBook Store
- [Free Cheat Sheets](https://dargslan.com/cheat-sheets)
- [Blog & Tutorials](https://dargslan.com/blog)

## License

MIT — see [LICENSE](LICENSE)
