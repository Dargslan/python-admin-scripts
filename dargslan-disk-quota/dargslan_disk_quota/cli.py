"""CLI for dargslan-disk-quota."""

import sys
import json
from . import generate_report, get_user_quotas, get_group_quotas, get_filesystem_usage, audit, __version__


def print_report(data):
    print(f"Disk Quota Report")
    print(f"{'=' * 60}")
    print(f"Timestamp: {data['timestamp']}")
    print(f"Quotas Enabled: {'Yes' if data['quota_enabled'] else 'No'}")
    print()
    if data["user_quotas"]:
        print(f"User Quotas ({len(data['user_quotas'])}):")
        print(f"{'User':<15} {'Used MB':>10} {'Soft MB':>10} {'Hard MB':>10} {'Status':>10}")
        for q in data["user_quotas"]:
            status = "OVER!" if q["over_hard"] else ("warn" if q["over_soft"] else "ok")
            soft = round(q["soft_limit_kb"] / 1024, 1) if q["soft_limit_kb"] else "-"
            hard = round(q["hard_limit_kb"] / 1024, 1) if q["hard_limit_kb"] else "-"
            print(f"  {q['user']:<13} {q['used_mb']:>10} {soft:>10} {hard:>10} {status:>10}")
        print()
    if data["filesystems"]:
        print(f"Filesystem Usage:")
        for fs in data["filesystems"]:
            bar = "#" * (fs["use_percent"] // 5) + "." * (20 - fs["use_percent"] // 5)
            print(f"  {fs['mount']:<20} [{bar}] {fs['use_percent']}% ({fs['used']}/{fs['size']})")
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
        print(f"dargslan-disk-quota v{__version__}")
        print(f"Linux disk quota monitor")
        print(f"\nUsage: dargslan-quota <command>")
        print(f"\nCommands:")
        print(f"  report    Full quota and filesystem report")
        print(f"  users     User quota listing")
        print(f"  groups    Group quota listing")
        print(f"  disk      Filesystem usage")
        print(f"  audit     Issues only")
        print(f"  json      Full report as JSON")
        print(f"  version   Show version")
        print(f"\nhttps://dargslan.com — Linux & DevOps Books")
        return
    cmd = args[0]
    if cmd == "version":
        print(f"dargslan-disk-quota v{__version__}")
    elif cmd == "report":
        print_report(generate_report())
    elif cmd == "users":
        uq = get_user_quotas()
        if not uq: print("No user quotas found.")
        for q in uq:
            print(f"{q['user']}: {q['used_mb']}MB used")
    elif cmd == "groups":
        gq = get_group_quotas()
        if not gq: print("No group quotas found.")
        for q in gq:
            print(f"{q['group']}: {q['used_mb']}MB used")
    elif cmd == "disk":
        for fs in get_filesystem_usage():
            print(f"{fs['mount']}: {fs['use_percent']}% ({fs['used']}/{fs['size']})")
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
