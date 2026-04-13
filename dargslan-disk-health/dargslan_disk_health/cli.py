#!/usr/bin/env python3
"""Disk Health Monitor - Check disk health and SMART data."""

import subprocess
import os
import argparse


def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout.strip(), result.returncode
    except:
        return "", 1


def check_disk_usage():
    print("=== Disk Usage ===")
    out, rc = run_cmd("df -h --output=source,fstype,size,used,avail,pcent,target -x tmpfs -x devtmpfs 2>/dev/null")
    if rc == 0 and out:
        lines = out.strip().split("\n")
        for line in lines:
            if any(f"{p}%" in line for p in range(90, 101)):
                print(f"  WARNING: {line}")
            else:
                print(f"  {line}")
    else:
        out2, _ = run_cmd("df -h")
        print(f"  {out2}")


def check_io_stats():
    print("\n=== I/O Statistics ===")
    if os.path.exists("/proc/diskstats"):
        out, rc = run_cmd("iostat -dx 1 1 2>/dev/null")
        if rc == 0 and out:
            print(f"  {out}")
        else:
            out2, _ = run_cmd("head -10 /proc/diskstats 2>/dev/null")
            if out2:
                print("  Device     Reads    Writes")
                for line in out2.split("\n"):
                    parts = line.split()
                    if len(parts) >= 14:
                        print(f"  {parts[2]:<12} {parts[3]:<10} {parts[7]}")
    else:
        print("  /proc/diskstats not available")


def check_smart():
    print("\n=== SMART Health ===")
    out, rc = run_cmd("lsblk -d -n -o NAME,TYPE 2>/dev/null")
    if rc == 0 and out:
        for line in out.split("\n"):
            parts = line.split()
            if len(parts) >= 2 and parts[1] == "disk":
                dev = parts[0]
                smart_out, smart_rc = run_cmd(f"sudo smartctl -H /dev/{dev} 2>/dev/null")
                if smart_rc == 0 and "PASSED" in smart_out:
                    print(f"  /dev/{dev}: HEALTHY (PASSED)")
                elif smart_rc == 0 and "FAILED" in smart_out:
                    print(f"  /dev/{dev}: WARNING - SMART test FAILED!")
                else:
                    print(f"  /dev/{dev}: SMART not available (may need sudo)")
    else:
        print("  Could not enumerate disks")


def check_filesystem():
    print("\n=== Filesystem Health ===")
    out, rc = run_cmd("mount | grep -E '^/dev' 2>/dev/null")
    if rc == 0 and out:
        for line in out.split("\n"):
            parts = line.split()
            dev = parts[0] if parts else ""
            mountpoint = parts[2] if len(parts) > 2 else ""
            fstype = parts[4] if len(parts) > 4 else ""
            opts = parts[5] if len(parts) > 5 else ""
            ro = "READ-ONLY" if "ro," in opts or "(ro" in opts else "read-write"
            print(f"  {dev} on {mountpoint} ({fstype}) [{ro}]")
    else:
        print("  Could not check mounted filesystems")


def check_inodes():
    print("\n=== Inode Usage ===")
    out, rc = run_cmd("df -i -x tmpfs -x devtmpfs 2>/dev/null")
    if rc == 0 and out:
        lines = out.strip().split("\n")
        for line in lines:
            if any(f"{p}%" in line for p in range(90, 101)):
                print(f"  WARNING: {line}")
            else:
                print(f"  {line}")


def main():
    parser = argparse.ArgumentParser(description="Disk Health Monitor")
    parser.add_argument("--usage", action="store_true", help="Show disk usage only")
    parser.add_argument("--smart", action="store_true", help="Show SMART health only")
    parser.add_argument("--io", action="store_true", help="Show I/O statistics only")
    parser.add_argument("--inodes", action="store_true", help="Show inode usage only")
    args = parser.parse_args()

    print("Disk Health Monitor")
    print("=" * 40)

    if args.usage:
        check_disk_usage()
    elif args.smart:
        check_smart()
    elif args.io:
        check_io_stats()
    elif args.inodes:
        check_inodes()
    else:
        check_disk_usage()
        check_io_stats()
        check_smart()
        check_filesystem()
        check_inodes()

    print("\n" + "=" * 40)
    print("Powered by dargslan.com")


if __name__ == "__main__":
    main()
