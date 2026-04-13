#!/usr/bin/env python3
"""dargslan-lsof-audit — Open files and ports auditor CLI"""

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


def get_listening_ports():
    output = run_cmd("lsof -i -P -n 2>/dev/null | grep LISTEN | head -20")
    if not output:
        output = run_cmd("ss -tlnp 2>/dev/null | head -20")
    results = []
    if output:
        for line in output.strip().split("\n"):
            if line.strip():
                results.append(line.strip())
    return results


def get_open_file_count():
    output = run_cmd("lsof 2>/dev/null | wc -l")
    try:
        return int(output)
    except (ValueError, TypeError):
        return 0


def get_deleted_files():
    output = run_cmd("lsof 2>/dev/null | grep '(deleted)' | head -10")
    results = []
    if output:
        for line in output.strip().split("\n"):
            if line.strip():
                results.append(line.strip()[:100])
    return results


def get_top_processes():
    output = run_cmd("lsof 2>/dev/null | awk '{print $1}' | sort | uniq -c | sort -rn | head -10")
    results = []
    if output:
        for line in output.strip().split("\n"):
            if line.strip():
                parts = line.strip().split()
                if len(parts) >= 2:
                    results.append({"count": parts[0], "process": parts[1]})
    return results


def get_network_connections():
    output = run_cmd("lsof -i -P -n 2>/dev/null | grep -E 'ESTABLISHED|SYN' | head -10")
    if not output:
        output = run_cmd("ss -tnp 2>/dev/null | grep ESTAB | head -10")
    results = []
    if output:
        for line in output.strip().split("\n"):
            if line.strip():
                results.append(line.strip()[:120])
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Open files and ports auditor — dargslan.com",
        epilog="More tools: pip install dargslan-toolkit | https://dargslan.com"
    )
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--ports", action="store_true", help="Show listening ports only")
    args = parser.parse_args()

    results = {
        "tool": "dargslan-lsof-audit",
        "version": "1.0.0",
        "open_file_count": get_open_file_count(),
        "listening_ports": get_listening_ports(),
        "deleted_files": get_deleted_files(),
        "top_processes": get_top_processes(),
        "network_connections": get_network_connections()
    }

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print("=" * 60)
        print("  Open Files & Ports Audit — dargslan.com")
        print("=" * 60)
        print(f"\n  Open files total: {results['open_file_count']}")
        if results["listening_ports"]:
            print(f"\n  Listening ports ({len(results['listening_ports'])}):")
            for p in results["listening_ports"][:8]:
                print(f"    {p[:80]}")
        if results["top_processes"]:
            print("\n  Top processes by open files:")
            for p in results["top_processes"][:5]:
                print(f"    {p['process']}: {p['count']} files")
        if results["deleted_files"]:
            print(f"\n  Deleted but open files: {len(results['deleted_files'])}")
        if results["network_connections"]:
            print(f"\n  Active connections: {len(results['network_connections'])}")
        print("\n  More tools: pip install dargslan-toolkit")
        print("  eBooks: https://dargslan.com/books")

    return 0


if __name__ == "__main__":
    sys.exit(main())
