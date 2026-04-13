#!/usr/bin/env python3
"""Password Policy and Shadow File Auditor."""

import subprocess
import os
import argparse


def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout.strip(), result.returncode
    except:
        return "", 1


def check_password_policy():
    print("=== Password Policy ===")
    policies = {
        "PASS_MAX_DAYS": ("Max password age", "/etc/login.defs"),
        "PASS_MIN_DAYS": ("Min password age", "/etc/login.defs"),
        "PASS_MIN_LEN": ("Min password length", "/etc/login.defs"),
        "PASS_WARN_AGE": ("Password warning days", "/etc/login.defs"),
    }
    for key, (desc, f) in policies.items():
        out, rc = run_cmd(f"grep '^{key}' {f} 2>/dev/null")
        if rc == 0 and out:
            val = out.split()[-1] if out.split() else "?"
            print(f"  {desc}: {val}")
        else:
            print(f"  {desc}: not set")


def check_empty_passwords():
    print("\n=== Empty Password Check ===")
    out, rc = run_cmd("sudo awk -F: '$2 == \"\" {print $1}' /etc/shadow 2>/dev/null")
    if rc == 0 and out:
        users = out.strip().split("\n")
        print(f"  WARNING: {len(users)} user(s) with empty passwords!")
        for u in users:
            print(f"    - {u}")
    elif rc == 0:
        print("  No users with empty passwords")
    else:
        out2, _ = run_cmd("grep -c '::' /etc/passwd 2>/dev/null")
        if out2 and int(out2) > 0:
            print(f"  WARNING: Potential empty password entries in /etc/passwd")
        else:
            print("  Cannot check shadow file (need sudo)")


def check_password_aging():
    print("\n=== Password Aging Status ===")
    out, rc = run_cmd("cat /etc/passwd 2>/dev/null")
    if rc == 0 and out:
        human_users = []
        for line in out.split("\n"):
            parts = line.split(":")
            if len(parts) >= 7:
                uid = int(parts[2])
                shell = parts[6]
                if uid >= 1000 and "nologin" not in shell and "false" not in shell:
                    human_users.append(parts[0])

        for user in human_users[:15]:
            chage_out, chage_rc = run_cmd(f"chage -l {user} 2>/dev/null")
            if chage_rc == 0 and chage_out:
                print(f"\n  User: {user}")
                for line in chage_out.split("\n")[:4]:
                    print(f"    {line}")
            else:
                print(f"  {user}: aging info not available")


def check_locked_accounts():
    print("\n=== Locked Accounts ===")
    out, rc = run_cmd("sudo grep -E '^[^:]+:[!*]' /etc/shadow 2>/dev/null")
    if rc == 0 and out:
        lines = out.strip().split("\n")
        locked = [l.split(":")[0] for l in lines]
        print(f"  Locked/disabled accounts: {len(locked)}")
        human_locked = [u for u in locked if not u.startswith("_") and u not in ("nobody", "daemon", "bin", "sys")]
        if human_locked:
            print(f"  Notable locked: {', '.join(human_locked[:10])}")
    else:
        print("  Cannot check locked accounts (need sudo)")


def check_uid_gid():
    print("\n=== UID/GID Anomalies ===")
    out, rc = run_cmd("awk -F: '{print $3}' /etc/passwd 2>/dev/null | sort -n | uniq -d")
    if rc == 0 and out:
        print(f"  WARNING: Duplicate UIDs found: {out}")
    else:
        print("  No duplicate UIDs")

    out2, _ = run_cmd("awk -F: '$3==0 {print $1}' /etc/passwd 2>/dev/null")
    if out2:
        users = out2.strip().split("\n")
        if len(users) > 1:
            print(f"  WARNING: Multiple UID 0 accounts: {', '.join(users)}")
        else:
            print(f"  UID 0 accounts: {', '.join(users)} (expected)")


def main():
    parser = argparse.ArgumentParser(description="Password Policy and Shadow File Auditor")
    parser.add_argument("--policy", action="store_true", help="Check password policy")
    parser.add_argument("--empty", action="store_true", help="Check empty passwords")
    parser.add_argument("--aging", action="store_true", help="Check password aging")
    parser.add_argument("--locked", action="store_true", help="Check locked accounts")
    parser.add_argument("--uid", action="store_true", help="Check UID/GID anomalies")
    args = parser.parse_args()

    print("Password Policy Auditor")
    print("=" * 40)

    if args.policy:
        check_password_policy()
    elif args.empty:
        check_empty_passwords()
    elif args.aging:
        check_password_aging()
    elif args.locked:
        check_locked_accounts()
    elif args.uid:
        check_uid_gid()
    else:
        check_password_policy()
        check_empty_passwords()
        check_locked_accounts()
        check_uid_gid()

    print("\n" + "=" * 40)
    print("Powered by dargslan.com")


if __name__ == "__main__":
    main()
