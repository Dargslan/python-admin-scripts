# dargslan-container-audit

**Container Security Auditor** — Audit Docker/Podman containers for privileged mode, root users, dangerous capabilities, sensitive volume mounts, and host network mode. Zero external dependencies.

[![PyPI version](https://img.shields.io/pypi/v/dargslan-container-audit)](https://pypi.org/project/dargslan-container-audit/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install dargslan-container-audit
```

## CLI Usage

```bash
# Full security report
dargslan-container report

# List all containers
dargslan-container list

# Check for privileged containers
dargslan-container privileged

# Check for root containers
dargslan-container root

# Check dangerous capabilities
dargslan-container caps

# Check sensitive volume mounts
dargslan-container volumes

# Check host network mode
dargslan-container network

# All issues as JSON
dargslan-container json

# Use Podman instead of Docker
dargslan-container report -r podman
```

## Python API

```python
from dargslan_container_audit import ContainerAudit

ca = ContainerAudit()  # auto-detects Docker or Podman

# Full audit
issues = ca.audit()

# Specific checks
privileged = ca.check_privileged()
root = ca.check_root_containers()
caps = ca.check_capabilities()
volumes = ca.check_volumes()
network = ca.check_network_mode()

# Formatted report
ca.print_report()
```

## Security Checks

| Check | Severity | Description |
|-------|----------|-------------|
| Privileged mode | Critical | Containers with `--privileged` flag |
| Root user | Warning | Containers running as root |
| Dangerous capabilities | High | SYS_ADMIN, NET_ADMIN, SYS_PTRACE, etc. |
| Sensitive mounts | High | /etc, /proc, /sys, docker.sock |
| Host network | Warning | Containers using `--network host` |

## More from Dargslan

- [Dargslan.com](https://dargslan.com) — Linux & DevOps eBook Store
- [Free Cheat Sheets](https://dargslan.com/cheat-sheets) — 300+ downloadable PDFs
- [Blog & Tutorials](https://dargslan.com/blog) — 300+ in-depth articles
- [All Python Tools](https://pypi.org/user/dargslan/) — 20+ CLI packages

## License

MIT — see [LICENSE](LICENSE)
