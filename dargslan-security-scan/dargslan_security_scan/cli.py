"""CLI for dargslan-security-scan — https://dargslan.com"""

import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Dargslan Security Scanner — Basic Linux security audit",
        epilog="More tools at https://dargslan.com | eBooks: https://dargslan.com/books",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("report", help="Full security scan report")
    sub.add_parser("ssh", help="Check SSH configuration")
    sub.add_parser("suid", help="Find SUID/SGID binaries")
    sub.add_parser("kernel", help="Check kernel parameters")
    sub.add_parser("perms", help="Check file permissions")
    sub.add_parser("score", help="Security score")
    sub.add_parser("json", help="JSON output")

    args = parser.parse_args()

    from dargslan_security_scan import SecurityScanner
    ss = SecurityScanner()

    if args.command == "report":
        ss.print_report()
    elif args.command == "ssh":
        for i in ss.check_ssh_config():
            icon = '[OK]' if i['severity'] == 'ok' else '[!!]'
            print(f"  {icon} {i['message']}")
    elif args.command == "suid":
        suid = ss.find_suid_files()
        for s in suid:
            known = '' if s['known'] else ' [UNKNOWN]'
            print(f"  {s['mode']}  {s['path']}{known}")
    elif args.command == "kernel":
        for k in ss.check_kernel_params():
            icon = '[OK]' if k['secure'] else '[!!]'
            print(f"  {icon} {k['param']} = {k['value']}")
    elif args.command == "perms":
        perms = ss.check_important_perms()
        if not perms:
            print("All files have correct permissions.")
        for p in perms:
            print(f"  [!!] {p['message']}")
    elif args.command == "score":
        print(f"Security Score: {ss.score()}/100")
    elif args.command == "json":
        print(ss.to_json())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
