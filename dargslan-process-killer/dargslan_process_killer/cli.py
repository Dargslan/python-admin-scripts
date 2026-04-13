"""CLI for dargslan-process-killer."""

import sys
import json
from . import generate_report, get_zombies, get_resource_hogs, get_long_running, get_top_cpu, get_top_mem, audit, __version__


def print_report(data):
    print(f"Process Hunter Report")
    print(f"{'=' * 60}")
    print(f"Timestamp: {data['timestamp']}")
    print(f"Zombies: {data['zombie_count']}")
    print(f"Resource Hogs: {len(data['resource_hogs'])}")
    print()
    if data["top_cpu"]:
        print(f"Top CPU Consumers:")
        print(f"  {'PID':>7} {'CPU%':>6} {'MEM%':>6} {'RSS MB':>8} {'Command'}")
        for p in data["top_cpu"][:5]:
            print(f"  {p['pid']:>7} {p['cpu_percent']:>6} {p['mem_percent']:>6} {p['rss_mb']:>8} {p['command']}")
        print()
    if data["top_mem"]:
        print(f"Top Memory Consumers:")
        print(f"  {'PID':>7} {'MEM%':>6} {'RSS MB':>8} {'Command'}")
        for p in data["top_mem"][:5]:
            print(f"  {p['pid']:>7} {p['mem_percent']:>6} {p['rss_mb']:>8} {p['command']}")
        print()
    if data["zombies"]:
        print(f"Zombie Processes ({data['zombie_count']}):")
        for z in data["zombies"]:
            print(f"  PID {z['pid']} (parent: {z['ppid']}): {z['command']}")
        print()
    if data["long_running"]:
        print(f"Long-Running Processes:")
        for p in data["long_running"][:5]:
            print(f"  PID {p['pid']}: {p['elapsed_human']} — {p['command']}")
        print()
    if data["issues"]:
        print(f"Issues ({data['issues_count']}):")
        for i in data["issues"]:
            print(f"  [{i['severity'].upper()}] {i['message']}")
    else:
        print("No issues found.")
    print(f"\nMore Linux tools: https://dargslan.com/cheat-sheets")


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(f"dargslan-process-killer v{__version__}")
        print(f"Zombie and runaway process hunter")
        print(f"\nUsage: dargslan-prockill <command>")
        print(f"\nCommands:")
        print(f"  report     Full process analysis report")
        print(f"  zombies    Find zombie processes")
        print(f"  hogs       Find resource hog processes")
        print(f"  topcpu     Top CPU consumers")
        print(f"  topmem     Top memory consumers")
        print(f"  long       Long-running processes (>24h)")
        print(f"  audit      Issues only")
        print(f"  json       Full report as JSON")
        print(f"  version    Show version")
        print(f"\nhttps://dargslan.com — Linux & DevOps Books")
        return
    cmd = args[0]
    if cmd == "version":
        print(f"dargslan-process-killer v{__version__}")
    elif cmd == "report":
        print_report(generate_report())
    elif cmd == "zombies":
        z = get_zombies()
        print(f"Zombie processes: {len(z)}")
        for p in z: print(f"  PID {p['pid']}: {p['command']} (parent: {p['ppid']})")
    elif cmd == "hogs":
        h = get_resource_hogs()
        print(f"Resource hogs: {len(h)}")
        for p in h: print(f"  PID {p['pid']}: CPU={p['cpu_percent']}% MEM={p['mem_percent']}% {p['command'][:50]}")
    elif cmd == "topcpu":
        n = 10
        if "-n" in args:
            idx = args.index("-n")
            if idx+1 < len(args): n = int(args[idx+1])
        for p in get_top_cpu(n):
            print(f"  PID {p['pid']:>7} CPU={p['cpu_percent']:>5}% MEM={p['mem_percent']:>5}% {p['command']}")
    elif cmd == "topmem":
        n = 10
        if "-n" in args:
            idx = args.index("-n")
            if idx+1 < len(args): n = int(args[idx+1])
        for p in get_top_mem(n):
            print(f"  PID {p['pid']:>7} MEM={p['mem_percent']:>5}% RSS={p['rss_mb']:>6}MB {p['command']}")
    elif cmd == "long":
        hrs = 24
        if "-h" in args:
            idx = args.index("-h")
            if idx+1 < len(args): hrs = int(args[idx+1])
        procs = get_long_running(hrs)
        print(f"Processes running > {hrs}h: {len(procs)}")
        for p in procs: print(f"  PID {p['pid']}: {p['elapsed_human']} — {p['command']}")
    elif cmd == "audit":
        issues = audit()
        if not issues: print("No issues found.")
        for i in issues: print(f"[{i['severity'].upper()}] {i['message']}")
    elif cmd == "json":
        print(json.dumps(generate_report(), indent=2))
    else:
        print(f"Unknown command: {cmd}. Use --help."); sys.exit(1)

if __name__ == "__main__":
    main()
