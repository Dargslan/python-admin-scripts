# dargslan-sysinfo

**Linux System Information Tool** — Get comprehensive system information with a single command. CPU, memory, disk, network, uptime, and process monitoring for sysadmins and DevOps engineers.

[![PyPI version](https://img.shields.io/pypi/v/dargslan-sysinfo)](https://pypi.org/project/dargslan-sysinfo/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install dargslan-sysinfo
```

## Quick Start

### Command Line

```bash
# Full system report
dargslan-sysinfo

# Specific sections
dargslan-sysinfo --cpu
dargslan-sysinfo --memory
dargslan-sysinfo --disk
dargslan-sysinfo --network
dargslan-sysinfo --processes
dargslan-sysinfo --all

# JSON output (for scripting)
dargslan-sysinfo --json
```

### Python API

```python
from dargslan_sysinfo import SystemInfo

info = SystemInfo()

# Get all system info
report = info.full_report()

# Individual sections
cpu = info.cpu_info()
mem = info.memory_info()
disk = info.disk_info()
net = info.network_info()
procs = info.top_processes(n=10)

# JSON output
import json
print(json.dumps(info.full_report(), indent=2))
```

## Output Example

```
╔══════════════════════════════════════════════════════════════╗
║                    SYSTEM INFORMATION                       ║
╚══════════════════════════════════════════════════════════════╝

🖥️  HOSTNAME:     web-server-01
🐧  OS:           Ubuntu 24.04.1 LTS
🔧  KERNEL:       6.8.0-45-generic
⏱️  UPTIME:       14 days, 3 hours, 22 minutes
📦  PACKAGES:     1,247 installed

💻  CPU
    Model:        AMD EPYC 7763 64-Core
    Cores:        4 (8 threads)
    Load Avg:     0.45, 0.38, 0.32
    Usage:        12.3%

🧠  MEMORY
    Total:        16.0 GB
    Used:         6.2 GB (38.8%)
    Available:    9.8 GB
    Swap:         2.0 GB (0.0% used)

💾  DISK
    /             45.2 GB / 100.0 GB (45.2%)
    /home         12.8 GB / 50.0 GB  (25.6%)

🌐  NETWORK
    eth0:         10.0.0.5
    RX:           2.4 GB
    TX:           1.1 GB
```

## Features

- Zero dependencies — uses only Python standard library
- Works on any Linux distribution
- CLI and Python API
- JSON output for automation
- Color-coded terminal output
- Top process monitoring

## Use Cases

- **Server health checks** — Quick overview of system resources
- **Monitoring scripts** — JSON output for integration with monitoring tools
- **Inventory management** — Collect system info across fleet
- **Troubleshooting** — Identify resource bottlenecks

## More Resources

- 📚 [Linux & DevOps eBooks](https://dargslan.com/books) — 210+ professional eBooks
- 📋 [Free Cheat Sheets](https://dargslan.com/cheat-sheets) — Linux, Docker, Kubernetes quick references
- 📖 [Blog & Tutorials](https://dargslan.com/blog) — In-depth Linux and DevOps guides

## License

MIT License — see [LICENSE](LICENSE) for details.

---

**Made with ❤️ by [Dargslan](https://dargslan.com)** — Your source for Linux & DevOps knowledge.
