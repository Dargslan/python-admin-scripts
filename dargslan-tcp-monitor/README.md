# dargslan-tcp-monitor

**TCP Connection Monitor** — Track connection states, listening ports, per-IP statistics, and TIME_WAIT buildup. Zero external dependencies.

[![PyPI version](https://img.shields.io/pypi/v/dargslan-tcp-monitor)](https://pypi.org/project/dargslan-tcp-monitor/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install dargslan-tcp-monitor
```

## CLI Usage

```bash
dargslan-tcp report            # Full TCP connection report
dargslan-tcp states            # Connection state counts
dargslan-tcp listen            # Listening ports
dargslan-tcp established       # Active connections
dargslan-tcp per-ip            # Connections per remote IP
dargslan-tcp timewait          # TIME_WAIT count
dargslan-tcp json              # JSON output
```

## Python API

```python
from dargslan_tcp_monitor import TCPMonitor
tm = TCPMonitor()
states = tm.get_state_counts()
listening = tm.get_listening_ports()
tm.print_report()
```

## More from Dargslan

- [Dargslan.com](https://dargslan.com) — Linux & DevOps eBook Store
- [Free Cheat Sheets](https://dargslan.com/cheat-sheets)
- [Blog & Tutorials](https://dargslan.com/blog)

## License

MIT — see [LICENSE](LICENSE)
