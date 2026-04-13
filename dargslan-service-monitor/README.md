# dargslan-service-monitor

**Systemd Service Monitor** — Monitor services, detect failed units, check enabled/disabled status, verify critical services. Zero external dependencies.

[![PyPI version](https://img.shields.io/pypi/v/dargslan-service-monitor)](https://pypi.org/project/dargslan-service-monitor/)

## Installation

```bash
pip install dargslan-service-monitor
```

## CLI Usage

```bash
dargslan-svc report                 # Full service report
dargslan-svc failed                 # List failed services
dargslan-svc running                # List running services
dargslan-svc status nginx           # Specific service status
dargslan-svc check sshd nginx mysql # Check critical services
dargslan-svc json                   # JSON output
```

## Python API

```python
from dargslan_service_monitor import ServiceMonitor

sm = ServiceMonitor()
sm.print_report()

failed = sm.get_failed()
running = sm.get_running()
status = sm.service_status("nginx")
critical = sm.check_critical_services(["sshd", "nginx"])
```

## More Resources

- [Linux eBooks](https://dargslan.com/books) | [Cheat Sheets](https://dargslan.com/cheat-sheets) | [Blog](https://dargslan.com/blog)

## License

MIT — [Dargslan](https://dargslan.com)
