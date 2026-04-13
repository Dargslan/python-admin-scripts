"""CLI for dargslan-mysql-health — https://dargslan.com"""

import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Dargslan MySQL Health — Monitor MySQL/MariaDB server health",
        epilog="More tools at https://dargslan.com | eBooks: https://dargslan.com/books",
    )
    parser.add_argument("command", nargs="?", default="report",
                       choices=["report", "connections", "slow", "databases", "replication", "issues", "json"],
                       help="Command (default: report)")
    parser.add_argument("-H", "--host", default="localhost", help="MySQL host")
    parser.add_argument("-P", "--port", type=int, default=3306, help="MySQL port")
    parser.add_argument("-u", "--user", help="MySQL user")
    parser.add_argument("-p", "--password", help="MySQL password")
    args = parser.parse_args()

    from dargslan_mysql_health import MySQLHealth
    mh = MySQLHealth(host=args.host, port=args.port, user=args.user, password=args.password)

    import json

    if args.command == 'report':
        mh.print_report()
    elif args.command == 'connections':
        c = mh.connection_status()
        print(json.dumps(c, indent=2))
    elif args.command == 'slow':
        s = mh.slow_queries()
        print(json.dumps(s, indent=2))
    elif args.command == 'databases':
        for db in mh.database_sizes():
            print(f"  {db['database']:30s} {db['size_mb']:>10.2f} MB")
    elif args.command == 'replication':
        r = mh.replication_status()
        print(json.dumps(r, indent=2))
    elif args.command == 'issues':
        for i in mh.audit():
            print(f"  [{i['severity'].upper()}] {i['message']}")
    elif args.command == 'json':
        print(json.dumps(mh.audit(), indent=2))


if __name__ == "__main__":
    main()
