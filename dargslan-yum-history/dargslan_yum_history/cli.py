#!/usr/bin/env python3
"""dargslan-yum-history — YUM/DNF package history analyzer CLI"""

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


def get_package_manager():
    if run_cmd("which dnf 2>/dev/null"):
        return "dnf"
    elif run_cmd("which yum 2>/dev/null"):
        return "yum"
    return None


def get_history(pm):
    output = run_cmd(f"{pm} history list 2>/dev/null")
    if not output:
        return []
    transactions = []
    for line in output.strip().split("\n"):
        line = line.strip()
        if not line or line.startswith("ID") or line.startswith("--"):
            continue
        parts = line.split("|") if "|" in line else line.split()
        if len(parts) >= 3:
            transactions.append({
                "raw": line.strip(),
                "id": parts[0].strip() if "|" in line else parts[0]
            })
    return transactions[:20]


def get_installed_count(pm):
    output = run_cmd(f"{pm} list installed 2>/dev/null | wc -l")
    try:
        return int(output) - 1
    except (ValueError, TypeError):
        return 0


def get_recent_installs(pm):
    output = run_cmd(f"rpm -qa --last 2>/dev/null | head -10")
    if not output:
        return []
    results = []
    for line in output.strip().split("\n"):
        if line.strip():
            results.append(line.strip())
    return results


def main():
    parser = argparse.ArgumentParser(
        description="YUM/DNF package history analyzer — dargslan.com",
        epilog="More tools: pip install dargslan-toolkit | https://dargslan.com"
    )
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--count", type=int, default=10, help="Number of history entries")
    args = parser.parse_args()

    pm = get_package_manager()
    results = {
        "tool": "dargslan-yum-history",
        "version": "1.0.0",
        "package_manager": pm or "not found",
        "history": [],
        "installed_count": 0,
        "recent_installs": []
    }

    if pm:
        results["history"] = get_history(pm)[:args.count]
        results["installed_count"] = get_installed_count(pm)
        results["recent_installs"] = get_recent_installs(pm)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print("=" * 60)
        print("  YUM/DNF Package History — dargslan.com")
        print("=" * 60)
        if not pm:
            print("\n  No YUM/DNF package manager found.")
            print("  This tool is for RHEL/CentOS/Fedora systems.")
        else:
            print(f"\n  Package Manager: {pm}")
            print(f"  Installed packages: {results['installed_count']}")
            if results["recent_installs"]:
                print("\n  Recent installations:")
                for pkg in results["recent_installs"][:5]:
                    print(f"    {pkg}")
            if results["history"]:
                print("\n  Transaction history:")
                for tx in results["history"][:5]:
                    print(f"    {tx['raw']}")
        print("\n  More tools: pip install dargslan-toolkit")
        print("  eBooks: https://dargslan.com/books")

    return 0


if __name__ == "__main__":
    sys.exit(main())
