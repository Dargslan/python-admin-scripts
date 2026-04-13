# dargslan-docker-health

**Docker Container Health Checker** — Monitor running containers, check resource usage, detect unhealthy services, and get container stats.

[![PyPI version](https://img.shields.io/pypi/v/dargslan-docker-health)](https://pypi.org/project/dargslan-docker-health/)

## Installation

```bash
pip install dargslan-docker-health
```

## Usage

```python
from dargslan_docker_health import DockerHealth

dh = DockerHealth()
status = dh.check_all()
for c in status:
    print(f"{c['name']}: {c['status']} (CPU: {c['cpu']}%, MEM: {c['memory_mb']}MB)")
```

```bash
dargslan-docker              # Status of all containers
dargslan-docker --json       # JSON output
dargslan-docker --unhealthy  # Show only unhealthy
```

## Resources

- [Docker & DevOps eBooks](https://dargslan.com/books)
- [Free Cheat Sheets](https://dargslan.com/cheat-sheets)

MIT — **[Dargslan](https://dargslan.com)**
