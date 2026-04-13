# dargslan-package-audit

**Linux Package Auditor** — Find outdated, security-pending, and orphaned packages on apt/dnf/pacman systems. Zero external dependencies.

[![PyPI version](https://img.shields.io/pypi/v/dargslan-package-audit)](https://pypi.org/project/dargslan-package-audit/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install dargslan-package-audit
```

## CLI Usage

```bash
dargslan-pkg report           # Full audit report
dargslan-pkg upgradable       # List upgradable packages
dargslan-pkg security         # Security updates only
dargslan-pkg orphans          # Auto-removable packages
dargslan-pkg count            # Total installed count
dargslan-pkg json             # JSON output
```

## Python API

```python
from dargslan_package_audit import PackageAudit
pa = PackageAudit()  # auto-detects apt/dnf/pacman
issues = pa.audit()
pa.print_report()
```

## More from Dargslan

- [Dargslan.com](https://dargslan.com) — Linux & DevOps eBook Store
- [Free Cheat Sheets](https://dargslan.com/cheat-sheets)
- [Blog & Tutorials](https://dargslan.com/blog)

## License

MIT — see [LICENSE](LICENSE)
