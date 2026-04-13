# dargslan-dns-resolver

**DNS Resolver Tester** — Measure resolution time, compare resolvers, test DNSSEC, and detect DNS configuration issues. Zero external dependencies.

[![PyPI version](https://img.shields.io/pypi/v/dargslan-dns-resolver)](https://pypi.org/project/dargslan-dns-resolver/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install dargslan-dns-resolver
```

## CLI Usage

```bash
dargslan-dns report                     # Full DNS report
dargslan-dns resolve google.com         # Quick resolution test
dargslan-dns dig google.com MX          # Dig-style query
dargslan-dns compare 8.8.8.8 1.1.1.1   # Compare resolvers
dargslan-dns dnssec google.com          # DNSSEC validation test
dargslan-dns reverse 8.8.8.8            # Reverse lookup
dargslan-dns config                     # Show resolver config
dargslan-dns json                       # JSON output
```

## Python API

```python
from dargslan_dns_resolver import DNSResolver
dr = DNSResolver()
result = dr.resolve("dargslan.com")
comparison = dr.compare_resolvers(["8.8.8.8", "1.1.1.1", "9.9.9.9"])
dr.print_report()
```

## More from Dargslan

- [Dargslan.com](https://dargslan.com) — Linux & DevOps eBook Store
- [Free Cheat Sheets](https://dargslan.com/cheat-sheets)
- [Blog & Tutorials](https://dargslan.com/blog)

## License

MIT — see [LICENSE](LICENSE)
