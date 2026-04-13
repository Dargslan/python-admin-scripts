#!/usr/bin/env python3
"""dargslan-xfs-check — XFS filesystem health checker CLI"""

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


def get_xfs_filesystems():
    results = []
    output = run_cmd("mount -t xfs 2>/dev/null")
    if not output:
        output = run_cmd("df -T 2>/dev/null | grep -i xfs")
    if output:
        for line in output.strip().split("\n"):
            parts = line.split()
            if len(parts) >= 3:
                results.append({
                    "device": parts[0],
                    "mountpoint": parts[2] if "on" in line else parts[-1],
                    "type": "xfs"
                })
    return results


def check_xfs_info(device):
    info = {}
    output = run_cmd(f"xfs_info {device} 2>/dev/null")
    if output:
        info["raw_info"] = output[:500]
        for line in output.split("\n"):
            if "bsize=" in line:
                for part in line.split():
                    if part.startswith("bsize="):
                        info["block_size"] = part.split("=")[1]
            if "agcount=" in line:
                for part in line.split():
                    if part.startswith("agcount="):
                        info["ag_count"] = part.split("=")[1]
    return info


def check_fragmentation(mountpoint):
    output = run_cmd(f"xfs_db -r -c 'frag -f' {mountpoint} 2>/dev/null")
    if output:
        return output[:200]
    return "N/A (requires root or xfs_db)"


def main():
    parser = argparse.ArgumentParser(
        description="XFS filesystem health checker — dargslan.com",
        epilog="More tools: pip install dargslan-toolkit | https://dargslan.com"
    )
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--device", help="Check specific device")
    args = parser.parse_args()

    results = {
        "tool": "dargslan-xfs-check",
        "version": "1.0.0",
        "xfs_filesystems": [],
        "xfs_found": False
    }

    filesystems = get_xfs_filesystems()
    results["xfs_found"] = len(filesystems) > 0
    results["xfs_filesystems"] = filesystems

    if args.device:
        info = check_xfs_info(args.device)
        results["device_info"] = info

    for fs in filesystems:
        fs["info"] = check_xfs_info(fs["device"])

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print("=" * 60)
        print("  XFS Filesystem Health Check — dargslan.com")
        print("=" * 60)
        if not filesystems:
            print("\n  No XFS filesystems found on this system.")
            print("  XFS is common on RHEL/CentOS servers.")
        else:
            for fs in filesystems:
                print(f"\n  Device: {fs['device']}")
                print(f"  Mount:  {fs['mountpoint']}")
                if "info" in fs and fs["info"]:
                    for k, v in fs["info"].items():
                        if k != "raw_info":
                            print(f"  {k}: {v}")
        print(f"\n  Total XFS filesystems: {len(filesystems)}")
        print("\n  More tools: pip install dargslan-toolkit")
        print("  eBooks: https://dargslan.com/books")

    return 0


if __name__ == "__main__":
    sys.exit(main())
