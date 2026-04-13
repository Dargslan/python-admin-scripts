#!/usr/bin/env python3
"""Temporary File Cleaner - Find and clean temporary files."""

import subprocess
import os
import argparse
from datetime import datetime


def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout.strip(), result.returncode
    except:
        return "", 1


def human_size(size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}PB"


def scan_tmp_dirs():
    print("=== Temporary Directory Analysis ===")
    tmp_dirs = ["/tmp", "/var/tmp", "/var/cache", "/var/log"]
    total_size = 0
    total_files = 0

    for d in tmp_dirs:
        if os.path.exists(d):
            out, rc = run_cmd(f"du -sb {d} 2>/dev/null")
            size = int(out.split()[0]) if rc == 0 and out else 0
            out2, rc2 = run_cmd(f"find {d} -type f 2>/dev/null | wc -l")
            count = int(out2) if rc2 == 0 and out2 else 0
            total_size += size
            total_files += count
            print(f"  {d}: {human_size(size)} ({count} files)")

    print(f"\n  Total: {human_size(total_size)} across {total_files} files")


def find_old_files(days=7):
    print(f"\n=== Files Older Than {days} Days ===")
    tmp_dirs = ["/tmp", "/var/tmp"]
    old_files = []

    for d in tmp_dirs:
        if os.path.exists(d):
            out, rc = run_cmd(f"find {d} -type f -mtime +{days} 2>/dev/null")
            if rc == 0 and out:
                for f in out.split("\n"):
                    if f:
                        try:
                            size = os.path.getsize(f)
                            mtime = os.path.getmtime(f)
                            old_files.append((f, size, mtime))
                        except:
                            pass

    if old_files:
        old_files.sort(key=lambda x: x[1], reverse=True)
        total = sum(f[1] for f in old_files)
        print(f"  Found {len(old_files)} old files ({human_size(total)} total)")
        for f, size, mtime in old_files[:20]:
            age = datetime.now() - datetime.fromtimestamp(mtime)
            print(f"  {human_size(size):>8}  {age.days}d ago  {f}")
        if len(old_files) > 20:
            print(f"  ... and {len(old_files) - 20} more files")
    else:
        print("  No old temporary files found")


def find_large_files(min_size_mb=10):
    print(f"\n=== Large Temp Files (>{min_size_mb}MB) ===")
    tmp_dirs = ["/tmp", "/var/tmp", "/var/cache"]
    large_files = []

    for d in tmp_dirs:
        if os.path.exists(d):
            out, rc = run_cmd(f"find {d} -type f -size +{min_size_mb}M 2>/dev/null")
            if rc == 0 and out:
                for f in out.split("\n"):
                    if f:
                        try:
                            large_files.append((f, os.path.getsize(f)))
                        except:
                            pass

    if large_files:
        large_files.sort(key=lambda x: x[1], reverse=True)
        total = sum(f[1] for f in large_files)
        print(f"  Found {len(large_files)} large files ({human_size(total)} total)")
        for f, size in large_files[:15]:
            print(f"  {human_size(size):>8}  {f}")
    else:
        print("  No large temporary files found")


def check_cache_dirs():
    print("\n=== User Cache Directories ===")
    home = os.path.expanduser("~")
    cache_dirs = [".cache", ".local/share/Trash", ".npm/_cacache", ".cache/pip", ".cargo/registry"]
    for d in cache_dirs:
        path = os.path.join(home, d)
        if os.path.exists(path):
            out, rc = run_cmd(f"du -sb {path} 2>/dev/null")
            size = int(out.split()[0]) if rc == 0 and out else 0
            if size > 1024 * 1024:
                print(f"  {human_size(size):>8}  ~/{d}")


def main():
    parser = argparse.ArgumentParser(description="Temporary File Cleaner")
    parser.add_argument("--scan", action="store_true", help="Scan tmp directories")
    parser.add_argument("--old", type=int, metavar="DAYS", help="Find files older than N days")
    parser.add_argument("--large", type=int, metavar="MB", help="Find files larger than N MB")
    parser.add_argument("--cache", action="store_true", help="Check user cache directories")
    args = parser.parse_args()

    print("Temporary File Cleaner")
    print("=" * 40)

    if args.scan:
        scan_tmp_dirs()
    elif args.old is not None:
        find_old_files(args.old)
    elif args.large is not None:
        find_large_files(args.large)
    elif args.cache:
        check_cache_dirs()
    else:
        scan_tmp_dirs()
        find_old_files()
        find_large_files()
        check_cache_dirs()

    print("\n" + "=" * 40)
    print("Powered by dargslan.com")


if __name__ == "__main__":
    main()
