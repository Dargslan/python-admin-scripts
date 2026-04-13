"""
CLI for dargslan-log-parser — https://dargslan.com
"""

import argparse
import json

from dargslan_log_parser.parser import LogParser


def main():
    parser = argparse.ArgumentParser(
        description="Linux Log Parser — dargslan.com",
        epilog="More tools at https://dargslan.com",
    )
    sub = parser.add_subparsers(dest="command")

    auth_p = sub.add_parser("auth", help="Parse auth.log")
    auth_p.add_argument("file", help="Path to auth.log")
    auth_p.add_argument("--tail", type=int, help="Only last N lines")
    auth_p.add_argument("--json", action="store_true")

    nginx_p = sub.add_parser("nginx", help="Parse nginx access log")
    nginx_p.add_argument("file", help="Path to access.log")
    nginx_p.add_argument("--errors-only", action="store_true")
    nginx_p.add_argument("--json", action="store_true")

    search_p = sub.add_parser("search", help="Search log file")
    search_p.add_argument("file", help="Path to log file")
    search_p.add_argument("-p", "--pattern", required=True)
    search_p.add_argument("-i", "--ignore-case", action="store_true")
    search_p.add_argument("--tail", type=int)

    summary_p = sub.add_parser("summary", help="Summary report")
    summary_p.add_argument("file", help="Path to log file")
    summary_p.add_argument("--type", choices=["auth", "nginx", "syslog"], default="syslog")

    args = parser.parse_args()
    lp = LogParser()

    if args.command == "auth":
        entries = lp.parse_auth_log(args.file, args.tail)
        if args.json:
            print(json.dumps(entries, indent=2))
        else:
            lp.print_summary(args.file, "auth")
    elif args.command == "nginx":
        entries = lp.parse_nginx_access(args.file, args.tail)
        if args.errors_only:
            entries = [e for e in entries if e["status"] >= 400]
        if args.json:
            print(json.dumps(entries, indent=2))
        else:
            lp.print_summary(args.file, "nginx")
    elif args.command == "search":
        matches = lp.search(args.file, args.pattern, args.ignore_case, args.tail)
        for m in matches:
            print(f"  {m['line_number']:6d}: {m['content']}")
    elif args.command == "summary":
        lp.print_summary(args.file, args.type)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
