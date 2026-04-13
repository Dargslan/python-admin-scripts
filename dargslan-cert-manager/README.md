# dargslan-cert-manager

**SSL/TLS Certificate Inventory Manager** — Track expiry dates, issuer info, and certificate chain across servers and local files. Zero external dependencies.

[![PyPI version](https://img.shields.io/pypi/v/dargslan-cert-manager)](https://pypi.org/project/dargslan-cert-manager/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install dargslan-cert-manager
```

## CLI Usage

```bash
dargslan-cert report example.com    # Full certificate report
dargslan-cert check example.com     # Quick expiry check
dargslan-cert file -f /etc/ssl/cert.pem  # Check local cert file
dargslan-cert local               # Find local certificates
dargslan-cert check a.com b.com   # Bulk check multiple hosts
dargslan-cert json                # JSON output
```

## Python API

```python
from dargslan_cert_manager import CertManager
cm = CertManager()
info = cm.check_remote("example.com")
print(f"Expires in {info['days_until_expiry']} days")
cm.print_report(["example.com", "google.com"])
```

## More from Dargslan

- [Dargslan.com](https://dargslan.com) — Linux & DevOps eBook Store
- [Free Cheat Sheets](https://dargslan.com/cheat-sheets)
- [Blog & Tutorials](https://dargslan.com/blog)

## License

MIT — see [LICENSE](LICENSE)
