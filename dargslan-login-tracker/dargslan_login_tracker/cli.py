"""CLI for dargslan-login-tracker."""

import sys
import json
from . import generate_report, get_current_sessions, get_last_logins, get_failed_logins, detect_brute_force, audit, __version__


def print_report(data):
    print(f"Login Tracker Report")
    print(f"{'=' * 60}")
    print(f"Timestamp: {data['timestamp']}")
    print(f"Active Users: {data['active_users']}")
    print(f"SSH Connections: {data['ssh_connections']}")
    print(f"Failed Logins: {data['failed_logins']}")
    print()
    if data["current_sessions"]:
        print(f"Current Sessions:")
        for s in data["current_sessions"]:
            src = f" from {s['from']}" if s["from"] else ""
            print(f"  {s['user']:<12} {s['terminal']:<10} {s['login_time']}{src}")
        print()
    bf = data["brute_force_detection"]
    if bf["suspicious_ips"]:
        print(f"Suspicious IPs (brute force):")
        for ip, count in bf["suspicious_ips"].items():
            print(f"  {ip}: {count} failed attempts")
        print()
    if data["issues"]:
        print(f"Issues ({data['issues_count']}):")
        for i in data["issues"]:
            print(f"  [{i['severity'].upper()}] {i['message']}")
    else:
        print("No issues found.")
    print(f"\nMore Linux tools: https://dargslan.com/cheat-sheets")


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(f"dargslan-login-tracker v{__version__}")
        print(f"Linux login and SSH session tracker")
        print(f"\nUsage: dargslan-logins <command>")
        print(f"\nCommands:")
        print(f"  report     Full login tracker report")
        print(f"  active     Current active sessions")
        print(f"  last       Recent login history")
        print(f"  failed     Failed login attempts")
        print(f"  brute      Brute force detection")
        print(f"  audit      Issues only")
        print(f"  json       Full report as JSON")
        print(f"  version    Show version")
        print(f"\nhttps://dargslan.com — Linux & DevOps Books")
        return
    cmd = args[0]
    if cmd == "version":
        print(f"dargslan-login-tracker v{__version__}")
    elif cmd == "report":
        print_report(generate_report())
    elif cmd == "active":
        sessions = get_current_sessions()
        print(f"Active sessions: {len(sessions)}")
        for s in sessions:
            print(f"  {s['user']} on {s['terminal']} since {s['login_time']}")
    elif cmd == "last":
        n = 20
        if "-n" in args:
            idx = args.index("-n")
            if idx+1 < len(args): n = int(args[idx+1])
        for l in get_last_logins(n):
            print(f"  {l['raw']}")
    elif cmd == "failed":
        for f in get_failed_logins():
            print(f"  {f['raw']}")
    elif cmd == "brute":
        bf = detect_brute_force()
        print(f"Total failed: {bf['total_failed']}")
        if bf["suspicious_ips"]:
            print("Suspicious IPs:")
            for ip, c in bf["suspicious_ips"].items():
                print(f"  {ip}: {c} attempts")
        if bf["suspicious_users"]:
            print("Targeted users:")
            for u, c in bf["suspicious_users"].items():
                print(f"  {u}: {c} attempts")
    elif cmd == "audit":
        issues = audit()
        if not issues: print("No issues found.")
        for i in issues: print(f"[{i['severity'].upper()}] {i['message']}")
    elif cmd == "json":
        print(json.dumps(generate_report(), indent=2))
    else:
        print(f"Unknown command: {cmd}. Use --help."); sys.exit(1)

if __name__ == "__main__":
    main()
