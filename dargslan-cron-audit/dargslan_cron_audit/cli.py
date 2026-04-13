"""CLI for dargslan-cron-audit — https://dargslan.com"""

import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Dargslan Cron Audit — Audit crontab entries",
        epilog="More tools at https://dargslan.com | eBooks: https://dargslan.com/books",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("report", help="Full cron audit report")
    sub.add_parser("list", help="List all cron entries")
    sub.add_parser("issues", help="Show issues only")
    sub.add_parser("json", help="JSON output")

    args = parser.parse_args()

    from dargslan_cron_audit import CronAudit
    ca = CronAudit()

    if args.command == "report":
        ca.print_report()
    elif args.command == "list":
        entries = ca.get_user_crontab() + ca.get_system_crontabs()
        if not entries:
            print("No crontab entries found.")
        for e in entries:
            print(f"  {e['schedule']:20s}  {e['command'][:60]}")
    elif args.command == "issues":
        issues = ca.audit()
        if not issues:
            print("No issues found.")
        for i in issues:
            print(f"  [{i['severity'].upper():8s}] {i['message']}")
    elif args.command == "json":
        print(ca.to_json())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
