"""CLI for dargslan-disk-cleaner — https://dargslan.com"""

import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Dargslan Disk Cleaner — Analyze disk usage & find large files",
        epilog="More tools at https://dargslan.com | eBooks: https://dargslan.com/books",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("report", help="Full disk usage report")
    sub.add_parser("usage", help="Filesystem usage summary")

    lg = sub.add_parser("large", help="Find large files")
    lg.add_argument("path", nargs="?", default="/", help="Path to scan")
    lg.add_argument("-m", "--min-size", type=int, default=100, help="Min size in MB")

    old = sub.add_parser("old", help="Find old files")
    old.add_argument("path", help="Path to scan")
    old.add_argument("-d", "--days", type=int, default=90, help="Days threshold")

    dr = sub.add_parser("dirs", help="Directory sizes")
    dr.add_argument("path", nargs="?", default="/", help="Path to scan")

    sub.add_parser("temp", help="Temp directory usage")
    sub.add_parser("json", help="JSON output")

    args = parser.parse_args()

    from dargslan_disk_cleaner import DiskCleaner, _human_size
    dc = DiskCleaner()

    if args.command == "report":
        dc.print_report()
    elif args.command == "usage":
        for du in dc.disk_usage():
            print(f"{du['mount']}: {du['used_human']}/{du['total_human']} ({du['percent_used']}%)")
    elif args.command == "large":
        files = dc.find_large_files(args.path, args.min_size)
        if not files:
            print(f"No files larger than {args.min_size}MB found.")
        for f in files:
            print(f"  {f['size_human']:>10}  {f['path']}")
    elif args.command == "old":
        files = dc.find_old_files(args.path, args.days)
        if not files:
            print(f"No files older than {args.days} days found.")
        for f in files:
            print(f"  {f['size_human']:>10}  {f['days_old']}d  {f['path']}")
    elif args.command == "dirs":
        for d in dc.dir_sizes(args.path):
            print(f"  {d['size_human']:>10}  {d['path']}")
    elif args.command == "temp":
        for t in dc.temp_usage():
            print(f"  {t['size_human']:>10}  {t['file_count']} files  {t['directory']}")
    elif args.command == "json":
        print(dc.to_json())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
