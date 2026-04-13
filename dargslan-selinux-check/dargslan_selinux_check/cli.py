"""CLI interface for dargslan-selinux-check."""

import sys
from dargslan_selinux_check import generate_report, get_selinux_status, get_booleans, get_recent_denials, check_security_score


def main():
    args = sys.argv[1:]
    cmd = args[0] if args else "report"

    if cmd == "report":
        print(generate_report())
    elif cmd == "status":
        s = get_selinux_status()
        print(f"Installed: {'Yes' if s['installed'] else 'No'}")
        print(f"Mode: {s['mode']}")
        print(f"Policy: {s['policy']}")
    elif cmd == "booleans":
        bools = get_booleans()
        if bools:
            for b in bools:
                print(f"  {b['name']:40s} = {b['value']}")
        else:
            print("No SELinux booleans found (SELinux may not be installed).")
    elif cmd == "denials":
        denials = get_recent_denials()
        if denials:
            for d in denials:
                print(f"  {d}")
        else:
            print("No recent SELinux denials found.")
    elif cmd == "score":
        s = check_security_score()
        print(f"SELinux Security Score: {s['score']}/{s['max']}")
        for issue in s['issues']:
            print(f"  [!] {issue}")
    elif cmd in ("help", "--help", "-h"):
        print("dargslan-selinux — SELinux status checker")
        print("Usage: dargslan-selinux [command]")
        print("Commands: report, status, booleans, denials, score")
        print("More: https://dargslan.com")
    else:
        print(f"Unknown command: {cmd}. Use --help for usage.")
        sys.exit(1)


if __name__ == "__main__":
    main()
