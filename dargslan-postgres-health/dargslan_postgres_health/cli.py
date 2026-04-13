"""CLI for dargslan-postgres-health — https://dargslan.com"""
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Dargslan PostgreSQL Health — PostgreSQL server health checker",
        epilog="More tools at https://dargslan.com | eBooks: https://dargslan.com/books",
    )
    parser.add_argument("command", nargs="?", default="report",
                       choices=["report", "connections", "databases", "bloat", "vacuum", "locks", "queries", "replication", "issues", "json"],
                       help="Command (default: report)")
    parser.add_argument("-H", "--host", default="localhost", help="PostgreSQL host")
    parser.add_argument("-p", "--port", type=int, default=5432, help="PostgreSQL port")
    parser.add_argument("-U", "--user", help="PostgreSQL user")
    parser.add_argument("-d", "--dbname", help="Database name")
    args = parser.parse_args()

    from dargslan_postgres_health import PostgresHealth
    ph = PostgresHealth(host=args.host, port=args.port, user=args.user, dbname=args.dbname)
    import json

    if args.command == 'report': ph.print_report()
    elif args.command == 'connections': print(json.dumps(ph.connection_status(), indent=2))
    elif args.command == 'databases':
        for db in ph.database_sizes(): print(f"  {db['database']:30s} {db['size_mb']:>10.1f} MB")
    elif args.command == 'bloat':
        for t in ph.table_bloat(): print(f"  {t['table']}: {t['dead_percent']}% dead ({t['dead_tuples']} tuples)")
    elif args.command == 'vacuum':
        for v in ph.vacuum_status(): print(f"  {v['table']}: vacuum={v['last_autovacuum']}")
    elif args.command == 'locks': print(f"  Waiting locks: {ph.active_locks()}")
    elif args.command == 'queries':
        for q in ph.long_running_queries(): print(f"  PID {q['pid']}: {q['duration']} - {q['query']}")
    elif args.command == 'replication': print(json.dumps(ph.replication_status(), indent=2))
    elif args.command == 'issues':
        for i in ph.audit(): print(f"  [{i['severity'].upper()}] {i['message']}")
    elif args.command == 'json': print(json.dumps(ph.audit(), indent=2))

if __name__ == "__main__": main()
