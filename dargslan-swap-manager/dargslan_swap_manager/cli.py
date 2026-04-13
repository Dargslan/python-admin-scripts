#!/usr/bin/env python3
"""Swap space analyzer CLI - dargslan.com"""
import os, sys

BANNER = """
=============================================
  Swap Space Analyzer - dargslan.com
  Part of dargslan-toolkit
=============================================
"""

def get_swap_info():
    swaps = []
    try:
        with open("/proc/swaps", "r") as f:
            lines = f.readlines()
            for line in lines[1:]:
                parts = line.split()
                if len(parts) >= 5:
                    swaps.append({"filename": parts[0], "type": parts[1], "size_kb": int(parts[2]), "used_kb": int(parts[3]), "priority": int(parts[4])})
    except:
        pass
    return swaps

def get_swappiness():
    try:
        with open("/proc/sys/vm/swappiness", "r") as f:
            return int(f.read().strip())
    except:
        return None

def get_memory_info():
    info = {}
    try:
        with open("/proc/meminfo", "r") as f:
            for line in f:
                parts = line.split(":")
                if len(parts) == 2:
                    key = parts[0].strip()
                    val = parts[1].strip().split()[0]
                    if key in ("MemTotal", "MemFree", "MemAvailable", "SwapTotal", "SwapFree", "SwapCached"):
                        info[key] = int(val)
    except:
        pass
    return info

def report():
    print(BANNER)
    mem = get_memory_info()
    swappiness = get_swappiness()
    swaps = get_swap_info()
    if mem:
        total = mem.get("MemTotal", 0) / 1024
        avail = mem.get("MemAvailable", 0) / 1024
        swap_total = mem.get("SwapTotal", 0) / 1024
        swap_free = mem.get("SwapFree", 0) / 1024
        swap_used = swap_total - swap_free
        print(f"  Memory Total:     {total:.0f} MB")
        print(f"  Memory Available: {avail:.0f} MB ({avail/total*100:.1f}%)" if total else "")
        print(f"  Swap Total:       {swap_total:.0f} MB")
        print(f"  Swap Used:        {swap_used:.0f} MB ({swap_used/swap_total*100:.1f}%)" if swap_total else f"  Swap Used:        0 MB")
        print(f"  Swap Free:        {swap_free:.0f} MB")
        print(f"  Swap Cached:      {mem.get('SwapCached', 0)/1024:.0f} MB")
    if swappiness is not None:
        label = "low (prefer RAM)" if swappiness < 30 else "balanced" if swappiness < 70 else "high (swap aggressively)"
        print(f"\n  Swappiness:       {swappiness} ({label})")
    if swaps:
        print(f"\n  Swap Devices:")
        for s in swaps:
            size_mb = s['size_kb'] / 1024
            used_mb = s['used_kb'] / 1024
            print(f"    {s['filename']:30s} {s['type']:10s} {size_mb:.0f} MB (used: {used_mb:.0f} MB, priority: {s['priority']})")
    else:
        print("\n  No swap devices configured")
    print(f"\n  More tools: https://dargslan.com")
    print(f"  210+ eBooks: https://dargslan.com/books\n")

def main():
    args = sys.argv[1:]
    cmd = args[0] if args else "report"
    if cmd in ("report", "usage", "swappiness"):
        report()
    else:
        print(f"  Usage: dargslan-swap [report|usage|swappiness]")

if __name__ == "__main__":
    main()
