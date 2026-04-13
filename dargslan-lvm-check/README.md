# dargslan-lvm-check

**LVM Volume Health Checker** — Audit PV, VG, LV status, thin pool usage, and snapshot health. Zero external dependencies.

[![PyPI version](https://img.shields.io/pypi/v/dargslan-lvm-check)](https://pypi.org/project/dargslan-lvm-check/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install dargslan-lvm-check
```

## CLI Usage

```bash
dargslan-lvm report           # Full LVM health report
dargslan-lvm pvs              # Physical volumes
dargslan-lvm vgs              # Volume groups
dargslan-lvm lvs              # Logical volumes
dargslan-lvm snapshots        # Snapshot status
dargslan-lvm thin             # Thin pool usage
dargslan-lvm json             # JSON output
```

## Python API

```python
from dargslan_lvm_check import LVMCheck
lc = LVMCheck()
pvs = lc.get_pvs()
vgs = lc.get_vgs()
lc.print_report()
```

## More from Dargslan

- [Dargslan.com](https://dargslan.com) — Linux & DevOps eBook Store
- [Free Cheat Sheets](https://dargslan.com/cheat-sheets)
- [Blog & Tutorials](https://dargslan.com/blog)

## License

MIT — see [LICENSE](LICENSE)
