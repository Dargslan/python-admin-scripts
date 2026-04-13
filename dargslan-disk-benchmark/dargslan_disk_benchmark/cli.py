"""CLI for dargslan-disk-benchmark — https://dargslan.com"""
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Dargslan Disk Benchmark — Linux disk I/O benchmark tool",
        epilog="More tools at https://dargslan.com | eBooks: https://dargslan.com/books",
    )
    parser.add_argument("command", nargs="?", default="report",
                       choices=["report", "write", "read", "iops", "latency", "info", "json"],
                       help="Command (default: report)")
    parser.add_argument("-p", "--path", default=None, help="Path to benchmark")
    parser.add_argument("-s", "--size", type=int, default=50, help="Test size in MB (default: 50)")
    args = parser.parse_args()

    from dargslan_disk_benchmark import DiskBenchmark
    db = DiskBenchmark(path=args.path)
    import json

    if args.command == 'report': db.print_report(size_mb=args.size)
    elif args.command == 'write':
        r = db.sequential_write(size_mb=args.size)
        print(f"  Sequential Write: {r['speed_human']} ({r['elapsed_sec']}s)")
    elif args.command == 'read':
        r = db.sequential_read(size_mb=args.size)
        print(f"  Sequential Read: {r['speed_human']} ({r['elapsed_sec']}s)")
    elif args.command == 'iops':
        rw = db.random_write_iops()
        rr = db.random_read_iops()
        print(f"  Random Write IOPS: {rw['iops']}")
        print(f"  Random Read IOPS:  {rr['iops']}")
    elif args.command == 'latency':
        r = db.latency_test()
        print(f"  Avg: {r['avg_ms']}ms | P50: {r['p50_ms']}ms | P95: {r['p95_ms']}ms | P99: {r['p99_ms']}ms")
    elif args.command == 'info':
        di = db.get_disk_info()
        print(f"  {di['path']}: {di.get('total_human','N/A')} total, {di.get('used_percent',0)}% used")
    elif args.command == 'json': print(json.dumps(db.full_benchmark(size_mb=args.size), indent=2))

if __name__ == "__main__": main()
