# dargslan-ssl-checker

**SSL/TLS Certificate Checker** — Check certificate expiry dates, cipher suites, and security issues for any domain. Zero external dependencies.

[![PyPI version](https://img.shields.io/pypi/v/dargslan-ssl-checker)](https://pypi.org/project/dargslan-ssl-checker/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install dargslan-ssl-checker
```

## CLI Usage

```bash
# Check single domain
dargslan-ssl google.com

# Check multiple domains
dargslan-ssl google.com github.com dargslan.com

# JSON output
dargslan-ssl google.com --json

# Custom port
dargslan-ssl myserver.com -p 8443
```

## Python API

```python
from dargslan_ssl_checker import SSLChecker

checker = SSLChecker()

# Get certificate info
info = checker.get_cert_info("google.com")
print(f"Days until expiry: {info['days_until_expiry']}")
print(f"Issuer: {info['issuer']}")
print(f"Protocol: {info['protocol']}")

# Check multiple domains
results = checker.check_multiple(["google.com", "github.com"])

# Find expiring certificates
expiring = checker.check_expiring(["site1.com", "site2.com"], days_threshold=30)

# Print formatted report
checker.print_report("dargslan.com")
```

## Features

- Certificate expiry date and days remaining
- Cipher suite and TLS protocol version
- Subject Alternative Names (SANs)
- Issuer information
- Expiry warnings (configurable threshold)
- Batch domain checking
- JSON output for scripting
- Zero external dependencies

## More Resources

- [Linux & DevOps eBooks](https://dargslan.com/books) — 210+ professional eBooks
- [Free Cheat Sheets](https://dargslan.com/cheat-sheets) — Quick references
- [Blog & Tutorials](https://dargslan.com/blog) — 300+ guides
- [All Dargslan Tools](https://pypi.org/project/dargslan-toolkit/) — Complete sysadmin toolkit

## License

MIT — [Dargslan](https://dargslan.com)
