#!/usr/bin/env python3
"""APT Package Manager Health Checker - Check APT status and package health."""

import subprocess
import sys
import argparse


def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "Command timed out", 1
    except Exception as e:
        return "", str(e), 1


def check_updates():
    print("=== Pending Updates ===")
    out, err, rc = run_cmd("apt list --upgradable 2>/dev/null | grep -v 'Listing'")
    if rc == 0 and out:
        lines = out.strip().split("\n")
        print(f"  Packages with updates available: {len(lines)}")
        for line in lines[:20]:
            pkg = line.split("/")[0] if "/" in line else line
            print(f"    - {pkg}")
        if len(lines) > 20:
            print(f"    ... and {len(lines) - 20} more")
    else:
        print("  All packages are up to date")


def check_broken():
    print("\n=== Broken Packages ===")
    out, err, rc = run_cmd("dpkg --audit 2>/dev/null")
    if rc == 0 and out:
        print(f"  WARNING: Broken packages detected:")
        print(f"  {out}")
    else:
        print("  No broken packages found")

    out2, err2, rc2 = run_cmd("dpkg -l | grep -E '^(iF|iU|iW|iH)' 2>/dev/null")
    if rc2 == 0 and out2:
        lines = out2.strip().split("\n")
        print(f"  Packages in inconsistent state: {len(lines)}")
    else:
        print("  All packages in consistent state")


def check_autoremove():
    print("\n=== Unused Dependencies ===")
    out, err, rc = run_cmd("apt-get --dry-run autoremove 2>/dev/null | grep '^Remv'")
    if rc == 0 and out:
        lines = out.strip().split("\n")
        print(f"  Packages that can be autoremoved: {len(lines)}")
        for line in lines[:15]:
            pkg = line.replace("Remv ", "").split(" ")[0]
            print(f"    - {pkg}")
    else:
        print("  No unused dependencies found")


def check_sources():
    print("\n=== APT Sources ===")
    out, err, rc = run_cmd("grep -r '^deb ' /etc/apt/sources.list /etc/apt/sources.list.d/ 2>/dev/null")
    if rc == 0 and out:
        lines = out.strip().split("\n")
        print(f"  Configured repositories: {len(lines)}")
        for line in lines:
            print(f"    {line}")
    else:
        print("  Could not read APT sources")


def check_cache():
    print("\n=== APT Cache ===")
    out, err, rc = run_cmd("du -sh /var/cache/apt/archives/ 2>/dev/null")
    if rc == 0 and out:
        size = out.split()[0] if out else "unknown"
        print(f"  Cache size: {size}")
    out2, err2, rc2 = run_cmd("ls /var/cache/apt/archives/*.deb 2>/dev/null | wc -l")
    if rc2 == 0 and out2:
        print(f"  Cached .deb files: {out2}")


def main():
    parser = argparse.ArgumentParser(description="APT Package Manager Health Checker")
    parser.add_argument("--updates", action="store_true", help="Check pending updates only")
    parser.add_argument("--broken", action="store_true", help="Check broken packages only")
    parser.add_argument("--sources", action="store_true", help="Show APT sources only")
    parser.add_argument("--cache", action="store_true", help="Show cache info only")
    args = parser.parse_args()

    print("APT Package Manager Health Check")
    print("=" * 40)

    if args.updates:
        check_updates()
    elif args.broken:
        check_broken()
    elif args.sources:
        check_sources()
    elif args.cache:
        check_cache()
    else:
        check_updates()
        check_broken()
        check_autoremove()
        check_sources()
        check_cache()

    print("\n" + "=" * 40)
    print("Powered by dargslan.com")


if __name__ == "__main__":
    main()
