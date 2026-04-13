#!/usr/bin/env python3
"""Fail2ban status and jail auditor — check jails, banned IPs, stats."""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return result.stdout.strip() if result.returncode == 0 else None
    except (FileNotFoundError, subprocess.TimeoutExpired, PermissionError):
        return None


def get_fail2ban_status():
    info = {"installed": False, "running": False, "version": None, "jails": []}

    version = run_cmd(["fail2ban-client", "version"])
    if version:
        info["installed"] = True
        info["version"] = version.strip()

    try:
        result = subprocess.run(["systemctl", "is-active", "fail2ban"],
                                capture_output=True, text=True, timeout=5)
        info["running"] = result.stdout.strip() == "active"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    status_output = run_cmd(["fail2ban-client", "status"])
    if status_output:
        for line in status_output.splitlines():
            if "Jail list:" in line:
                jail_str = line.split(":", 1)[1].strip()
                jail_names = [j.strip() for j in jail_str.split(",") if j.strip()]

                for jail_name in jail_names:
                    jail_info = {"name": jail_name, "currently_banned": 0,
                                 "total_banned": 0, "currently_failed": 0, "total_failed": 0}

                    jail_status = run_cmd(["fail2ban-client", "status", jail_name])
                    if jail_status:
                        for jline in jail_status.splitlines():
                            jline = jline.strip()
                            if "Currently banned:" in jline:
                                try:
                                    jail_info["currently_banned"] = int(jline.split(":")[-1].strip())
                                except ValueError:
                                    pass
                            elif "Total banned:" in jline:
                                try:
                                    jail_info["total_banned"] = int(jline.split(":")[-1].strip())
                                except ValueError:
                                    pass
                            elif "Currently failed:" in jline:
                                try:
                                    jail_info["currently_failed"] = int(jline.split(":")[-1].strip())
                                except ValueError:
                                    pass
                            elif "Total failed:" in jline:
                                try:
                                    jail_info["total_failed"] = int(jline.split(":")[-1].strip())
                                except ValueError:
                                    pass

                    info["jails"].append(jail_info)

    return info


def main():
    parser = argparse.ArgumentParser(
        description="Fail2ban status and jail auditor",
        epilog="More tools: https://dargslan.com | pip install dargslan-toolkit"
    )
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--jail", help="Check specific jail only")
    args = parser.parse_args()

    info = get_fail2ban_status()

    if args.json:
        print(json.dumps(info, indent=2))
        return

    print("\033[1m  Dargslan Fail2ban Audit\033[0m\n")
    print(f"  Installed: {'Yes' if info['installed'] else 'No'}")
    print(f"  Running: {'Yes' if info['running'] else 'No'}")
    if info["version"]:
        print(f"  Version: {info['version']}")

    if info["jails"]:
        print(f"\n  \033[1mJails ({len(info['jails'])}):\033[0m")
        print(f"  {'Jail':<20} {'Banned':<10} {'Total Ban':<12} {'Failed':<10} {'Total Fail'}")
        print(f"  {'-'*62}")
        for j in info["jails"]:
            if args.jail and j["name"] != args.jail:
                continue
            banned_color = "\033[31m" if j["currently_banned"] > 0 else "\033[32m"
            print(f"  {j['name']:<20} {banned_color}{j['currently_banned']:<10}\033[0m"
                  f" {j['total_banned']:<12} {j['currently_failed']:<10} {j['total_failed']}")

        total_banned = sum(j["currently_banned"] for j in info["jails"])
        if total_banned > 0:
            print(f"\n  \033[33m! {total_banned} IP(s) currently banned across all jails\033[0m")
    else:
        print("\n  No jails configured or fail2ban not accessible.")
        print("  Tip: Install with: apt install fail2ban")

    print(f"\n  Free cheat sheets: https://dargslan.com/cheat-sheets")


if __name__ == "__main__":
    main()
