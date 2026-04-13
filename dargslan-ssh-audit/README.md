# dargslan-ssh-audit

**SSH Server Configuration Auditor** — Check key types, ciphers, login policies, authorized_keys security, and SSH hardening best practices. Zero external dependencies.

[![PyPI version](https://img.shields.io/pypi/v/dargslan-ssh-audit)](https://pypi.org/project/dargslan-ssh-audit/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install dargslan-ssh-audit
```

## CLI Usage

```bash
dargslan-ssh report           # Full security report
dargslan-ssh issues           # List all issues
dargslan-ssh keys             # Check host key types
dargslan-ssh auth-keys        # Audit authorized_keys files
dargslan-ssh json             # JSON output
dargslan-ssh report -c /path  # Custom sshd_config
```

## Python API

```python
from dargslan_ssh_audit import SSHAudit
sa = SSHAudit()
issues = sa.audit()
sa.print_report()
```

## More from Dargslan

- [Dargslan.com](https://dargslan.com) — Linux & DevOps eBook Store
- [Free Cheat Sheets](https://dargslan.com/cheat-sheets) — 300+ downloadable PDFs
- [Blog & Tutorials](https://dargslan.com/blog) — 330+ in-depth articles

## License

MIT — see [LICENSE](LICENSE)
