# dargslan-iptables-export

**Firewall Rule Exporter & Documenter** — Export iptables/nftables rules to readable, JSON, and CSV formats. Auto-detects backend. Zero external dependencies.

[![PyPI version](https://img.shields.io/pypi/v/dargslan-iptables-export)](https://pypi.org/project/dargslan-iptables-export/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install dargslan-iptables-export
```

## CLI Usage

```bash
dargslan-iptexp report            # Full firewall report
dargslan-iptexp readable          # Human-readable export
dargslan-iptexp json              # JSON export
dargslan-iptexp csv               # CSV export
dargslan-iptexp raw               # Raw iptables output
dargslan-iptexp stats             # Rule statistics
dargslan-iptexp readable -o rules.txt  # Export to file
```

## Python API

```python
from dargslan_iptables_export import IptablesExport
ie = IptablesExport()
rules = ie.parse_iptables_rules()
readable = ie.export_readable()
ie.print_report()
```

## More from Dargslan

- [Dargslan.com](https://dargslan.com) — Linux & DevOps eBook Store
- [Free Cheat Sheets](https://dargslan.com/cheat-sheets)
- [Blog & Tutorials](https://dargslan.com/blog)

## License

MIT — see [LICENSE](LICENSE)
