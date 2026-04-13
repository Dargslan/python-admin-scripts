# dargslan-disk-benchmark

**Linux Disk I/O Benchmark Tool** — Measure sequential read/write speed, random IOPS, and write latency. Zero external dependencies.

[![PyPI version](https://img.shields.io/pypi/v/dargslan-disk-benchmark)](https://pypi.org/project/dargslan-disk-benchmark/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install dargslan-disk-benchmark
```

## CLI Usage

```bash
dargslan-diskbench report           # Full I/O benchmark
dargslan-diskbench write -s 100     # Sequential write (100 MB)
dargslan-diskbench read -s 100      # Sequential read (100 MB)
dargslan-diskbench iops             # Random IOPS test
dargslan-diskbench latency          # Write latency test
dargslan-diskbench json             # JSON output
```

## Python API

```python
from dargslan_disk_benchmark import DiskBenchmark
db = DiskBenchmark(path="/mnt/data")
results = db.full_benchmark(size_mb=100)
db.print_report()
```

## More from Dargslan

- [Dargslan.com](https://dargslan.com) — Linux & DevOps eBook Store
- [Free Cheat Sheets](https://dargslan.com/cheat-sheets)
- [Blog & Tutorials](https://dargslan.com/blog)

## License

MIT — see [LICENSE](LICENSE)
