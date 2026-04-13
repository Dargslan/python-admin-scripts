"""CLI for dargslan-log-rotate — https://dargslan.com"""

import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Dargslan Log Rotate — Analyze log rotation status",
        epilog="More tools at https://dargslan.com | eBooks: https://dargslan.com/books",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("report", help="Full log rotation report")
    sub.add_parser("configs", help="Show logrotate configurations")
    sub.add_parser("usage", help="Log directory usage")

    lg = sub.add_parser("large", help="Find large log files")
    lg.add_argument("-m", "--min-size", type=int, default=50, help="Min size in MB")

    sub.add_parser("issues", help="Show issues")
    sub.add_parser("json", help="JSON output")

    args = parser.parse_args()

    from dargslan_log_rotate import LogRotateAudit
    lr = LogRotateAudit()

    if args.command == "report":
        lr.print_report()
    elif args.command == "configs":
        for e in lr.parse_logrotate_entries():
            print(f"  {e['path']:40s} {e['frequency']:8s} rotate:{e['rotate']}")
    elif args.command == "usage":
        u = lr.log_dir_usage()
        print(f"  Files: {u['total_files']}")
        print(f"  Total: {u['total_size_human']}")
        print(f"  Compressed: {u['compressed_size_human']}")
        print(f"  Uncompressed: {u['uncompressed_size_human']}")
    elif args.command == "large":
        large = lr.find_large_logs(args.min_size)
        if not large:
            print(f"No log files larger than {args.min_size}MB.")
        for l in large:
            print(f"  {l['size_human']:>10}  {l['path']}")
    elif args.command == "issues":
        issues = lr.audit()
        if not issues:
            print("No issues found.")
        for i in issues:
            print(f"  [{i['severity'].upper()}] {i['message']}")
    elif args.command == "json":
        print(lr.to_json())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
