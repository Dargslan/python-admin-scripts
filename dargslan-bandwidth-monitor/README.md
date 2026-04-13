# dargslan-bandwidth-monitor

**Network Bandwidth Monitor** — Track interface statistics, throughput, and traffic from /proc/net/dev. Real-time speed tests. Zero external dependencies.

[![PyPI version](https://img.shields.io/pypi/v/dargslan-bandwidth-monitor)](https://pypi.org/project/dargslan-bandwidth-monitor/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install dargslan-bandwidth-monitor
```

## CLI Usage

```bash
dargslan-bw report            # Full bandwidth report
dargslan-bw stats             # Interface statistics
dargslan-bw speed             # Real-time throughput test
dargslan-bw speed -d 5        # 5-second speed test
dargslan-bw total             # Total traffic counters
dargslan-bw errors            # Interface errors/drops
dargslan-bw json              # JSON output
```

## Python API

```python
from dargslan_bandwidth_monitor import BandwidthMonitor
bm = BandwidthMonitor()
stats = bm.get_stats()
throughput = bm.measure_throughput(duration=3)
bm.print_report()
```

## More from Dargslan

- [Dargslan.com](https://dargslan.com) — Linux & DevOps eBook Store
- [Free Cheat Sheets](https://dargslan.com/cheat-sheets)
- [Blog & Tutorials](https://dargslan.com/blog)

## License

MIT — see [LICENSE](LICENSE)
