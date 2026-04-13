# dargslan-kernel-check

**Linux Kernel Parameter Checker** — Audit sysctl hardening, compare live vs saved settings, security scoring. Zero external dependencies.

[![PyPI version](https://img.shields.io/pypi/v/dargslan-kernel-check)](https://pypi.org/project/dargslan-kernel-check/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install dargslan-kernel-check
```

## CLI Usage

```bash
dargslan-kernel report        # Full hardening report with score
dargslan-kernel score         # Security score out of 100
dargslan-kernel params        # All security parameters
dargslan-kernel diffs         # Live vs saved differences
dargslan-kernel json          # JSON output
```

## Python API

```python
from dargslan_kernel_check import KernelCheck
kc = KernelCheck()
score = kc.get_score()
params = kc.check_all_params()
kc.print_report()
```

## More from Dargslan

- [Dargslan.com](https://dargslan.com) — Linux & DevOps eBook Store
- [Free Cheat Sheets](https://dargslan.com/cheat-sheets)
- [Blog & Tutorials](https://dargslan.com/blog)

## License

MIT — see [LICENSE](LICENSE)
