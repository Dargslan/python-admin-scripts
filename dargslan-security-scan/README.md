# dargslan-security-scan

**Linux Security Scanner** — Check SSH config, SUID binaries, kernel parameters, file permissions, world-writable files, and get a security score. Zero external dependencies.

[![PyPI version](https://img.shields.io/pypi/v/dargslan-security-scan)](https://pypi.org/project/dargslan-security-scan/)

## Installation

```bash
pip install dargslan-security-scan
```

## CLI Usage

```bash
dargslan-secscan report    # Full security report with score
dargslan-secscan ssh       # Check SSH configuration
dargslan-secscan suid      # Find SUID/SGID binaries
dargslan-secscan kernel    # Check kernel parameters
dargslan-secscan perms     # Check file permissions
dargslan-secscan score     # Security score (0-100)
dargslan-secscan json      # JSON output
```

## Python API

```python
from dargslan_security_scan import SecurityScanner

ss = SecurityScanner()
ss.print_report()

score = ss.score()
ssh_issues = ss.check_ssh_config()
suid = ss.find_suid_files()
kernel = ss.check_kernel_params()
full = ss.full_scan()
```

## What It Checks

- SSH configuration (root login, password auth, empty passwords, port)
- SUID/SGID binaries (known vs unknown)
- Kernel security parameters (IP forwarding, ASLR, SYN cookies, etc.)
- File permissions (/etc/passwd, /etc/shadow, sshd_config, etc.)
- World-writable files in /etc and /var

## More Resources

- [Linux eBooks](https://dargslan.com/books) | [Cheat Sheets](https://dargslan.com/cheat-sheets) | [Blog](https://dargslan.com/blog)

## License

MIT — [Dargslan](https://dargslan.com)
