"""CLI for dargslan-service-monitor — https://dargslan.com"""

import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Dargslan Service Monitor — Monitor systemd services",
        epilog="More tools at https://dargslan.com | eBooks: https://dargslan.com/books",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("report", help="Full service report")
    sub.add_parser("failed", help="List failed services")
    sub.add_parser("running", help="List running services")
    sub.add_parser("enabled", help="List enabled services")

    st = sub.add_parser("status", help="Status of specific service")
    st.add_argument("name", help="Service name")

    chk = sub.add_parser("check", help="Check critical services")
    chk.add_argument("services", nargs="*", help="Services to check")

    sub.add_parser("json", help="JSON output")

    args = parser.parse_args()

    from dargslan_service_monitor import ServiceMonitor
    sm = ServiceMonitor()

    if args.command == "report":
        sm.print_report()
    elif args.command == "failed":
        failed = sm.get_failed()
        if not failed:
            print("No failed services.")
        for f in failed:
            print(f"  [FAILED] {f['name']:30s} {f['description']}")
    elif args.command == "running":
        for r in sm.get_running():
            print(f"  {r['name']:30s} {r['description'][:40]}")
    elif args.command == "enabled":
        for e in sm.get_enabled():
            print(f"  {e['name']}")
    elif args.command == "status":
        info = sm.service_status(args.name)
        for k, v in info.items():
            print(f"  {k:25s}: {v}")
    elif args.command == "check":
        svcs = args.services if args.services else None
        for r in sm.check_critical_services(svcs):
            icon = '[OK]' if r['running'] else '[DOWN]'
            print(f"  {icon:6s} {r['name']}")
    elif args.command == "json":
        print(sm.to_json())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
