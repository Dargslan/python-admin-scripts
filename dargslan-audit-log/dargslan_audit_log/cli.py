#!/usr/bin/env python3
"""Audit log analyzer CLI - dargslan.com"""
import os, sys, glob

BANNER = """
=============================================
  Audit Log Analyzer - dargslan.com
  Part of dargslan-toolkit
=============================================
"""

def find_audit_logs():
    paths = ["/var/log/audit/audit.log", "/var/log/audit/audit.log.1"]
    found = []
    for p in paths:
        if os.path.exists(p):
            try:
                size = os.path.getsize(p)
                found.append((p, size))
            except:
                pass
    return found

def parse_audit_summary(path):
    stats = {"total": 0, "syscall": 0, "user_auth": 0, "user_login": 0, "avc": 0, "other": 0}
    try:
        with open(path, 'r') as f:
            for line in f:
                stats["total"] += 1
                if "type=SYSCALL" in line: stats["syscall"] += 1
                elif "type=USER_AUTH" in line: stats["user_auth"] += 1
                elif "type=USER_LOGIN" in line: stats["user_login"] += 1
                elif "type=AVC" in line: stats["avc"] += 1
                else: stats["other"] += 1
    except PermissionError:
        return None
    return stats

def report():
    print(BANNER)
    logs = find_audit_logs()
    if not logs:
        print("  No audit logs found at /var/log/audit/")
        print("  Install auditd: apt install auditd (Debian) or yum install audit (RHEL)")
        print("\n  Auditd commands:")
        print("    auditctl -l          List active audit rules")
        print("    ausearch -m USER_AUTH Recent auth events")
        print("    aureport --summary   Audit summary report")
    else:
        for path, size in logs:
            print(f"  Log: {path} ({size/1024:.0f} KB)")
            stats = parse_audit_summary(path)
            if stats:
                print(f"    Total entries:  {stats['total']}")
                print(f"    Syscall events: {stats['syscall']}")
                print(f"    User auth:      {stats['user_auth']}")
                print(f"    User login:     {stats['user_login']}")
                print(f"    SELinux AVC:    {stats['avc']}")
                print(f"    Other:          {stats['other']}")
            else:
                print("    (Permission denied - run as root)")
    print(f"\n  More security tools: https://dargslan.com")
    print(f"  210+ eBooks: https://dargslan.com/books\n")

def main():
    args = sys.argv[1:]
    cmd = args[0] if args else "report"
    if cmd in ("report", "auth", "files", "summary"):
        report()
    else:
        print(f"  Usage: dargslan-auditlog [report|auth|files|summary]")

if __name__ == "__main__":
    main()
