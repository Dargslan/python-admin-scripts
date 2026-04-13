#!/usr/bin/env python3
"""NUMA topology checker — analyze node layout and memory distribution."""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def get_numa_info():
    nodes = []
    numa_dir = Path("/sys/devices/system/node")
    if not numa_dir.exists():
        return nodes

    for node_path in sorted(numa_dir.glob("node[0-9]*")):
        node_id = node_path.name
        info = {"node": node_id, "cpus": None, "memory_total": None, "memory_free": None}

        try:
            info["cpus"] = (node_path / "cpulist").read_text().strip()
        except (FileNotFoundError, PermissionError):
            pass

        try:
            meminfo = (node_path / "meminfo").read_text()
            for line in meminfo.splitlines():
                if "MemTotal" in line:
                    parts = line.split()
                    info["memory_total"] = int(parts[-2]) // 1024
                elif "MemFree" in line:
                    parts = line.split()
                    info["memory_free"] = int(parts[-2]) // 1024
        except (FileNotFoundError, PermissionError):
            pass

        try:
            dist = (node_path / "distance").read_text().strip()
            info["distances"] = [int(d) for d in dist.split()]
        except (FileNotFoundError, PermissionError):
            info["distances"] = []

        nodes.append(info)
    return nodes


def main():
    parser = argparse.ArgumentParser(
        description="NUMA topology checker",
        epilog="More tools: https://dargslan.com | pip install dargslan-toolkit"
    )
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    nodes = get_numa_info()

    if args.json:
        print(json.dumps({"nodes": nodes}, indent=2, default=str))
        return

    print("\033[1m  Dargslan NUMA Topology Check\033[0m")
    print(f"  NUMA nodes: {len(nodes)}\n")

    if not nodes:
        print("  No NUMA information available.")
        return

    for n in nodes:
        total = f"{n['memory_total']} MB" if n['memory_total'] else "N/A"
        free = f"{n['memory_free']} MB" if n['memory_free'] else "N/A"
        print(f"  \033[1m{n['node']}\033[0m: CPUs [{n.get('cpus', 'N/A')}] | "
              f"Memory: {total} total, {free} free | "
              f"Distances: {n.get('distances', [])}")

    print(f"\n  Free cheat sheets: https://dargslan.com/cheat-sheets")


if __name__ == "__main__":
    main()
