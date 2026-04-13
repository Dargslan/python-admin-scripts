"""CLI for dargslan-process-monitor — https://dargslan.com"""

import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Dargslan Process Monitor — Monitor Linux processes",
        epilog="More tools at https://dargslan.com | eBooks: https://dargslan.com/books",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("summary", help="Process summary")
    sub.add_parser("zombies", help="Find zombie processes")

    mem = sub.add_parser("topmem", help="Top memory consumers")
    mem.add_argument("-n", type=int, default=10, help="Number of results")

    cpu = sub.add_parser("topcpu", help="Top CPU consumers")
    cpu.add_argument("-n", type=int, default=10, help="Number of results")

    find = sub.add_parser("find", help="Find process by name")
    find.add_argument("name", help="Process name to search")

    sub.add_parser("count", help="Process count by state")
    sub.add_parser("json", help="JSON output")

    args = parser.parse_args()

    from dargslan_process_monitor import ProcessMonitor
    pm = ProcessMonitor()

    if args.command == "summary":
        pm.print_summary()
    elif args.command == "zombies":
        zombies = pm.find_zombies()
        if not zombies:
            print("No zombie processes found.")
        else:
            print(f"Found {len(zombies)} zombie process(es):")
            for z in zombies:
                print(f"  PID {z['pid']:>6}  PPID {z['ppid']:>6}  {z['name']}")
    elif args.command == "topmem":
        for p in pm.top_memory(args.n):
            print(f"  PID {p['pid']:>6}  {p['mem_human']:>10}  {p['name']}")
    elif args.command == "topcpu":
        for p in pm.top_cpu(args.n):
            print(f"  PID {p['pid']:>6}  {p['cpu_ticks']:>10} ticks  {p['name']}")
    elif args.command == "find":
        results = pm.find_by_name(args.name)
        if not results:
            print(f"No processes matching '{args.name}'")
        else:
            for p in results:
                print(f"  PID {p['pid']:>6}  {p['state_name']:>12}  {p['mem_human']:>10}  {p['name']}")
    elif args.command == "count":
        for state, count in sorted(pm.process_count().items()):
            print(f"  {state:20s}: {count}")
    elif args.command == "json":
        print(pm.to_json())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
