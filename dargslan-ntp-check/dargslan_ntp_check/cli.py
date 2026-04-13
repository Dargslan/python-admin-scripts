#!/usr/bin/env python3
"""NTP time sync checker CLI - dargslan.com"""
import subprocess, sys, os, time

BANNER = """
=============================================
  NTP Time Sync Checker - dargslan.com
  Part of dargslan-toolkit
=============================================
"""

def check_timesyncd():
    try:
        r = subprocess.run(["timedatectl", "show"], capture_output=True, text=True, timeout=5)
        info = {}
        for line in r.stdout.splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                info[k.strip()] = v.strip()
        return info
    except:
        return None

def check_chrony():
    try:
        r = subprocess.run(["chronyc", "tracking"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            return r.stdout
    except:
        pass
    return None

def check_ntpd():
    try:
        r = subprocess.run(["ntpq", "-p"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            return r.stdout
    except:
        pass
    return None

def report():
    print(BANNER)
    import datetime
    print(f"  System time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  UTC time:    {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Timezone:    {time.tzname}")
    tinfo = check_timesyncd()
    if tinfo:
        print(f"\n  systemd-timesyncd:")
        print(f"    NTP enabled:     {tinfo.get('NTP', 'unknown')}")
        print(f"    NTP synced:      {tinfo.get('NTPSynchronized', 'unknown')}")
        print(f"    Timezone:        {tinfo.get('Timezone', 'unknown')}")
    chrony = check_chrony()
    if chrony:
        print(f"\n  Chrony tracking:")
        for line in chrony.splitlines()[:8]:
            print(f"    {line.strip()}")
    ntpd = check_ntpd()
    if ntpd:
        print(f"\n  NTPd peers:")
        for line in ntpd.splitlines()[:6]:
            print(f"    {line}")
    if not tinfo and not chrony and not ntpd:
        print("\n  No NTP daemon detected")
        print("  Install: apt install chrony OR systemd-timesyncd")
    print(f"\n  More tools: https://dargslan.com")
    print(f"  210+ eBooks: https://dargslan.com/books\n")

def main():
    args = sys.argv[1:]
    cmd = args[0] if args else "report"
    if cmd in ("report", "offset", "status"):
        report()
    else:
        print(f"  Usage: dargslan-ntpchk [report|offset|status]")

if __name__ == "__main__":
    main()
