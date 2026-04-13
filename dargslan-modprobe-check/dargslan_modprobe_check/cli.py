#!/usr/bin/env python3
"""dargslan-modprobe-check — Kernel module load and blacklist checker CLI"""

import subprocess
import json
import argparse
import sys
import os


def run_cmd(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return r.stdout.strip()
    except Exception:
        return ""


def get_loaded_modules():
    output = run_cmd("lsmod 2>/dev/null")
    modules = []
    if output:
        for line in output.strip().split("\n")[1:]:
            parts = line.split()
            if len(parts) >= 3:
                modules.append({
                    "name": parts[0],
                    "size": parts[1],
                    "used_by": parts[2],
                    "dependents": parts[3] if len(parts) > 3 else ""
                })
    return modules


def get_blacklisted():
    blacklisted = []
    conf_dirs = ["/etc/modprobe.d", "/lib/modprobe.d", "/run/modprobe.d"]
    for d in conf_dirs:
        if os.path.isdir(d):
            try:
                for f in os.listdir(d):
                    full = os.path.join(d, f)
                    if os.path.isfile(full) and f.endswith(".conf"):
                        try:
                            with open(full) as fh:
                                for line in fh:
                                    line = line.strip()
                                    if line.startswith("blacklist "):
                                        mod = line.split()[1]
                                        blacklisted.append({
                                            "module": mod,
                                            "file": full
                                        })
                        except PermissionError:
                            pass
            except PermissionError:
                pass
    return blacklisted


def get_module_info(module):
    output = run_cmd(f"modinfo {module} 2>/dev/null | head -10")
    if output:
        info = {}
        for line in output.split("\n"):
            if ":" in line:
                key, _, val = line.partition(":")
                info[key.strip()] = val.strip()
        return info
    return {}


def check_security_modules():
    dangerous = ["vboxdrv", "nbd", "usb-storage", "firewire-core", "thunderbolt"]
    loaded = [m["name"] for m in get_loaded_modules()]
    findings = []
    for mod in dangerous:
        if mod in loaded:
            findings.append(f"WARNING: {mod} is loaded (consider blacklisting)")
    return findings


def main():
    parser = argparse.ArgumentParser(
        description="Kernel module load and blacklist checker — dargslan.com",
        epilog="More tools: pip install dargslan-toolkit | https://dargslan.com"
    )
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--module", help="Check specific module info")
    args = parser.parse_args()

    modules = get_loaded_modules()
    blacklisted = get_blacklisted()
    results = {
        "tool": "dargslan-modprobe-check",
        "version": "1.0.0",
        "loaded_modules_count": len(modules),
        "loaded_modules": modules[:30],
        "blacklisted": blacklisted,
        "security_warnings": check_security_modules()
    }

    if args.module:
        results["module_info"] = get_module_info(args.module)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print("=" * 60)
        print("  Kernel Module & Modprobe Check — dargslan.com")
        print("=" * 60)
        print(f"\n  Loaded modules: {len(modules)}")
        if modules:
            print("\n  Top modules by size:")
            sorted_mods = sorted(modules, key=lambda x: int(x["size"]) if x["size"].isdigit() else 0, reverse=True)
            for m in sorted_mods[:10]:
                print(f"    {m['name']:24s} {m['size']:>10s} bytes  (used: {m['used_by']})")
        if blacklisted:
            print(f"\n  Blacklisted modules: {len(blacklisted)}")
            for b in blacklisted[:10]:
                print(f"    {b['module']} ({b['file']})")
        if results["security_warnings"]:
            print("\n  Security warnings:")
            for w in results["security_warnings"]:
                print(f"    {w}")
        if args.module and "module_info" in results:
            print(f"\n  Module info for '{args.module}':")
            for k, v in results["module_info"].items():
                print(f"    {k}: {v}")
        print("\n  More tools: pip install dargslan-toolkit")
        print("  eBooks: https://dargslan.com/books")

    return 0


if __name__ == "__main__":
    sys.exit(main())
