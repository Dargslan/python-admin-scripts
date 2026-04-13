# dargslan-ip-geo

**IP Geolocation & WHOIS Lookup** — Find country, ISP, abuse contact, and network info for any IP address. Reverse DNS, bulk lookups. Zero external dependencies.

[![PyPI version](https://img.shields.io/pypi/v/dargslan-ip-geo)](https://pypi.org/project/dargslan-ip-geo/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install dargslan-ip-geo
```

## CLI Usage

```bash
dargslan-ip 8.8.8.8           # Full geolocation report
dargslan-ip 8.8.8.8 --whois   # Include WHOIS data
dargslan-ip 8.8.8.8 --reverse # Reverse DNS only
dargslan-ip 8.8.8.8 --json    # JSON output
dargslan-ip 1.1.1.1 8.8.8.8   # Multiple IPs
```

## Python API

```python
from dargslan_ip_geo import IPGeo
ig = IPGeo()
info = ig.lookup("8.8.8.8")
whois = ig.whois("8.8.8.8")
ig.print_report("8.8.8.8")
```

## More from Dargslan

- [Dargslan.com](https://dargslan.com) — Linux & DevOps eBook Store
- [Free Cheat Sheets](https://dargslan.com/cheat-sheets)
- [Blog & Tutorials](https://dargslan.com/blog)

## License

MIT — see [LICENSE](LICENSE)
