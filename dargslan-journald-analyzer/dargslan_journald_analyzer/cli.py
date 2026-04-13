"""CLI for dargslan-journald-analyzer — https://dargslan.com"""
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Dargslan Journald Analyzer — Systemd journal log analyzer",
        epilog="More tools at https://dargslan.com | eBooks: https://dargslan.com/books",
    )
    parser.add_argument("command", nargs="?", default="report",
                       choices=["report", "errors", "failures", "kernel", "security", "oom", "boots", "disk", "issues", "json"],
                       help="Command (default: report)")
    parser.add_argument("-b", "--boot", type=int, default=0, help="Boot offset (0=current)")
    args = parser.parse_args()

    from dargslan_journald_analyzer import JournaldAnalyzer
    ja = JournaldAnalyzer()
    import json

    if args.command == 'report': ja.print_report()
    elif args.command == 'errors':
        for e in ja.get_boot_errors(args.boot): print(f"  {e[:120]}")
    elif args.command == 'failures':
        for f in ja.get_failed_units(): print(f"  [!!] {f['unit']}")
    elif args.command == 'kernel':
        for w in ja.get_kernel_warnings(args.boot): print(f"  {w[:120]}")
    elif args.command == 'security':
        for s in ja.get_security_events(): print(f"  [{s['type']}] {s['line'][:100]}")
    elif args.command == 'oom':
        for o in ja.get_oom_kills(args.boot): print(f"  {o}")
    elif args.command == 'boots':
        for b in ja.get_boot_list(): print(f"  {b}")
    elif args.command == 'disk': print(f"  {ja.get_disk_usage()}")
    elif args.command == 'issues':
        for i in ja.audit(): print(f"  [{i['severity'].upper()}] {i['message']}")
    elif args.command == 'json': print(json.dumps(ja.audit(), indent=2))

if __name__ == "__main__": main()
