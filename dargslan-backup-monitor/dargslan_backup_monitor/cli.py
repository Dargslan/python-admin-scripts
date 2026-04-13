"""CLI for dargslan-backup-monitor — https://dargslan.com"""

import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Dargslan Backup Monitor — Check backup status & freshness",
        epilog="More tools at https://dargslan.com | eBooks: https://dargslan.com/books",
    )
    sub = parser.add_subparsers(dest="command")

    rp = sub.add_parser("report", help="Full backup report")
    rp.add_argument("path", nargs="?", default=None, help="Backup directory")
    rp.add_argument("--max-age", type=int, default=24, help="Max age in hours")

    fr = sub.add_parser("check", help="Check backup freshness")
    fr.add_argument("path", nargs="?", default=None, help="Backup directory")
    fr.add_argument("--max-age", type=int, default=24, help="Max age in hours")

    ls = sub.add_parser("list", help="List backup files")
    ls.add_argument("path", nargs="?", default=None, help="Backup directory")

    cs = sub.add_parser("checksum", help="Verify backup checksum")
    cs.add_argument("file", help="Backup file path")
    cs.add_argument("-a", "--algorithm", default="sha256", help="Hash algorithm")

    sub.add_parser("json", help="JSON output")

    args = parser.parse_args()

    from dargslan_backup_monitor import BackupMonitor
    bm = BackupMonitor()

    if args.command == "report":
        bm.print_report(args.path, args.max_age)
    elif args.command == "check":
        result = bm.check_freshness(args.path, args.max_age)
        if result['total'] == 0:
            print("No backups found.")
        elif result['all_fresh']:
            print(f"[OK] All {result['total']} backups are fresh (< {args.max_age}h)")
        else:
            print(f"[WARNING] {len(result['stale'])} of {result['total']} backups are stale")
            for b in result['stale']:
                print(f"  STALE: {b['filename']} ({b['age_human']})")
    elif args.command == "list":
        backups = bm.find_backups(args.path)
        if not backups:
            print("No backup files found.")
        for b in backups:
            print(f"  {b['size_human']:>10}  {b['age_human']:>20}  {b['path']}")
    elif args.command == "checksum":
        result = bm.verify_checksum(args.file, args.algorithm)
        if 'error' in result:
            print(f"Error: {result['error']}")
        else:
            print(f"File: {result['file']}")
            print(f"Algorithm: {result['algorithm']}")
            print(f"Checksum: {result['checksum']}")
            print(f"Size: {result['size_human']}")
    elif args.command == "json":
        print(bm.to_json())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
