#!/usr/bin/env python3
"""Zombie Process Finder and Killer - Detect and clean zombie processes."""

import subprocess
import os
import signal
import argparse


def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout.strip(), result.returncode
    except:
        return "", 1


def find_zombies():
    print("=== Zombie Process Detection ===")
    out, rc = run_cmd("ps aux | awk '$8 ~ /Z/ {print}'")
    zombies = []
    if rc == 0 and out:
        lines = out.strip().split("\n")
        for line in lines:
            parts = line.split(None, 10)
            if len(parts) >= 11:
                zombies.append({
                    'user': parts[0],
                    'pid': parts[1],
                    'ppid': '',
                    'stat': parts[7],
                    'cmd': parts[10]
                })

    if zombies:
        for z in zombies:
            ppid_out, _ = run_cmd(f"ps -o ppid= -p {z['pid']} 2>/dev/null")
            z['ppid'] = ppid_out.strip()
            parent_out, _ = run_cmd(f"ps -o comm= -p {z['ppid']} 2>/dev/null")
            z['parent_cmd'] = parent_out.strip()

        print(f"  Found {len(zombies)} zombie process(es):\n")
        print(f"  {'PID':<8} {'PPID':<8} {'User':<12} {'Parent':<20} {'Command'}")
        print(f"  {'-'*8} {'-'*8} {'-'*12} {'-'*20} {'-'*20}")
        for z in zombies:
            print(f"  {z['pid']:<8} {z['ppid']:<8} {z['user']:<12} {z.get('parent_cmd','?'):<20} {z['cmd']}")
    else:
        print("  No zombie processes found. System is clean!")

    return zombies


def check_zombie_count():
    print("\n=== Zombie Statistics ===")
    out, rc = run_cmd("ps aux | awk '$8 ~ /Z/' | wc -l")
    count = int(out) if rc == 0 and out else 0

    total_out, _ = run_cmd("ps aux | wc -l")
    total = int(total_out) if total_out else 0

    print(f"  Zombie processes: {count}")
    print(f"  Total processes:  {total}")

    if count == 0:
        print("  Status: HEALTHY - No zombies")
    elif count < 5:
        print("  Status: OK - Few zombies, monitoring recommended")
    elif count < 20:
        print("  Status: WARNING - Multiple zombies detected")
    else:
        print("  Status: CRITICAL - Many zombie processes!")


def show_process_tree():
    print("\n=== Process Tree (zombies) ===")
    out, rc = run_cmd("ps axjf 2>/dev/null | head -50")
    if rc == 0 and out:
        for line in out.split("\n"):
            if "<defunct>" in line or "PPID" in line:
                print(f"  {line}")
    else:
        print("  Process tree not available")


def suggest_cleanup(zombies):
    if not zombies:
        return
    print("\n=== Cleanup Suggestions ===")
    ppids = set(z['ppid'] for z in zombies if z['ppid'])
    for ppid in ppids:
        parent_out, _ = run_cmd(f"ps -o comm= -p {ppid} 2>/dev/null")
        parent = parent_out.strip() or "unknown"
        zombie_count = sum(1 for z in zombies if z['ppid'] == ppid)
        print(f"  Parent PID {ppid} ({parent}) has {zombie_count} zombie(s)")
        print(f"    Option 1: kill -SIGCHLD {ppid}")
        print(f"    Option 2: kill {ppid}")
        print(f"    Option 3: kill -9 {ppid}")


def main():
    parser = argparse.ArgumentParser(description="Zombie Process Finder and Killer")
    parser.add_argument("--find", action="store_true", help="Find zombie processes")
    parser.add_argument("--tree", action="store_true", help="Show process tree")
    parser.add_argument("--stats", action="store_true", help="Show zombie statistics")
    parser.add_argument("--kill-parent", type=int, metavar="PID", help="Send SIGCHLD to parent PID")
    args = parser.parse_args()

    print("Zombie Process Finder")
    print("=" * 40)

    if args.kill_parent:
        print(f"  Sending SIGCHLD to PID {args.kill_parent}...")
        try:
            os.kill(args.kill_parent, signal.SIGCHLD)
            print(f"  Signal sent successfully.")
        except ProcessLookupError:
            print(f"  Process {args.kill_parent} not found")
        except PermissionError:
            print(f"  Permission denied. Try with sudo.")
    elif args.tree:
        show_process_tree()
    elif args.stats:
        check_zombie_count()
    else:
        zombies = find_zombies()
        check_zombie_count()
        show_process_tree()
        suggest_cleanup(zombies)

    print("\n" + "=" * 40)
    print("Powered by dargslan.com")


if __name__ == "__main__":
    main()
