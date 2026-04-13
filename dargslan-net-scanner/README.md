# dargslan-net-scanner

**Lightweight Network Scanner** — Ping sweep, TCP port scan, and service detection. Zero dependencies, pure Python.

[![PyPI version](https://img.shields.io/pypi/v/dargslan-net-scanner)](https://pypi.org/project/dargslan-net-scanner/)

## Installation

```bash
pip install dargslan-net-scanner
```

## Usage

```python
from dargslan_net_scanner import NetScanner

scanner = NetScanner()

# Ping sweep a subnet
alive = scanner.ping_sweep("192.168.1.0/24")

# Port scan
open_ports = scanner.port_scan("192.168.1.1", ports=[22, 80, 443, 3306, 5432, 8080])

# Quick scan common ports
results = scanner.quick_scan("10.0.0.1")

# Full report
report = scanner.scan_host("192.168.1.1")
```

```bash
# CLI
dargslan-netscan ping 192.168.1.0/24
dargslan-netscan ports 192.168.1.1 -p 22,80,443
dargslan-netscan quick 10.0.0.1
```

## Resources

- [Linux & DevOps eBooks](https://dargslan.com/books)
- [Free Cheat Sheets](https://dargslan.com/cheat-sheets)
- [Tutorials](https://dargslan.com/blog)

MIT — **[Dargslan](https://dargslan.com)**
