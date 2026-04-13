#!/usr/bin/env python3
"""Cgroup v2 Resource Limit Auditor."""

import subprocess
import os
import argparse


def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout.strip(), result.returncode
    except:
        return "", 1


def human_bytes(n):
    for u in ['B', 'KB', 'MB', 'GB', 'TB']:
        if n < 1024:
            return f"{n:.1f}{u}"
        n /= 1024
    return f"{n:.1f}PB"


def check_cgroup_version():
    print("=== Cgroup Version ===")
    out, rc = run_cmd("stat -fc %T /sys/fs/cgroup/ 2>/dev/null")
    if rc == 0 and out:
        if "cgroup2" in out:
            print("  Version: cgroup v2 (unified hierarchy)")
        elif "tmpfs" in out:
            print("  Version: cgroup v1 (legacy)")
        else:
            print(f"  Filesystem type: {out}")

    controllers, _ = run_cmd("cat /sys/fs/cgroup/cgroup.controllers 2>/dev/null")
    if controllers:
        print(f"  Available controllers: {controllers}")


def check_slices():
    print("\n=== System Slices ===")
    out, rc = run_cmd("systemctl list-units --type=slice --no-pager --no-legend 2>/dev/null")
    if rc == 0 and out:
        for line in out.split("\n"):
            parts = line.split()
            if parts:
                slice_name = parts[0]
                print(f"  {slice_name}")

                mem_out, _ = run_cmd(f"cat /sys/fs/cgroup/{slice_name.replace('.slice','')}/memory.current 2>/dev/null")
                mem_max, _ = run_cmd(f"cat /sys/fs/cgroup/{slice_name.replace('.slice','')}/memory.max 2>/dev/null")
                if mem_out:
                    current = int(mem_out) if mem_out.isdigit() else 0
                    limit = mem_max if mem_max and mem_max != "max" else "unlimited"
                    if limit != "unlimited" and limit.isdigit():
                        limit_str = human_bytes(int(limit))
                    else:
                        limit_str = limit
                    print(f"    Memory: {human_bytes(current)} / {limit_str}")


def check_memory_limits():
    print("\n=== Memory Limits ===")
    out, rc = run_cmd("systemctl list-units --type=service --state=active --no-pager --no-legend 2>/dev/null | head -20")
    if rc == 0 and out:
        limited = []
        for line in out.split("\n"):
            parts = line.split()
            if parts:
                svc = parts[0]
                mem_out, _ = run_cmd(f"systemctl show {svc} -p MemoryMax 2>/dev/null")
                if mem_out:
                    val = mem_out.replace("MemoryMax=", "")
                    if val and val != "infinity" and val != "[not set]":
                        limited.append((svc, val))

        if limited:
            print(f"  Services with memory limits: {len(limited)}")
            for svc, limit in limited:
                print(f"    {svc:<40} Max={limit}")
        else:
            print("  No services with explicit memory limits")


def check_cpu_limits():
    print("\n=== CPU Limits ===")
    out, rc = run_cmd("systemctl list-units --type=service --state=active --no-pager --no-legend 2>/dev/null | head -20")
    if rc == 0 and out:
        limited = []
        for line in out.split("\n"):
            parts = line.split()
            if parts:
                svc = parts[0]
                cpu_out, _ = run_cmd(f"systemctl show {svc} -p CPUQuotaPerSecUSec 2>/dev/null")
                if cpu_out:
                    val = cpu_out.replace("CPUQuotaPerSecUSec=", "")
                    if val and val != "infinity" and val != "[not set]":
                        limited.append((svc, val))

        if limited:
            print(f"  Services with CPU limits: {len(limited)}")
            for svc, limit in limited:
                print(f"    {svc:<40} Quota={limit}")
        else:
            print("  No services with explicit CPU quotas")


def check_io_limits():
    print("\n=== I/O Limits ===")
    out, rc = run_cmd("systemctl list-units --type=service --state=active --no-pager --no-legend 2>/dev/null | head -15")
    if rc == 0 and out:
        limited = []
        for line in out.split("\n"):
            parts = line.split()
            if parts:
                svc = parts[0]
                io_out, _ = run_cmd(f"systemctl show {svc} -p IOReadBandwidthMax -p IOWriteBandwidthMax 2>/dev/null")
                if io_out and "[not set]" not in io_out and io_out.replace("IOReadBandwidthMax=", "").replace("IOWriteBandwidthMax=", "").strip():
                    limited.append(svc)

        if limited:
            print(f"  Services with I/O limits: {len(limited)}")
            for svc in limited:
                print(f"    {svc}")
        else:
            print("  No services with explicit I/O limits")


def main():
    parser = argparse.ArgumentParser(description="Cgroup v2 Resource Limit Auditor")
    parser.add_argument("--version", action="store_true", help="Check cgroup version")
    parser.add_argument("--slices", action="store_true", help="Show system slices")
    parser.add_argument("--memory", action="store_true", help="Show memory limits")
    parser.add_argument("--cpu", action="store_true", help="Show CPU limits")
    parser.add_argument("--io", action="store_true", help="Show I/O limits")
    args = parser.parse_args()

    print("Cgroup Resource Limit Auditor")
    print("=" * 40)

    if args.version:
        check_cgroup_version()
    elif args.slices:
        check_slices()
    elif args.memory:
        check_memory_limits()
    elif args.cpu:
        check_cpu_limits()
    elif args.io:
        check_io_limits()
    else:
        check_cgroup_version()
        check_slices()
        check_memory_limits()
        check_cpu_limits()

    print("\n" + "=" * 40)
    print("Powered by dargslan.com")


if __name__ == "__main__":
    main()
