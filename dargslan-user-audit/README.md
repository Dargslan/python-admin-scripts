# dargslan-user-audit

**Linux User Account Auditor** — Audit user accounts, detect empty passwords, check sudo access, find duplicate UIDs, review home directory permissions. Zero external dependencies.

[![PyPI version](https://img.shields.io/pypi/v/dargslan-user-audit)](https://pypi.org/project/dargslan-user-audit/)

## Installation

```bash
pip install dargslan-user-audit
```

## CLI Usage

```bash
dargslan-users report    # Full user audit report
dargslan-users list      # List login users
dargslan-users sudo      # List sudo users
dargslan-users root      # List root-level accounts
dargslan-users issues    # Show security issues
dargslan-users json      # JSON output
```

## Python API

```python
from dargslan_user_audit import UserAudit

ua = UserAudit()
ua.print_report()

login_users = ua.get_login_users()
sudo_users = ua.check_sudo_users()
issues = ua.audit()
```

## More Resources

- [Linux eBooks](https://dargslan.com/books) | [Cheat Sheets](https://dargslan.com/cheat-sheets) | [Blog](https://dargslan.com/blog)

## License

MIT — [Dargslan](https://dargslan.com)
