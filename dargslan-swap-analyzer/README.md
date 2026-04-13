# dargslan-swap-analyzer

**Linux Swap Usage Analyzer** — Find which processes use swap, measure swap pressure, get optimization recommendations. Zero external dependencies.

[![PyPI version](https://img.shields.io/pypi/v/dargslan-swap-analyzer)](https://pypi.org/project/dargslan-swap-analyzer/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install dargslan-swap-analyzer
```

## CLI Usage

```bash
dargslan-swap report          # Full swap analysis
dargslan-swap info            # Swap summary
dargslan-swap processes       # Per-process swap usage
dargslan-swap devices         # Swap partitions/files
dargslan-swap pressure        # Memory pressure info
dargslan-swap json            # JSON output
```

## Python API

```python
from dargslan_swap_analyzer import SwapAnalyzer
sa = SwapAnalyzer()
info = sa.get_swap_info()
procs = sa.get_process_swap()
sa.print_report()
```

## More from Dargslan

- [Dargslan.com](https://dargslan.com) — Linux & DevOps eBook Store
- [Free Cheat Sheets](https://dargslan.com/cheat-sheets)
- [Blog & Tutorials](https://dargslan.com/blog)

## License

MIT — see [LICENSE](LICENSE)
