"""CLI for dargslan-kernel-check — https://dargslan.com"""
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Dargslan Kernel Check — Linux kernel parameter auditor",
        epilog="More tools at https://dargslan.com | eBooks: https://dargslan.com/books",
    )
    parser.add_argument("command", nargs="?", default="report",
                       choices=["report", "score", "params", "diffs", "issues", "json"],
                       help="Command (default: report)")
    args = parser.parse_args()

    from dargslan_kernel_check import KernelCheck
    kc = KernelCheck()
    import json

    if args.command == 'report': kc.print_report()
    elif args.command == 'score': print(f"  Kernel Hardening Score: {kc.get_score()}/100")
    elif args.command == 'params':
        for p in kc.check_all_params():
            icon = '[OK]' if p['compliant'] else '[!!]'
            print(f"  {icon} {p['param']}: {p['current']}")
    elif args.command == 'diffs':
        for d in kc.compare_live_vs_saved():
            print(f"  {d['param']}: live={d['live']}, saved={d['saved']}")
    elif args.command == 'issues':
        for i in kc.audit(): print(f"  [{i['severity'].upper()}] {i['param']}: {i['message']}")
    elif args.command == 'json': print(json.dumps(kc.audit(), indent=2))

if __name__ == "__main__": main()
