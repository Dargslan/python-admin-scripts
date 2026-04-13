# dargslan-port-monitor

**Linux Open Port Monitor** — Monitor listening ports, detect exposed services, check port availability. Reads from ss/netstat and /proc/net. Zero external dependencies.

[![PyPI version](https://img.shields.io/pypi/v/dargslan-port-monitor)](https://pypi.org/project/dargslan-port-monitor/)

## Installation

```bash
pip install dargslan-port-monitor
```

## CLI Usage

```bash
dargslan-ports report              # Full port report
dargslan-ports tcp                 # TCP listening ports
dargslan-ports udp                 # UDP listening ports
dargslan-ports exposed             # Externally exposed ports
dargslan-ports check 192.168.1.1 22  # Check specific port
dargslan-ports json                # JSON output
```

## Python API

```python
from dargslan_port_monitor import PortMonitor

pm = PortMonitor()
pm.print_report()

tcp = pm.get_listening_ports()
exposed = pm.find_exposed()
unexpected = pm.find_unexpected(expected_ports=[22, 80, 443])
result = pm.check_port("192.168.1.1", 22)
```

## More Resources

- [Linux eBooks](https://dargslan.com/books) | [Cheat Sheets](https://dargslan.com/cheat-sheets) | [Blog](https://dargslan.com/blog)

## License

MIT — [Dargslan](https://dargslan.com)
