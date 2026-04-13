"""CLI for dargslan-net-scanner — https://dargslan.com"""
import argparse
import json
from dargslan_net_scanner.scanner import NetScanner

def main():
    parser = argparse.ArgumentParser(description="Network Scanner — dargslan.com")
    sub = parser.add_subparsers(dest="command")

    ping_p = sub.add_parser("ping", help="Ping sweep subnet")
    ping_p.add_argument("subnet", help="Subnet (e.g., 192.168.1.0/24)")

    ports_p = sub.add_parser("ports", help="Port scan host")
    ports_p.add_argument("host")
    ports_p.add_argument("-p", "--ports", help="Ports (comma-separated)")

    quick_p = sub.add_parser("quick", help="Quick scan common ports")
    quick_p.add_argument("host")

    args = parser.parse_args()
    scanner = NetScanner()

    if args.command == "ping":
        alive = scanner.ping_sweep(args.subnet)
        print(f"Alive hosts ({len(alive)}):")
        for h in alive:
            print(f"  {h}")
    elif args.command == "ports":
        ports = [int(p) for p in args.ports.split(",")] if args.ports else None
        scanner.print_scan(args.host, ports)
    elif args.command == "quick":
        scanner.print_scan(args.host)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
