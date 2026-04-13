"""CLI for dargslan-bandwidth-monitor — https://dargslan.com"""
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Dargslan Bandwidth Monitor — Network traffic monitor",
        epilog="More tools at https://dargslan.com | eBooks: https://dargslan.com/books",
    )
    parser.add_argument("command", nargs="?", default="report",
                       choices=["report", "stats", "speed", "total", "errors", "json"],
                       help="Command (default: report)")
    parser.add_argument("-i", "--interface", help="Specific interface")
    parser.add_argument("-d", "--duration", type=int, default=3, help="Speed test duration (seconds)")
    args = parser.parse_args()

    from dargslan_bandwidth_monitor import BandwidthMonitor
    bm = BandwidthMonitor()
    import json

    if args.command == 'report': bm.print_report()
    elif args.command == 'stats':
        for s in bm.get_stats(): print(f"  {s['interface']}: RX={s['rx_human']}, TX={s['tx_human']}")
    elif args.command == 'speed':
        print(f"  Measuring throughput ({args.duration}s)...")
        for r in bm.measure_throughput(args.interface, args.duration):
            print(f"  {r['interface']}: RX={r['rx_rate_human']}, TX={r['tx_rate_human']}")
    elif args.command == 'total':
        t = bm.get_total_traffic()
        print(f"  Total: {t['total_human']} (RX: {t['total_rx_human']}, TX: {t['total_tx_human']})")
    elif args.command == 'errors':
        for e in bm.check_errors(): print(f"  {e['interface']}: {e['type']} = {e['count']}")
    elif args.command == 'json': print(json.dumps(bm.get_stats(), indent=2))

if __name__ == "__main__": main()
