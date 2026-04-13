#!/usr/bin/env python3
"""Network bonding/teaming monitor — check bond mode, slave status, failover."""

import argparse
import json
import sys
from pathlib import Path


def get_bond_info():
    bonds = []
    bond_dir = Path("/proc/net/bonding")
    if not bond_dir.exists():
        sys_bonds = Path("/sys/class/net")
        for iface in sys_bonds.iterdir():
            bonding_dir = iface / "bonding"
            if bonding_dir.exists():
                info = {"interface": iface.name, "mode": None, "slaves": [], "active_slave": None}
                try:
                    info["mode"] = (bonding_dir / "mode").read_text().strip()
                except (FileNotFoundError, PermissionError):
                    pass
                try:
                    slaves = (bonding_dir / "slaves").read_text().strip()
                    info["slaves"] = slaves.split() if slaves else []
                except (FileNotFoundError, PermissionError):
                    pass
                try:
                    info["active_slave"] = (bonding_dir / "active_slave").read_text().strip()
                except (FileNotFoundError, PermissionError):
                    pass
                try:
                    info["miimon"] = (bonding_dir / "miimon").read_text().strip()
                except (FileNotFoundError, PermissionError):
                    pass
                bonds.append(info)
        return bonds

    for bond_file in sorted(bond_dir.iterdir()):
        info = {"interface": bond_file.name, "mode": None, "slaves": [], "mii_status": None}
        try:
            content = bond_file.read_text()
            for line in content.splitlines():
                if line.startswith("Bonding Mode:"):
                    info["mode"] = line.split(":", 1)[1].strip()
                elif line.startswith("MII Status:"):
                    info["mii_status"] = line.split(":", 1)[1].strip()
                elif line.startswith("Slave Interface:"):
                    info["slaves"].append(line.split(":", 1)[1].strip())
                elif line.startswith("Currently Active Slave:"):
                    info["active_slave"] = line.split(":", 1)[1].strip()
        except (FileNotFoundError, PermissionError):
            pass
        bonds.append(info)
    return bonds


def main():
    parser = argparse.ArgumentParser(
        description="Network bonding/teaming monitor",
        epilog="More tools: https://dargslan.com | pip install dargslan-toolkit"
    )
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    bonds = get_bond_info()

    if args.json:
        print(json.dumps({"bonds": bonds}, indent=2, default=str))
        return

    print("\033[1m  Dargslan Bonding Check\033[0m")

    if not bonds:
        print("  No bonding interfaces found.")
        print("  Tip: Create a bond with: ip link add bond0 type bond mode 802.3ad")
    else:
        for b in bonds:
            print(f"\n  \033[1m{b['interface']}\033[0m")
            print(f"    Mode: {b.get('mode', 'N/A')}")
            print(f"    Slaves: {', '.join(b['slaves']) if b['slaves'] else 'none'}")
            print(f"    Active: {b.get('active_slave', 'N/A')}")
            if b.get('mii_status'):
                print(f"    MII Status: {b['mii_status']}")

    print(f"\n  Free cheat sheets: https://dargslan.com/cheat-sheets")


if __name__ == "__main__":
    main()
