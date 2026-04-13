# dargslan-memory-profiler

**Linux Memory Profiler** — Per-process RSS, shared memory, swap usage, grouped by application. Zero external dependencies.

[![PyPI version](https://img.shields.io/pypi/v/dargslan-memory-profiler)](https://pypi.org/project/dargslan-memory-profiler/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install dargslan-memory-profiler
```

## CLI Usage

```bash
dargslan-memprof report        # Full memory profile
dargslan-memprof system        # System memory overview
dargslan-memprof top -n 30     # Top processes by RSS
dargslan-memprof grouped       # Memory by application name
dargslan-memprof shm           # Shared memory segments
dargslan-memprof json          # JSON output
```

## Python API

```python
from dargslan_memory_profiler import MemoryProfiler
mp = MemoryProfiler()
sys_mem = mp.get_system_memory()
top_procs = mp.get_all_processes(limit=10)
mp.print_report()
```

## More from Dargslan

- [Dargslan.com](https://dargslan.com) — Linux & DevOps eBook Store
- [Free Cheat Sheets](https://dargslan.com/cheat-sheets)
- [Blog & Tutorials](https://dargslan.com/blog)

## License

MIT — see [LICENSE](LICENSE)
