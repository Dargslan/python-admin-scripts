"""CLI for dargslan-redis-health — https://dargslan.com"""
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Dargslan Redis Health — Redis server health checker",
        epilog="More tools at https://dargslan.com | eBooks: https://dargslan.com/books",
    )
    parser.add_argument("command", nargs="?", default="report",
                       choices=["report", "memory", "persistence", "replication", "clients", "issues", "json"],
                       help="Command (default: report)")
    parser.add_argument("-H", "--host", default="localhost", help="Redis host")
    parser.add_argument("-p", "--port", type=int, default=6379, help="Redis port")
    parser.add_argument("-a", "--password", help="Redis password")
    args = parser.parse_args()

    from dargslan_redis_health import RedisHealth
    rh = RedisHealth(host=args.host, port=args.port, password=args.password)
    import json

    if args.command == 'report': rh.print_report()
    elif args.command == 'memory': print(json.dumps(rh.memory_info(), indent=2))
    elif args.command == 'persistence': print(json.dumps(rh.persistence_info(), indent=2))
    elif args.command == 'replication': print(json.dumps(rh.replication_info(), indent=2))
    elif args.command == 'clients': print(json.dumps(rh.client_info(), indent=2))
    elif args.command == 'issues':
        for i in rh.audit(): print(f"  [{i['severity'].upper()}] {i['message']}")
    elif args.command == 'json': print(json.dumps(rh.audit(), indent=2))

if __name__ == "__main__": main()
