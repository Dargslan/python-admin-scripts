# dargslan-log-parser

**Linux Log File Parser & Analyzer** — Parse and analyze syslog, auth.log, nginx access/error logs, and Apache logs. Detect failed SSH logins, error patterns, and security events.

[![PyPI version](https://img.shields.io/pypi/v/dargslan-log-parser)](https://pypi.org/project/dargslan-log-parser/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install dargslan-log-parser
```

## Quick Start

```python
from dargslan_log_parser import LogParser

parser = LogParser()

# Parse auth.log for failed SSH logins
failed = parser.parse_auth_log("/var/log/auth.log")
for entry in failed:
    print(f"{entry['timestamp']} - Failed login from {entry['ip']} as {entry['user']}")

# Parse nginx access log
entries = parser.parse_nginx_access("/var/log/nginx/access.log")
errors = [e for e in entries if e["status"] >= 400]

# Search any log for patterns
matches = parser.search("/var/log/syslog", pattern="error|warning|critical", case_insensitive=True)

# Summary report
report = parser.summary("/var/log/auth.log", log_type="auth")
print(f"Failed logins: {report['failed_logins']}")
print(f"Top attackers: {report['top_ips']}")
```

## CLI Usage

```bash
# Analyze auth log
dargslan-logs auth /var/log/auth.log

# Parse nginx access log
dargslan-logs nginx /var/log/nginx/access.log --errors-only

# Search any log
dargslan-logs search /var/log/syslog -p "error|fail" -i

# Summary
dargslan-logs summary /var/log/auth.log --type auth
```

## More Resources

- [Linux & DevOps eBooks](https://dargslan.com/books) — 210+ professional eBooks
- [Free Cheat Sheets](https://dargslan.com/cheat-sheets) — Quick reference PDFs
- [Blog & Tutorials](https://dargslan.com/blog) — In-depth guides

## License

MIT — **Made by [Dargslan](https://dargslan.com)**
