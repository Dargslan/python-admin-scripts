"""
CLI interface for dargslan-sysinfo.

Usage:
    dargslan-sysinfo          Full system report
    dargslan-sysinfo --cpu    CPU info only
    dargslan-sysinfo --json   JSON output

More tools at https://dargslan.com
"""

import argparse
import json
import sys

from dargslan_sysinfo.sysinfo import SystemInfo


def main():
    parser = argparse.ArgumentParser(
        description="Linux System Information Tool — dargslan.com",
        epilog="More Linux & DevOps tools at https://dargslan.com",
    )
    parser.add_argument("--cpu", action="store_true", help="Show CPU information")
    parser.add_argument("--memory", action="store_true", help="Show memory information")
    parser.add_argument("--disk", action="store_true", help="Show disk information")
    parser.add_argument("--network", action="store_true", help="Show network information")
    parser.add_argument("--processes", action="store_true", help="Show top processes")
    parser.add_argument("--all", action="store_true", help="Show all sections")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--version", action="version", version="dargslan-sysinfo 1.0.0")

    args = parser.parse_args()
    info = SystemInfo()

    if args.json:
        report = info.full_report()
        print(json.dumps(report, indent=2, default=str))
        return

    sections = []
    if args.all:
        sections = ["os", "cpu", "memory", "disk", "network", "processes"]
    elif any([args.cpu, args.memory, args.disk, args.network, args.processes]):
        sections.append("os")
        if args.cpu:
            sections.append("cpu")
        if args.memory:
            sections.append("memory")
        if args.disk:
            sections.append("disk")
        if args.network:
            sections.append("network")
        if args.processes:
            sections.append("processes")
    else:
        sections = ["os", "cpu", "memory", "disk", "network"]

    info.print_report(sections)


if __name__ == "__main__":
    main()
