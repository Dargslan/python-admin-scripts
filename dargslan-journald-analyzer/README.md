# dargslan-journald-analyzer

**Systemd Journal Log Analyzer** — Find boot errors, service failures, kernel warnings, OOM kills, and security events. Zero external dependencies.

[![PyPI version](https://img.shields.io/pypi/v/dargslan-journald-analyzer)](https://pypi.org/project/dargslan-journald-analyzer/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install dargslan-journald-analyzer
```

## CLI Usage

```bash
dargslan-journal report       # Full journal analysis
dargslan-journal errors       # Boot errors
dargslan-journal failures     # Failed systemd units
dargslan-journal kernel       # Kernel warnings
dargslan-journal security     # Security events
dargslan-journal oom          # OOM kill events
dargslan-journal boots        # Boot history
dargslan-journal json         # JSON output
```

## Python API

```python
from dargslan_journald_analyzer import JournaldAnalyzer
ja = JournaldAnalyzer()
errors = ja.get_boot_errors()
failed = ja.get_failed_units()
ja.print_report()
```

## More from Dargslan

- [Dargslan.com](https://dargslan.com) — Linux & DevOps eBook Store
- [Free Cheat Sheets](https://dargslan.com/cheat-sheets)
- [Blog & Tutorials](https://dargslan.com/blog)

## License

MIT — see [LICENSE](LICENSE)
