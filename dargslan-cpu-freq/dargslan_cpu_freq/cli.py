#!/usr/bin/env python3
"""CPU frequency scaling monitor — check governor, frequencies, turbo boost."""

import argparse
import json
import sys
from pathlib import Path


def get_cpu_info():
    cpus = []
    cpu_dir = Path("/sys/devices/system/cpu")
    if not cpu_dir.exists():
        return cpus

    for cpu_path in sorted(cpu_dir.glob("cpu[0-9]*")):
        cpu_id = cpu_path.name
        freq_dir = cpu_path / "cpufreq"
        info = {"cpu": cpu_id}

        for attr in ["scaling_governor", "scaling_cur_freq", "scaling_min_freq",
                     "scaling_max_freq", "cpuinfo_min_freq", "cpuinfo_max_freq",
                     "scaling_driver", "scaling_available_governors"]:
            try:
                val = (freq_dir / attr).read_text().strip()
                if "freq" in attr and val.isdigit():
                    info[attr] = int(val) // 1000
                else:
                    info[attr] = val
            except (FileNotFoundError, PermissionError):
                info[attr] = None

        try:
            online = (cpu_path / "online").read_text().strip()
            info["online"] = online == "1"
        except (FileNotFoundError, PermissionError):
            info["online"] = True

        cpus.append(info)
    return cpus


def get_turbo_status():
    for path in ["/sys/devices/system/cpu/intel_pstate/no_turbo",
                 "/sys/devices/system/cpu/cpufreq/boost"]:
        try:
            val = Path(path).read_text().strip()
            if "no_turbo" in path:
                return "disabled" if val == "1" else "enabled"
            else:
                return "enabled" if val == "1" else "disabled"
        except (FileNotFoundError, PermissionError):
            continue
    return "unknown"


def main():
    parser = argparse.ArgumentParser(
        description="CPU frequency scaling monitor",
        epilog="More tools: https://dargslan.com | pip install dargslan-toolkit"
    )
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--summary", action="store_true", help="Summary only")
    args = parser.parse_args()

    cpus = get_cpu_info()
    turbo = get_turbo_status()

    if args.json:
        print(json.dumps({"cpus": cpus, "turbo_boost": turbo}, indent=2, default=str))
        return

    print("\033[1m  Dargslan CPU Frequency Monitor\033[0m")
    print(f"  Turbo Boost: {turbo}")
    print(f"  CPUs found: {len(cpus)}\n")

    if args.summary:
        print(f"  {'CPU':<8} {'Governor':<15} {'Current':<10} {'Min':<10} {'Max':<10}")
        print(f"  {'-'*53}")
        for c in cpus:
            cur = f"{c.get('scaling_cur_freq', 'N/A')} MHz" if c.get('scaling_cur_freq') else "N/A"
            mn = f"{c.get('scaling_min_freq', 'N/A')} MHz" if c.get('scaling_min_freq') else "N/A"
            mx = f"{c.get('scaling_max_freq', 'N/A')} MHz" if c.get('scaling_max_freq') else "N/A"
            gov = c.get('scaling_governor') or 'N/A'
            print(f"  {c['cpu']:<8} {gov:<15} {cur:<10} {mn:<10} {mx:<10}")
    else:
        for c in cpus:
            print(f"  \033[1m{c['cpu']}\033[0m: {c.get('scaling_governor', 'N/A')} | "
                  f"{c.get('scaling_cur_freq', 'N/A')} MHz | "
                  f"range {c.get('scaling_min_freq', '?')}-{c.get('scaling_max_freq', '?')} MHz | "
                  f"driver: {c.get('scaling_driver', 'N/A')}")

    print(f"\n  Free cheat sheets: https://dargslan.com/cheat-sheets")


if __name__ == "__main__":
    main()
