# dargslan-firewall-audit

**Linux Firewall Audit Tool** — Audit iptables/nftables rules, detect security gaps, check default policies, and generate compliance reports.

[![PyPI version](https://img.shields.io/pypi/v/dargslan-firewall-audit)](https://pypi.org/project/dargslan-firewall-audit/)

## Installation

```bash
pip install dargslan-firewall-audit
```

## Usage

```python
from dargslan_firewall_audit import FirewallAudit

audit = FirewallAudit()
report = audit.full_audit()
print(f"Score: {report['score']}/100")
print(f"Issues: {len(report['issues'])}")
```

```bash
sudo dargslan-fwaudit           # Full audit
sudo dargslan-fwaudit --json    # JSON output
sudo dargslan-fwaudit --fix     # Show fix suggestions
```

## Checks

- Default INPUT/FORWARD policy (should be DROP)
- SSH rate limiting rules
- Open ports without firewall rules
- ICMP flood protection
- IP forwarding status
- Logging configuration

## Resources

- [Linux & Security eBooks](https://dargslan.com/books)
- [Free Cheat Sheets](https://dargslan.com/cheat-sheets)
- [Security Tutorials](https://dargslan.com/blog)

MIT — **[Dargslan](https://dargslan.com)**
