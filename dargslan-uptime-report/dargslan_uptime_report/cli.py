"""CLI for dargslan-uptime-report."""

import sys
import json
from . import generate_report, get_uptime, get_reboot_history, get_crash_events, get_load_average, audit, __version__


def print_report(data):
    print(f"System Uptime & Availability Report")
    print(f"{'=' * 60}")
    print(f"Timestamp: {data['timestamp']}")
    print()

    u = data["uptime"]
    print(f"Current Uptime: {u['human']}")
    print(f"Boot Time: {u['boot_time']}")
    print(f"30-Day Availability: {data['availability_30d']}%")
    print()

    la = data["load_average"]
    cpus = data["cpu_count"]
    print(f"Load Average: {la['1min']} / {la['5min']} / {la['15min']} (CPUs: {cpus})")
    print()

    ci = data["crash_info"]
    print(f"Boot History:")
    print(f"  Total Boots: {ci['total_boots']}")
    print(f"  Kernel Panics: {ci['kernel_panics']}")
    print(f"  OOM Kills: {ci['oom_kills']}")
    print()

    if data["reboots"]:
        print(f"Recent Reboots ({data['reboot_count']}):")
        print(f"{'-' * 40}")
        for r in data["reboots"][:10]:
            print(f"  {r['date']}  kernel={r['kernel']}")
        print()

    if data["issues"]:
        print(f"Issues Found: {data['issues_count']}")
        for issue in data["issues"]:
            print(f"  [{issue['severity'].upper()}] {issue['message']}")
    else:
        print("No issues found. System is stable.")

    print(f"\nMore Linux tools: https://dargslan.com/cheat-sheets")


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(f"dargslan-uptime-report v{__version__}")
        print(f"System uptime and availability reporter")
        print(f"\nUsage: dargslan-uptime <command>")
        print(f"\nCommands:")
        print(f"  report    Full uptime & availability report")
        print(f"  uptime    Current uptime only")
        print(f"  reboots   Reboot history")
        print(f"  crashes   Crash event analysis")
        print(f"  load      Current load average")
        print(f"  audit     Security audit (issues only)")
        print(f"  json      Full report as JSON")
        print(f"  version   Show version")
        print(f"\nhttps://dargslan.com — Linux & DevOps Books")
        return

    cmd = args[0]
    if cmd == "version":
        print(f"dargslan-uptime-report v{__version__}")
    elif cmd == "report":
        print_report(generate_report())
    elif cmd == "uptime":
        u = get_uptime()
        print(f"Uptime: {u['human']}")
        print(f"Boot time: {u['boot_time']}")
    elif cmd == "reboots":
        reboots = get_reboot_history()
        print(f"Reboots: {len(reboots)}")
        for r in reboots:
            print(f"  {r['date']}  kernel={r['kernel']}")
    elif cmd == "crashes":
        crashes = get_crash_events()
        print(f"Total boots: {crashes['total_boots']}")
        print(f"Kernel panics: {crashes['kernel_panics']}")
        print(f"OOM kills: {crashes['oom_kills']}")
    elif cmd == "load":
        la = get_load_average()
        print(f"1min: {la['1min']}  5min: {la['5min']}  15min: {la['15min']}")
    elif cmd == "audit":
        issues = audit()
        if not issues:
            print("No issues found.")
        for i in issues:
            print(f"[{i['severity'].upper()}] {i['message']}")
    elif cmd == "json":
        print(json.dumps(generate_report(), indent=2))
    else:
        print(f"Unknown command: {cmd}. Use --help for usage.")
        sys.exit(1)


if __name__ == "__main__":
    main()
