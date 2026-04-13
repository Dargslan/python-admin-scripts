# dargslan-process-monitor

**Linux Process Monitor** — Monitor processes, detect zombies, track resource-hungry processes. Reads directly from /proc. Zero external dependencies.

[![PyPI version](https://img.shields.io/pypi/v/dargslan-process-monitor)](https://pypi.org/project/dargslan-process-monitor/)

## Installation

```bash
pip install dargslan-process-monitor
```

## CLI Usage

```bash
dargslan-proc summary          # Process summary
dargslan-proc zombies          # Find zombie processes
dargslan-proc topmem -n 15     # Top 15 memory consumers
dargslan-proc topcpu           # Top CPU consumers
dargslan-proc find nginx       # Find processes by name
dargslan-proc count            # Process count by state
dargslan-proc json             # JSON output
```

## Python API

```python
from dargslan_process_monitor import ProcessMonitor

pm = ProcessMonitor()
pm.print_summary()

zombies = pm.find_zombies()
top_mem = pm.top_memory(10)
top_cpu = pm.top_cpu(10)
nginx = pm.find_by_name("nginx")
counts = pm.process_count()
```

## More Resources

- [Linux eBooks](https://dargslan.com/books) | [Cheat Sheets](https://dargslan.com/cheat-sheets) | [Blog](https://dargslan.com/blog)

## License

MIT — [Dargslan](https://dargslan.com)
