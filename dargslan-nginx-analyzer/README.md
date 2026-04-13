# dargslan-nginx-analyzer

**Nginx Configuration Analyzer** — Validate configs, detect security issues, check SSL settings, audit security headers, and analyze server blocks. Zero external dependencies.

[![PyPI version](https://img.shields.io/pypi/v/dargslan-nginx-analyzer)](https://pypi.org/project/dargslan-nginx-analyzer/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install dargslan-nginx-analyzer
```

## CLI Usage

```bash
# Full analysis report
dargslan-nginx report

# List server blocks
dargslan-nginx servers

# Check SSL configuration
dargslan-nginx ssl

# Check security headers
dargslan-nginx headers

# All issues
dargslan-nginx issues

# Test nginx config (nginx -t)
dargslan-nginx test

# JSON output
dargslan-nginx json

# Custom config path
dargslan-nginx report -c /etc/nginx/nginx.conf
```

## Python API

```python
from dargslan_nginx_analyzer import NginxAnalyzer

na = NginxAnalyzer()  # auto-finds nginx.conf

# Full audit
issues = na.audit()

# Specific checks
ssl_issues = na.check_ssl_config()
header_issues = na.check_security_headers()
common_issues = na.check_common_issues()

# Get server blocks
servers = na.get_server_blocks()

# Test config validity
result = na.test_config()

# Formatted report
na.print_report()
```

## Checks Performed

| Category | What It Checks |
|----------|---------------|
| SSL/TLS | Insecure protocols, cipher config, server cipher preference |
| Headers | X-Frame-Options, HSTS, CSP, X-Content-Type-Options, etc. |
| Security | server_tokens, autoindex, dotfile access |
| Config | Syntax validation via `nginx -t` |

## More from Dargslan

- [Dargslan.com](https://dargslan.com) — Linux & DevOps eBook Store
- [Free Cheat Sheets](https://dargslan.com/cheat-sheets) — 300+ downloadable PDFs
- [Blog & Tutorials](https://dargslan.com/blog) — 300+ in-depth articles
- [All Python Tools](https://pypi.org/user/dargslan/) — 20+ CLI packages

## License

MIT — see [LICENSE](LICENSE)
