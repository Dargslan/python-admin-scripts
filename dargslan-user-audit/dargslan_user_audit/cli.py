"""CLI for dargslan-user-audit — https://dargslan.com"""

import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Dargslan User Audit — Audit Linux user accounts",
        epilog="More tools at https://dargslan.com | eBooks: https://dargslan.com/books",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("report", help="Full user audit report")
    sub.add_parser("list", help="List login users")
    sub.add_parser("sudo", help="List sudo users")
    sub.add_parser("root", help="List root-level accounts")
    sub.add_parser("issues", help="Show security issues")
    sub.add_parser("json", help="JSON output")

    args = parser.parse_args()

    from dargslan_user_audit import UserAudit
    ua = UserAudit()

    if args.command == "report":
        ua.print_report()
    elif args.command == "list":
        for u in ua.get_login_users():
            print(f"  {u['username']:20s} UID:{u['uid']:>5}  {u['shell']}")
    elif args.command == "sudo":
        sudo = ua.check_sudo_users()
        if not sudo:
            print("No sudo users found.")
        for s in sudo:
            print(f"  {s}")
    elif args.command == "root":
        for r in ua.check_root_accounts():
            print(f"  {r['username']} (UID {r['uid']})")
    elif args.command == "issues":
        issues = ua.audit()
        if not issues:
            print("No issues found.")
        for i in issues:
            print(f"  [{i['severity'].upper():8s}] {i['message']}")
    elif args.command == "json":
        print(ua.to_json())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
