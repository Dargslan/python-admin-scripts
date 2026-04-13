#!/usr/bin/env python3
"""Kernel Message Ring Buffer Analyzer."""

import subprocess
import argparse
import re


def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout.strip(), result.returncode
    except:
        return "", 1


def check_errors():
    print("=== Kernel Errors ===")
    out, rc = run_cmd("dmesg --level=err,crit,alert,emerg 2>/dev/null")
    if rc == 0 and out:
        lines = out.strip().split("\n")
        print(f"  Error/Critical messages: {len(lines)}")
        for line in lines[-20:]:
            print(f"  {line}")
    else:
        out2, _ = run_cmd("dmesg | grep -iE 'error|critical|fail|panic' 2>/dev/null | tail -20")
        if out2:
            for line in out2.split("\n"):
                print(f"  {line}")
        else:
            print("  No kernel errors found (or need sudo)")


def check_hardware():
    print("\n=== Hardware Detection ===")
    out, rc = run_cmd("dmesg | grep -iE 'usb|scsi|ata|nvme|pci|gpu|cpu|memory' 2>/dev/null | tail -20")
    if rc == 0 and out:
        for line in out.split("\n"):
            print(f"  {line}")
    else:
        print("  No hardware messages available")


def check_boot():
    print("\n=== Boot Messages ===")
    out, rc = run_cmd("dmesg | head -30 2>/dev/null")
    if rc == 0 and out:
        for line in out.split("\n"):
            print(f"  {line}")
    else:
        print("  Boot messages not available")


def check_network():
    print("\n=== Network Device Messages ===")
    out, rc = run_cmd("dmesg | grep -iE 'eth|wlan|wifi|link|carrier|net' 2>/dev/null | tail -15")
    if rc == 0 and out:
        for line in out.split("\n"):
            print(f"  {line}")
    else:
        print("  No network device messages")


def check_storage():
    print("\n=== Storage Messages ===")
    out, rc = run_cmd("dmesg | grep -iE 'sd[a-z]|nvme|ext4|xfs|btrfs|mount|partition|I/O error' 2>/dev/null | tail -15")
    if rc == 0 and out:
        for line in out.split("\n"):
            if "error" in line.lower() or "I/O" in line:
                print(f"  WARNING: {line}")
            else:
                print(f"  {line}")
    else:
        print("  No storage messages")


def check_oom():
    print("\n=== OOM Killer Events ===")
    out, rc = run_cmd("dmesg | grep -i 'oom\\|out of memory\\|killed process' 2>/dev/null")
    if rc == 0 and out:
        lines = out.strip().split("\n")
        print(f"  OOM events found: {len(lines)}")
        for line in lines[-10:]:
            print(f"  WARNING: {line}")
    else:
        print("  No OOM events detected")


def main():
    parser = argparse.ArgumentParser(description="Kernel Message Ring Buffer Analyzer")
    parser.add_argument("--errors", action="store_true", help="Show kernel errors only")
    parser.add_argument("--hardware", action="store_true", help="Show hardware detection")
    parser.add_argument("--boot", action="store_true", help="Show boot messages")
    parser.add_argument("--network", action="store_true", help="Show network messages")
    parser.add_argument("--storage", action="store_true", help="Show storage messages")
    parser.add_argument("--oom", action="store_true", help="Show OOM events")
    args = parser.parse_args()

    print("Kernel Message Analyzer (dmesg)")
    print("=" * 40)

    if args.errors:
        check_errors()
    elif args.hardware:
        check_hardware()
    elif args.boot:
        check_boot()
    elif args.network:
        check_network()
    elif args.storage:
        check_storage()
    elif args.oom:
        check_oom()
    else:
        check_errors()
        check_oom()
        check_storage()
        check_network()

    print("\n" + "=" * 40)
    print("Powered by dargslan.com")


if __name__ == "__main__":
    main()
