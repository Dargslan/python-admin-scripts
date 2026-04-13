# dargslan-dns-check

**DNS Record Checker & Analyzer** — Query A, AAAA, MX, NS, TXT, CNAME, SOA records for any domain. Check DNS propagation across multiple nameservers. Zero external dependencies.

[![PyPI version](https://img.shields.io/pypi/v/dargslan-dns-check)](https://pypi.org/project/dargslan-dns-check/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install dargslan-dns-check
```

## CLI Usage

```bash
# Full DNS report
dargslan-dns example.com

# Query specific record type
dargslan-dns example.com -t MX

# JSON output
dargslan-dns example.com --json

# Check DNS propagation
dargslan-dns example.com --propagation

# Reverse DNS lookup
dargslan-dns 8.8.8.8 --reverse

# Use custom nameserver
dargslan-dns example.com -n 1.1.1.1
```

## Python API

```python
from dargslan_dns_check import DNSChecker

checker = DNSChecker()

# Query all DNS records
all_records = checker.query_all("example.com")

# Query specific type
mx_records = checker.query("example.com", "MX")

# Check propagation across nameservers
propagation = checker.check_propagation("example.com")

# Reverse DNS
result = checker.reverse_lookup("8.8.8.8")

# Print formatted report
checker.print_report("example.com")

# JSON output
print(checker.to_json("example.com"))
```

## Features

- Query all common DNS record types (A, AAAA, MX, NS, TXT, CNAME, SOA)
- DNS propagation check across Google, Cloudflare, OpenDNS, Quad9
- Reverse DNS lookups
- Custom nameserver support
- JSON and formatted report output
- Zero external dependencies — pure Python standard library

## More from Dargslan

- [Dargslan.com](https://dargslan.com) — Linux & DevOps eBook Store
- [Free Cheat Sheets](https://dargslan.com/cheat-sheets) — 300+ downloadable PDFs
- [Blog & Tutorials](https://dargslan.com/blog) — 300+ in-depth articles
- [All Python Tools](https://pypi.org/user/dargslan/) — 20+ CLI packages

## License

MIT — see [LICENSE](LICENSE)
