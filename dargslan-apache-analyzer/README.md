# dargslan-apache-analyzer

**Apache HTTP Server Configuration Analyzer** — Check VirtualHosts, SSL, security modules, ServerTokens, directory listing, and common misconfigurations. Zero external dependencies.

[![PyPI version](https://img.shields.io/pypi/v/dargslan-apache-analyzer)](https://pypi.org/project/dargslan-apache-analyzer/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install dargslan-apache-analyzer
```

## CLI Usage

```bash
dargslan-apache report        # Full analysis report
dargslan-apache vhosts        # List VirtualHosts
dargslan-apache modules       # Loaded modules
dargslan-apache issues        # Security issues
dargslan-apache test          # Config syntax test
dargslan-apache json          # JSON output
```

## Python API

```python
from dargslan_apache_analyzer import ApacheAnalyzer
aa = ApacheAnalyzer()
vhosts = aa.get_vhosts()
issues = aa.check_security()
aa.print_report()
```

## More from Dargslan

- [Dargslan.com](https://dargslan.com) — Linux & DevOps eBook Store
- [Free Cheat Sheets](https://dargslan.com/cheat-sheets)
- [Blog & Tutorials](https://dargslan.com/blog)

## License

MIT — see [LICENSE](LICENSE)
