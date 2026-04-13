#!/usr/bin/env python3
"""Login history analyzer CLI - dargslan.com"""
import subprocess, sys, os

BANNER = """
=============================================
  Login History Analyzer - dargslan.com
  Part of dargslan-toolkit
=============================================
"""

def get_last_logins(count=15):
    try:
        r = subprocess.run(["last", "-n", str(count), "--time-format", "short"], capture_output=True, text=True, timeout=10)
        return r.stdout.strip() if r.returncode == 0 else None
    except:
        try:
            r = subprocess.run(["last", "-n", str(count)], capture_output=True, text=True, timeout=10)
            return r.stdout.strip() if r.returncode == 0 else None
        except:
            return None

def get_failed_logins():
    try:
        r = subprocess.run(["lastb", "-n", "10"], capture_output=True, text=True, timeout=10)
        return r.stdout.strip() if r.returncode == 0 else None
    except:
        return None

def get_current_users():
    try:
        r = subprocess.run(["who"], capture_output=True, text=True, timeout=5)
        return r.stdout.strip() if r.returncode == 0 else None
    except:
        return None

def check_wtmp():
    files = {"/var/log/wtmp": "Successful logins", "/var/log/btmp": "Failed logins", "/var/log/lastlog": "Last login records"}
    found = []
    for path, desc in files.items():
        if os.path.exists(path):
            size = os.path.getsize(path)
            found.append((path, desc, size))
    return found

def report():
    print(BANNER)
    current = get_current_users()
    if current:
        lines = current.splitlines()
        print(f"  Currently logged in ({len(lines)}):")
        for l in lines:
            print(f"    {l}")
    else:
        print("  No users currently logged in")
    last = get_last_logins()
    if last:
        print(f"\n  Recent logins:")
        for l in last.splitlines()[:12]:
            if l.strip():
                print(f"    {l}")
    failed = get_failed_logins()
    if failed and failed.strip():
        lines = [l for l in failed.splitlines() if l.strip()]
        print(f"\n  Failed login attempts ({len(lines)}):")
        for l in lines[:8]:
            print(f"    {l}")
    elif failed is None:
        print("\n  Failed logins: (need root access for lastb)")
    log_files = check_wtmp()
    if log_files:
        print(f"\n  Login log files:")
        for path, desc, size in log_files:
            print(f"    {path:25s} {size/1024:8.0f} KB  ({desc})")
    print(f"\n  More tools: https://dargslan.com")
    print(f"  210+ eBooks: https://dargslan.com/books\n")

def main():
    args = sys.argv[1:]
    cmd = args[0] if args else "report"
    if cmd in ("report", "failed", "sessions", "current"):
        report()
    else:
        print(f"  Usage: dargslan-logins [report|failed|sessions|current]")

if __name__ == "__main__":
    main()
