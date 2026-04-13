"""CLI for dargslan-tcp-monitor — https://dargslan.com"""
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Dargslan TCP Monitor — TCP connection monitor",
        epilog="More tools at https://dargslan.com | eBooks: https://dargslan.com/books",
    )
    parser.add_argument("command", nargs="?", default="report",
                       choices=["report", "states", "listen", "established", "per-ip", "per-port", "timewait", "issues", "json"],
                       help="Command (default: report)")
    args = parser.parse_args()

    from dargslan_tcp_monitor import TCPMonitor
    tm = TCPMonitor()
    import json

    if args.command == 'report': tm.print_report()
    elif args.command == 'states':
        for s, c in sorted(tm.get_state_counts().items(), key=lambda x: -x[1]):
            print(f"  {s:15s} {c}")
    elif args.command == 'listen':
        for l in tm.get_listening_ports(): print(f"  {l['local_ip']}:{l['local_port']}")
    elif args.command == 'established':
        for c in tm.get_established()[:30]:
            print(f"  {c['local_ip']}:{c['local_port']} -> {c['remote_ip']}:{c['remote_port']}")
    elif args.command == 'per-ip':
        for e in tm.get_connections_per_ip()[:20]: print(f"  {e['ip']:>15s}  {e['count']}")
    elif args.command == 'per-port':
        for e in tm.get_connections_per_port()[:20]: print(f"  Port {e['port']:>5d}  {e['count']}")
    elif args.command == 'timewait': print(f"  TIME_WAIT connections: {tm.get_time_wait_count()}")
    elif args.command == 'issues':
        for i in tm.audit(): print(f"  [{i['severity'].upper()}] {i['message']}")
    elif args.command == 'json': print(json.dumps(tm.get_state_counts(), indent=2))

if __name__ == "__main__": main()
