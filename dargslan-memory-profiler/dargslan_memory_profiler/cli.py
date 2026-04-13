"""CLI for dargslan-memory-profiler — https://dargslan.com"""
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Dargslan Memory Profiler — Linux memory profiler",
        epilog="More tools at https://dargslan.com | eBooks: https://dargslan.com/books",
    )
    parser.add_argument("command", nargs="?", default="report",
                       choices=["report", "system", "top", "grouped", "shm", "issues", "json"],
                       help="Command (default: report)")
    parser.add_argument("-n", "--limit", type=int, default=20, help="Number of processes")
    args = parser.parse_args()

    from dargslan_memory_profiler import MemoryProfiler
    mp = MemoryProfiler()
    import json

    if args.command == 'report': mp.print_report()
    elif args.command == 'system':
        s = mp.get_system_memory()
        print(f"  Total: {s['total_human']} | Used: {s['used_human']} ({s['used_percent']}%) | Available: {s['available_human']}")
    elif args.command == 'top':
        for p in mp.get_all_processes(limit=args.limit):
            print(f"  {p.get('rss_human','N/A'):>10s}  PID {p['pid']:>6d}  {p.get('name','?')}")
    elif args.command == 'grouped':
        for g in mp.get_memory_by_name()[:args.limit]:
            print(f"  {g['total_rss_human']:>10s}  {g['name']:<25s} ({g['count']} procs)")
    elif args.command == 'shm':
        for s in mp.get_shared_memory():
            print(f"  shmid={s['shmid']} owner={s['owner']} size={s['size']} nattch={s['nattch']}")
    elif args.command == 'issues':
        for i in mp.audit(): print(f"  [{i['severity'].upper()}] {i['message']}")
    elif args.command == 'json': print(json.dumps(mp.get_system_memory(), indent=2))

if __name__ == "__main__": main()
