"""CLI for dargslan-port-monitor — https://dargslan.com"""

import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Dargslan Port Monitor — Monitor open ports & listening services",
        epilog="More tools at https://dargslan.com | eBooks: https://dargslan.com/books",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("report", help="Full port report")
    sub.add_parser("tcp", help="List TCP listening ports")
    sub.add_parser("udp", help="List UDP listening ports")
    sub.add_parser("exposed", help="Show externally exposed ports")

    chk = sub.add_parser("check", help="Check if port is open")
    chk.add_argument("host", help="Host to check")
    chk.add_argument("port", type=int, help="Port to check")

    sub.add_parser("json", help="JSON output")

    args = parser.parse_args()

    from dargslan_port_monitor import PortMonitor
    pm = PortMonitor()

    if args.command == "report":
        pm.print_report()
    elif args.command == "tcp":
        for p in sorted(pm.get_listening_ports(), key=lambda x: x['port']):
            svc = f" ({p['service']})" if p['service'] else ''
            print(f"  {p['address']:>15}:{p['port']:<6}{svc}")
    elif args.command == "udp":
        for p in pm.get_udp_ports():
            print(f"  {p['address']:>15}:{p['port']:<6}")
    elif args.command == "exposed":
        exposed = pm.find_exposed()
        if not exposed:
            print("No externally exposed ports.")
        for p in exposed:
            svc = f" ({p['service']})" if p['service'] else ''
            print(f"  [EXPOSED] :{p['port']}{svc}")
    elif args.command == "check":
        r = pm.check_port(args.host, args.port)
        status = "OPEN" if r['open'] else "CLOSED"
        print(f"  {args.host}:{args.port} — {status}")
    elif args.command == "json":
        print(pm.to_json())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
