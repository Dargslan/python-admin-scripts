#!/usr/bin/env python3
"""Process Resource Monitor and Reporter."""

import subprocess
import os
import argparse


def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout.strip(), result.returncode
    except:
        return "", 1


def top_cpu():
    print("=== Top CPU Consumers ===")
    out, rc = run_cmd("ps aux --sort=-%cpu | head -16")
    if rc == 0 and out:
        for line in out.split("\n"):
            print(f"  {line}")


def top_memory():
    print("\n=== Top Memory Consumers ===")
    out, rc = run_cmd("ps aux --sort=-%mem | head -16")
    if rc == 0 and out:
        for line in out.split("\n"):
            print(f"  {line}")


def process_count():
    print("\n=== Process Statistics ===")
    out, rc = run_cmd("ps aux | wc -l")
    total = int(out) - 1 if rc == 0 and out else 0
    print(f"  Total processes: {total}")

    states = {"R": 0, "S": 0, "D": 0, "Z": 0, "T": 0}
    out2, _ = run_cmd("ps aux | awk 'NR>1 {print $8}'")
    if out2:
        for s in out2.split("\n"):
            key = s[0] if s else ""
            if key in states:
                states[key] += 1
    print(f"  Running: {states['R']}")
    print(f"  Sleeping: {states['S']}")
    print(f"  Disk wait: {states['D']}")
    print(f"  Zombie: {states['Z']}")
    print(f"  Stopped: {states['T']}")

    if states['Z'] > 0:
        print(f"  WARNING: {states['Z']} zombie processes detected!")
    if states['D'] > 5:
        print(f"  WARNING: {states['D']} processes in disk wait!")


def thread_count():
    print("\n=== Thread Statistics ===")
    out, rc = run_cmd("ps -eLf | wc -l")
    total = int(out) - 1 if rc == 0 and out else 0
    print(f"  Total threads: {total}")

    out2, _ = run_cmd("ps -eo nlwp,comm --sort=-nlwp | head -11")
    if out2:
        print(f"  Top thread creators:")
        for line in out2.split("\n"):
            print(f"    {line}")


def load_average():
    print("\n=== System Load ===")
    out, rc = run_cmd("uptime")
    if rc == 0 and out:
        print(f"  {out}")

    cpu_count, _ = run_cmd("nproc")
    if cpu_count:
        print(f"  CPU cores: {cpu_count}")
        loadavg, _ = run_cmd("cat /proc/loadavg")
        if loadavg:
            load1 = float(loadavg.split()[0])
            cores = int(cpu_count)
            ratio = load1 / cores
            status = "OVERLOADED" if ratio > 1.5 else "HIGH" if ratio > 1.0 else "NORMAL"
            print(f"  Load ratio: {ratio:.2f} [{status}]")


def main():
    parser = argparse.ArgumentParser(description="Process Resource Monitor")
    parser.add_argument("--cpu", action="store_true", help="Show top CPU consumers")
    parser.add_argument("--memory", action="store_true", help="Show top memory consumers")
    parser.add_argument("--count", action="store_true", help="Show process counts")
    parser.add_argument("--threads", action="store_true", help="Show thread statistics")
    parser.add_argument("--load", action="store_true", help="Show system load")
    args = parser.parse_args()

    print("Process Resource Monitor")
    print("=" * 40)

    if args.cpu:
        top_cpu()
    elif args.memory:
        top_memory()
    elif args.count:
        process_count()
    elif args.threads:
        thread_count()
    elif args.load:
        load_average()
    else:
        top_cpu()
        top_memory()
        process_count()
        load_average()

    print("\n" + "=" * 40)
    print("Powered by dargslan.com")


if __name__ == "__main__":
    main()
