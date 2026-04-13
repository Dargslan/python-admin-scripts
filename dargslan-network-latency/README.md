# dargslan-network-latency

Network latency tester — ping analysis, jitter measurement, traceroute, TCP latency, and multi-host comparison.

## Installation

```bash
pip install dargslan-network-latency
```

## Usage

```bash
dargslan-latency report              # Test default hosts
dargslan-latency ping 8.8.8.8        # Detailed ping stats
dargslan-latency tcp example.com 443 # TCP connection latency
dargslan-latency trace 8.8.8.8       # Traceroute
dargslan-latency compare 8.8.8.8 1.1.1.1 9.9.9.9  # Compare
dargslan-latency audit               # Issues only
dargslan-latency json                # JSON output
```

## Features

- ICMP ping with jitter and packet loss
- TCP connection latency measurement
- Traceroute with per-hop timing
- Multi-host latency comparison (sorted)
- High latency and packet loss alerting
- Zero dependencies — pure Python

## Part of dargslan-toolkit

Install all 54 Linux sysadmin tools: `pip install dargslan-toolkit`

## Links

- [Free Linux Cheat Sheets](https://dargslan.com/cheat-sheets)
- [Linux & DevOps Books](https://dargslan.com/books)

## License

MIT
