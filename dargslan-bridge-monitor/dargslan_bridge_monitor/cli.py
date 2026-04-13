#!/usr/bin/env python3
"""dargslan-bridge-monitor — Network bridge interface monitor CLI"""

import subprocess
import json
import argparse
import sys


def run_cmd(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return r.stdout.strip()
    except Exception:
        return ""


def get_bridges():
    bridges = []
    output = run_cmd("bridge link show 2>/dev/null")
    if output:
        for line in output.strip().split("\n"):
            if line.strip():
                bridges.append({"raw": line.strip()})
        return bridges

    output = run_cmd("brctl show 2>/dev/null")
    if output:
        for line in output.strip().split("\n")[1:]:
            if line.strip():
                parts = line.split()
                if len(parts) >= 1:
                    bridges.append({
                        "name": parts[0],
                        "id": parts[1] if len(parts) > 1 else "",
                        "stp": parts[2] if len(parts) > 2 else "",
                        "interfaces": parts[3] if len(parts) > 3 else ""
                    })
    return bridges


def get_bridge_vlan():
    output = run_cmd("bridge vlan show 2>/dev/null")
    if output:
        return output[:500]
    return ""


def get_virtual_interfaces():
    output = run_cmd("ip link show type bridge 2>/dev/null")
    results = []
    if output:
        for line in output.strip().split("\n"):
            if ":" in line and not line.startswith(" "):
                parts = line.split(":")
                if len(parts) >= 2:
                    results.append(parts[1].strip().split("@")[0])
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Network bridge interface monitor — dargslan.com",
        epilog="More tools: pip install dargslan-toolkit | https://dargslan.com"
    )
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    results = {
        "tool": "dargslan-bridge-monitor",
        "version": "1.0.0",
        "bridges": get_bridges(),
        "virtual_bridges": get_virtual_interfaces(),
        "vlan_info": get_bridge_vlan()
    }

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print("=" * 60)
        print("  Network Bridge Monitor — dargslan.com")
        print("=" * 60)
        if not results["bridges"] and not results["virtual_bridges"]:
            print("\n  No bridge interfaces found.")
            print("  Bridges are used in virtualization and container networking.")
        else:
            if results["virtual_bridges"]:
                print("\n  Bridge interfaces:")
                for br in results["virtual_bridges"]:
                    print(f"    - {br}")
            if results["bridges"]:
                print("\n  Bridge details:")
                for br in results["bridges"]:
                    if "name" in br:
                        print(f"    {br['name']} (STP: {br.get('stp', 'N/A')})")
                    else:
                        print(f"    {br.get('raw', '')}")
        print(f"\n  Total bridges: {len(results['virtual_bridges']) or len(results['bridges'])}")
        print("\n  More tools: pip install dargslan-toolkit")
        print("  eBooks: https://dargslan.com/books")

    return 0


if __name__ == "__main__":
    sys.exit(main())
