"""CLI for dargslan-nfs-health — https://dargslan.com"""
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Dargslan NFS Health — NFS mount health checker",
        epilog="More tools at https://dargslan.com | eBooks: https://dargslan.com/books",
    )
    parser.add_argument("command", nargs="?", default="report",
                       choices=["report", "mounts", "exports", "stats", "throughput", "issues", "json"],
                       help="Command (default: report)")
    parser.add_argument("-m", "--mountpoint", help="Specific mountpoint for throughput test")
    args = parser.parse_args()

    from dargslan_nfs_health import NFSHealth
    nh = NFSHealth()
    import json

    if args.command == 'report': nh.print_report()
    elif args.command == 'mounts':
        for m in nh.check_all_mounts():
            status = 'OK' if m.get('accessible') else 'FAIL'
            print(f"  [{status}] {m.get('source','')} -> {m['mountpoint']}")
    elif args.command == 'exports':
        for e in nh.get_exports(): print(f"  {e['path']} -> {' '.join(e['clients'])}")
    elif args.command == 'stats': print(json.dumps(nh.get_nfs_stats(), indent=2))
    elif args.command == 'throughput':
        if args.mountpoint:
            r = nh.measure_throughput(args.mountpoint)
            print(f"  Write: {r.get('write_mbps',0)} MB/s, Read: {r.get('read_mbps',0)} MB/s")
        else:
            print("  Specify --mountpoint for throughput test")
    elif args.command == 'issues':
        for i in nh.audit(): print(f"  [{i['severity'].upper()}] {i['message']}")
    elif args.command == 'json': print(json.dumps(nh.audit(), indent=2))

if __name__ == "__main__": main()
