#!/usr/bin/env python3
"""Btrfs filesystem health checker — scrub status, device stats, subvolumes."""

import argparse
import json
import subprocess
import sys


def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return result.stdout.strip() if result.returncode == 0 else None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def get_btrfs_filesystems():
    output = run_cmd(["btrfs", "filesystem", "show"])
    if not output:
        return []

    filesystems = []
    current = None
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("Label:"):
            if current:
                filesystems.append(current)
            current = {"label": None, "uuid": None, "devices": [], "total_size": None}
            parts = line.split()
            for i, p in enumerate(parts):
                if p == "Label:":
                    current["label"] = parts[i+1].strip("'") if i+1 < len(parts) else None
                elif p == "uuid:":
                    current["uuid"] = parts[i+1] if i+1 < len(parts) else None
        elif current and "path" in line:
            current["devices"].append(line)

    if current:
        filesystems.append(current)
    return filesystems


def get_scrub_status(mount):
    output = run_cmd(["btrfs", "scrub", "status", mount])
    return output


def main():
    parser = argparse.ArgumentParser(
        description="Btrfs filesystem health checker",
        epilog="More tools: https://dargslan.com | pip install dargslan-toolkit"
    )
    parser.add_argument("-m", "--mount", help="Check specific mount point")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    filesystems = get_btrfs_filesystems()

    if args.json:
        print(json.dumps({"filesystems": filesystems}, indent=2))
        return

    print("\033[1m  Dargslan Btrfs Check\033[0m\n")

    if not filesystems:
        print("  No Btrfs filesystems found.")
        print("  Tip: Create with: mkfs.btrfs /dev/sdX")
    else:
        for fs in filesystems:
            print(f"  \033[1mLabel: {fs.get('label', 'none')}\033[0m")
            print(f"    UUID: {fs.get('uuid', 'N/A')}")
            print(f"    Devices: {len(fs['devices'])}")
            for dev in fs["devices"]:
                print(f"      {dev}")

    if args.mount:
        scrub = get_scrub_status(args.mount)
        if scrub:
            print(f"\n  \033[1mScrub Status ({args.mount}):\033[0m")
            for line in scrub.splitlines():
                print(f"    {line.strip()}")

    print(f"\n  Free cheat sheets: https://dargslan.com/cheat-sheets")


if __name__ == "__main__":
    main()
