"""CLI for dargslan-systemd-analyze — https://dargslan.com"""
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Dargslan Systemd Analyze — Boot time analyzer",
        epilog="More tools at https://dargslan.com | eBooks: https://dargslan.com/books",
    )
    parser.add_argument("command", nargs="?", default="report",
                       choices=["report", "time", "blame", "chain", "slow", "timers", "issues", "json"],
                       help="Command (default: report)")
    parser.add_argument("-t", "--threshold", type=float, default=5.0, help="Slow unit threshold in seconds")
    args = parser.parse_args()

    from dargslan_systemd_analyze import SystemdAnalyze
    sa = SystemdAnalyze()
    import json

    if args.command == 'report': sa.print_report()
    elif args.command == 'time':
        bt = sa.get_boot_time()
        print(f"  {bt.get('summary', bt.get('raw', 'N/A'))}")
    elif args.command == 'blame':
        for u in sa.get_blame(): print(f"  {u['time_raw']:>8s} {u['name']}")
    elif args.command == 'chain': print(sa.get_critical_chain())
    elif args.command == 'slow':
        for u in sa.get_slow_units(args.threshold): print(f"  {u['time_raw']:>8s} {u['name']}")
    elif args.command == 'timers':
        for t in sa.get_calendar_timers(): print(f"  {t}")
    elif args.command == 'issues':
        for i in sa.audit(): print(f"  [{i['severity'].upper()}] {i['message']}")
    elif args.command == 'json': print(json.dumps(sa.audit(), indent=2))

if __name__ == "__main__": main()
