"""CLI for dargslan-swap-analyzer — https://dargslan.com"""
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Dargslan Swap Analyzer — Linux swap usage analyzer",
        epilog="More tools at https://dargslan.com | eBooks: https://dargslan.com/books",
    )
    parser.add_argument("command", nargs="?", default="report",
                       choices=["report", "info", "processes", "devices", "pressure", "issues", "json"],
                       help="Command (default: report)")
    args = parser.parse_args()

    from dargslan_swap_analyzer import SwapAnalyzer
    sa = SwapAnalyzer()
    import json

    if args.command == 'report': sa.print_report()
    elif args.command == 'info':
        i = sa.get_swap_info()
        print(f"  Swap: {i.get('used_human','?')}/{i.get('total_human','?')} ({i.get('usage_percent',0)}%)")
    elif args.command == 'processes':
        for p in sa.get_process_swap()[:20]:
            print(f"  PID {p['pid']:6d} {p['name']:20s} {p['swap_human']}")
    elif args.command == 'devices':
        for d in sa.get_swap_devices():
            print(f"  {d['device']} ({d['type']}): {d['used_human']}/{d['size_human']}")
    elif args.command == 'pressure':
        print(json.dumps(sa.get_pressure(), indent=2))
    elif args.command == 'issues':
        for i in sa.audit(): print(f"  [{i['severity'].upper()}] {i['message']}")
    elif args.command == 'json': print(json.dumps(sa.audit(), indent=2))

if __name__ == "__main__": main()
