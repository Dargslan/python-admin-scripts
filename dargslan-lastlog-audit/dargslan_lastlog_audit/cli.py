#!/usr/bin/env python3
"""Last Login Audit and Reporting Tool."""

import subprocess
import os
import argparse


def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout.strip(), result.returncode
    except:
        return "", 1


def check_lastlog():
    print("=== Last Login Report ===")
    out, rc = run_cmd("lastlog 2>/dev/null | grep -v 'Never logged in'")
    if rc == 0 and out:
        lines = out.strip().split("\n")
        print(f"  Users who have logged in: {len(lines) - 1}")
        for line in lines:
            print(f"  {line}")
    else:
        print("  No login records found or lastlog not available")


def check_never_logged():
    print("\n=== Users Never Logged In ===")
    out, rc = run_cmd("lastlog 2>/dev/null | grep 'Never logged in'")
    if rc == 0 and out:
        lines = out.strip().split("\n")
        users = []
        for line in lines:
            user = line.split()[0] if line.split() else ""
            if user:
                users.append(user)
        print(f"  Users never logged in: {len(users)}")
        human_users = [u for u in users if not u.startswith("_")]
        if human_users:
            print(f"  Potential human accounts: {', '.join(human_users[:20])}")
    else:
        print("  All users have logged in at least once")


def check_recent_logins():
    print("\n=== Recent Login Activity ===")
    out, rc = run_cmd("last -n 20 2>/dev/null")
    if rc == 0 and out:
        for line in out.split("\n")[:20]:
            if line.strip():
                print(f"  {line}")
    else:
        print("  Login history not available")


def check_failed_logins():
    print("\n=== Failed Login Attempts ===")
    out, rc = run_cmd("lastb -n 20 2>/dev/null")
    if rc == 0 and out:
        lines = [l for l in out.strip().split("\n") if l.strip()]
        print(f"  Recent failed attempts: {len(lines)}")
        for line in lines[:15]:
            print(f"  {line}")
    else:
        out2, _ = run_cmd("grep 'Failed password' /var/log/auth.log 2>/dev/null | tail -10")
        if out2:
            for line in out2.split("\n"):
                print(f"  {line}")
        else:
            print("  No failed login data available (may need sudo)")


def check_login_shells():
    print("\n=== Users with Login Shells ===")
    out, rc = run_cmd("grep -v '/nologin\\|/false\\|/sync' /etc/passwd 2>/dev/null")
    if rc == 0 and out:
        lines = out.strip().split("\n")
        print(f"  Users with login shells: {len(lines)}")
        for line in lines:
            parts = line.split(":")
            if len(parts) >= 7:
                print(f"    {parts[0]:<20} UID={parts[2]:<6} Shell={parts[6]}")


def main():
    parser = argparse.ArgumentParser(description="Last Login Audit and Reporting Tool")
    parser.add_argument("--lastlog", action="store_true", help="Show lastlog report")
    parser.add_argument("--never", action="store_true", help="Show users never logged in")
    parser.add_argument("--recent", action="store_true", help="Show recent logins")
    parser.add_argument("--failed", action="store_true", help="Show failed login attempts")
    parser.add_argument("--shells", action="store_true", help="Show users with login shells")
    args = parser.parse_args()

    print("Last Login Audit Tool")
    print("=" * 40)

    if args.lastlog:
        check_lastlog()
    elif args.never:
        check_never_logged()
    elif args.recent:
        check_recent_logins()
    elif args.failed:
        check_failed_logins()
    elif args.shells:
        check_login_shells()
    else:
        check_lastlog()
        check_never_logged()
        check_recent_logins()
        check_failed_logins()
        check_login_shells()

    print("\n" + "=" * 40)
    print("Powered by dargslan.com")


if __name__ == "__main__":
    main()
