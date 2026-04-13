#!/usr/bin/env python3
"""Systemd timer analyzer CLI - dargslan.com"""
import subprocess, sys

BANNER = """
=============================================
  Systemd Timer Analyzer - dargslan.com
  Part of dargslan-toolkit
=============================================
"""

def get_timers():
    timers = []
    try:
        result = subprocess.run(["systemctl", "list-timers", "--all", "--no-pager", "--no-legend"], capture_output=True, text=True, timeout=10)
        for line in result.stdout.strip().splitlines():
            if line.strip():
                timers.append(line.strip())
    except:
        pass
    return timers

def get_timer_units():
    units = []
    try:
        result = subprocess.run(["systemctl", "list-unit-files", "--type=timer", "--no-pager", "--no-legend"], capture_output=True, text=True, timeout=10)
        for line in result.stdout.strip().splitlines():
            parts = line.split()
            if len(parts) >= 2:
                units.append({"name": parts[0], "state": parts[1]})
    except:
        pass
    return units

def report():
    print(BANNER)
    timers = get_timers()
    units = get_timer_units()
    if timers:
        print(f"  Active Timers ({len(timers)}):")
        print(f"  {'NEXT':30s} {'LEFT':15s} {'UNIT':30s}")
        print(f"  {'-'*75}")
        for t in timers[:20]:
            print(f"  {t}")
    else:
        print("  No active timers found (systemd may not be available)")
    if units:
        enabled = [u for u in units if u['state'] == 'enabled']
        disabled = [u for u in units if u['state'] != 'enabled']
        print(f"\n  Timer Units: {len(units)} total ({len(enabled)} enabled, {len(disabled)} disabled)")
        for u in units[:15]:
            status = "ON" if u['state'] == 'enabled' else "OFF"
            print(f"    [{status:3s}] {u['name']}")
    print(f"\n  More tools: https://dargslan.com")
    print(f"  210+ eBooks: https://dargslan.com/books\n")

def main():
    args = sys.argv[1:]
    cmd = args[0] if args else "report"
    if cmd in ("report", "list", "next"):
        report()
    else:
        print(f"  Usage: dargslan-timer [report|list|next]")

if __name__ == "__main__":
    main()
