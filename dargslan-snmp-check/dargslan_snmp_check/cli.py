#!/usr/bin/env python3
"""SNMP configuration and security auditor."""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def check_snmp_config():
    config = {"installed": False, "running": False, "version": None,
              "communities": [], "users": [], "issues": []}

    for cmd in ["snmpd", "/usr/sbin/snmpd"]:
        try:
            result = subprocess.run([cmd, "--version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0 or result.stderr:
                config["installed"] = True
                output = result.stdout + result.stderr
                for line in output.splitlines():
                    if "NET-SNMP" in line or "version" in line.lower():
                        config["version"] = line.strip()
                        break
                break
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue

    try:
        result = subprocess.run(["systemctl", "is-active", "snmpd"],
                                capture_output=True, text=True, timeout=5)
        config["running"] = result.stdout.strip() == "active"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    for conf_path in ["/etc/snmp/snmpd.conf", "/etc/snmpd.conf"]:
        p = Path(conf_path)
        if p.exists():
            try:
                for line in p.read_text().splitlines():
                    line = line.strip()
                    if line.startswith("#") or not line:
                        continue
                    if line.startswith("rocommunity") or line.startswith("rwcommunity"):
                        parts = line.split()
                        if len(parts) >= 2:
                            community = parts[1]
                            access = "read-only" if "ro" in parts[0] else "read-write"
                            config["communities"].append({"name": community, "access": access})
                            if community == "public":
                                config["issues"].append("Default 'public' community string in use")
                            if "rw" in parts[0]:
                                config["issues"].append(f"Read-write community '{community}' configured")
                    elif line.startswith("createUser") or line.startswith("rouser") or line.startswith("rwuser"):
                        config["users"].append(line.split()[1] if len(line.split()) > 1 else line)
            except PermissionError:
                config["issues"].append(f"Cannot read {conf_path} (permission denied)")
            break

    return config


def main():
    parser = argparse.ArgumentParser(
        description="SNMP configuration and security auditor",
        epilog="More tools: https://dargslan.com | pip install dargslan-toolkit"
    )
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    config = check_snmp_config()

    if args.json:
        print(json.dumps(config, indent=2))
        return

    print("\033[1m  Dargslan SNMP Check\033[0m\n")
    print(f"  Installed: {'Yes' if config['installed'] else 'No'}")
    print(f"  Running: {'Yes' if config['running'] else 'No'}")
    if config["version"]:
        print(f"  Version: {config['version']}")

    if config["communities"]:
        print(f"\n  \033[1mCommunities:\033[0m")
        for c in config["communities"]:
            print(f"    {c['name']} ({c['access']})")

    if config["users"]:
        print(f"\n  \033[1mSNMPv3 Users:\033[0m")
        for u in config["users"]:
            print(f"    {u}")

    if config["issues"]:
        print(f"\n  \033[33mSecurity Issues ({len(config['issues'])}):\033[0m")
        for i in config["issues"]:
            print(f"    ! {i}")
    else:
        print(f"\n  \033[32mNo security issues found.\033[0m")

    print(f"\n  Free cheat sheets: https://dargslan.com/cheat-sheets")


if __name__ == "__main__":
    main()
