"""CLI interface for dargslan-log-stats."""

import sys
from dargslan_log_stats import generate_report, get_largest_logs, get_log_disk_usage, get_unrotated_logs, check_rotation_status


def main():
    args = sys.argv[1:]
    cmd = args[0] if args else "report"

    if cmd == "report":
        print(generate_report())
    elif cmd == "largest":
        count = int(args[1]) if len(args) > 1 else 10
        for l in get_largest_logs(count=count):
            print(f"  {l['size_human']:>10s}  {l['modified']}  {l['path']}")
    elif cmd == "usage":
        u = get_log_disk_usage()
        print(f"Total: {u['total_human']} ({u['file_count']} files)")
    elif cmd == "unrotated":
        logs = get_unrotated_logs()
        if logs:
            for l in logs:
                print(f"  [WARNING] {l['path']} ({l['size_human']})")
        else:
            print("No unrotated large log files found.")
    elif cmd == "rotation":
        r = check_rotation_status()
        print(f"Configured: {'Yes' if r['configured'] else 'No'}")
        if r['last_run']:
            print(f"Last run: {r['last_run']}")
    elif cmd in ("help", "--help", "-h"):
        print("dargslan-logstats — Linux log file statistics")
        print("Usage: dargslan-logstats [command]")
        print("Commands: report, largest [n], usage, unrotated, rotation")
        print("More: https://dargslan.com")
    else:
        print(f"Unknown command: {cmd}. Use --help for usage.")
        sys.exit(1)


if __name__ == "__main__":
    main()
