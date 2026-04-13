# dargslan-git-audit

**Git Repository Security Auditor** — Scan for secrets in commits, large files, .gitignore gaps, and sensitive data leaks. Zero external dependencies.

[![PyPI version](https://img.shields.io/pypi/v/dargslan-git-audit)](https://pypi.org/project/dargslan-git-audit/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install dargslan-git-audit
```

## CLI Usage

```bash
dargslan-git report           # Full security report
dargslan-git secrets          # Scan for secrets
dargslan-git sensitive        # Check sensitive files
dargslan-git gitignore        # Check .gitignore gaps
dargslan-git large            # Find large files
dargslan-git stats            # Repository statistics
dargslan-git json             # JSON output
```

## Python API

```python
from dargslan_git_audit import GitAudit
ga = GitAudit()
secrets = ga.scan_working_secrets()
issues = ga.audit()
ga.print_report()
```

## More from Dargslan

- [Dargslan.com](https://dargslan.com) — Linux & DevOps eBook Store
- [Free Cheat Sheets](https://dargslan.com/cheat-sheets)
- [Blog & Tutorials](https://dargslan.com/blog)

## License

MIT — see [LICENSE](LICENSE)
