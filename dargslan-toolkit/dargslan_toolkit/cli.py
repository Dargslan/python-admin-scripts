"""
Unified CLI for dargslan-toolkit — https://dargslan.com
"""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Dargslan Toolkit — Complete Linux Sysadmin Toolset",
        epilog="More tools and eBooks at https://dargslan.com",
    )
    sub = parser.add_subparsers(dest="tool")

    sub.add_parser("overview", help="Quick system overview")
    sub.add_parser("sysinfo", help="Full system information")
    sub.add_parser("firewall", help="Firewall audit")
    sub.add_parser("docker", help="Docker health check")

    logs_p = sub.add_parser("logs", help="Log parser")
    logs_p.add_argument("log_type", choices=["auth", "nginx", "syslog"])
    logs_p.add_argument("file", help="Path to log file")

    net_p = sub.add_parser("netscan", help="Network scanner")
    net_p.add_argument("action", choices=["quick", "ping"])
    net_p.add_argument("target", help="Host or subnet")

    sub.add_parser("version", help="Show version info")

    args = parser.parse_args()

    if args.tool == "overview":
        from dargslan_toolkit import Toolkit
        tk = Toolkit()
        tk.quick_overview()

    elif args.tool == "sysinfo":
        from dargslan_sysinfo import SystemInfo
        SystemInfo().print_report(["os", "cpu", "memory", "disk", "network", "processes"])

    elif args.tool == "firewall":
        from dargslan_firewall_audit import FirewallAudit
        FirewallAudit().print_audit()

    elif args.tool == "docker":
        from dargslan_docker_health import DockerHealth
        DockerHealth().print_status()

    elif args.tool == "logs":
        from dargslan_log_parser import LogParser
        LogParser().print_summary(args.file, args.log_type)

    elif args.tool == "netscan":
        from dargslan_net_scanner import NetScanner
        scanner = NetScanner()
        if args.action == "quick":
            scanner.print_scan(args.target)
        elif args.action == "ping":
            alive = scanner.ping_sweep(args.target)
            print(f"Alive hosts ({len(alive)}):")
            for h in alive:
                print(f"  {h}")

    elif args.tool == "version":
        from dargslan_toolkit import __version__
        print(f"dargslan-toolkit v{__version__}")
        print("https://dargslan.com")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
