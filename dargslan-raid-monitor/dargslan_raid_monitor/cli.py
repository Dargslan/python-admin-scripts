"""CLI for dargslan-raid-monitor."""

import sys
import json
from . import generate_report, get_arrays, get_rebuild_progress, audit, __version__


def print_report(data):
    print(f"RAID Array Health Report")
    print(f"{'=' * 60}")
    print(f"Timestamp: {data['timestamp']}")
    print(f"Total Arrays: {data['total_arrays']}")
    print()

    for arr in data["arrays"]:
        print(f"  Array: {arr['device']}")
        print(f"    State: {arr['state']}")
        print(f"    Level: {arr['level']}")
        print(f"    Devices:")
        for d in arr["devices"]:
            marker = " [FAULTY]" if d["status"] == "faulty" else ""
            marker = " [SPARE]" if d["status"] == "spare" else marker
            print(f"      - {d['device']}: {d['status']}{marker}")
        if "rebuild" in arr:
            rb = arr["rebuild"]
            print(f"    Rebuild: {rb['percentage']}% complete (ETA: {rb.get('eta', 'unknown')})")
        print()

    if data["issues"]:
        print(f"Issues Found: {data['issues_count']}")
        print(f"{'-' * 40}")
        for issue in data["issues"]:
            sev = issue["severity"].upper()
            print(f"  [{sev}] {issue['message']}")
    else:
        print("No issues found. All arrays healthy.")

    print(f"\nMore Linux tools: https://dargslan.com/cheat-sheets")


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(f"dargslan-raid-monitor v{__version__}")
        print(f"Linux RAID array health checker")
        print(f"\nUsage: dargslan-raid <command>")
        print(f"\nCommands:")
        print(f"  report    Full RAID health report")
        print(f"  arrays    List all RAID arrays")
        print(f"  rebuild   Show rebuild progress")
        print(f"  audit     Security audit (issues only)")
        print(f"  json      Full report as JSON")
        print(f"  version   Show version")
        print(f"\nhttps://dargslan.com — Linux & DevOps Books")
        return

    cmd = args[0]
    if cmd == "version":
        print(f"dargslan-raid-monitor v{__version__}")
    elif cmd == "report":
        print_report(generate_report())
    elif cmd == "arrays":
        arrays = get_arrays()
        if not arrays:
            print("No RAID arrays found in /proc/mdstat")
        for a in arrays:
            print(f"{a['name']}: {a['state']} ({a['level']}) — {len(a['devices'])} devices")
    elif cmd == "rebuild":
        progress = get_rebuild_progress()
        if not progress:
            print("No rebuilds in progress.")
        for dev, info in progress.items():
            print(f"{dev}: {info['percentage']}% (ETA: {info.get('eta', 'unknown')})")
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
