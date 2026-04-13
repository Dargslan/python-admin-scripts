#!/usr/bin/env python3
"""Service Auto-Restart Monitor and Analyzer."""

import subprocess
import argparse
import re


def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout.strip(), result.returncode
    except:
        return "", 1


def check_failed_services():
    print("=== Failed Services ===")
    out, rc = run_cmd("systemctl --failed --no-pager 2>/dev/null")
    if rc == 0 and out:
        lines = out.strip().split("\n")
        failed = [l for l in lines if "failed" in l.lower() and "loaded" in l.lower()]
        if failed:
            print(f"  Failed services: {len(failed)}")
            for line in failed:
                print(f"    {line.strip()}")
        else:
            print("  No failed services")
    else:
        print("  Could not check systemd services")


def check_restart_counts():
    print("\n=== Service Restart History ===")
    out, rc = run_cmd("systemctl list-units --type=service --state=active --no-pager --no-legend 2>/dev/null")
    if rc == 0 and out:
        services = []
        for line in out.split("\n"):
            parts = line.split()
            if parts:
                svc = parts[0]
                restart_out, _ = run_cmd(f"systemctl show {svc} -p NRestarts 2>/dev/null")
                if restart_out:
                    match = re.search(r'NRestarts=(\d+)', restart_out)
                    if match and int(match.group(1)) > 0:
                        services.append((svc, int(match.group(1))))

        if services:
            services.sort(key=lambda x: x[1], reverse=True)
            print(f"  Services with restarts: {len(services)}")
            for svc, count in services[:15]:
                status = "WARNING" if count > 5 else "OK"
                print(f"    {svc:<40} restarts={count} [{status}]")
        else:
            print("  No services have been restarted")


def check_restart_policy():
    print("\n=== Restart Policies ===")
    out, rc = run_cmd("systemctl list-units --type=service --state=active --no-pager --no-legend 2>/dev/null | head -20")
    if rc == 0 and out:
        for line in out.split("\n"):
            parts = line.split()
            if parts:
                svc = parts[0]
                policy_out, _ = run_cmd(f"systemctl show {svc} -p Restart 2>/dev/null")
                if policy_out:
                    policy = policy_out.replace("Restart=", "")
                    if policy != "no":
                        print(f"    {svc:<40} Restart={policy}")


def check_watchdog():
    print("\n=== Watchdog Status ===")
    out, rc = run_cmd("systemctl list-units --type=service --state=active --no-pager --no-legend 2>/dev/null | head -20")
    if rc == 0 and out:
        watchdog_services = []
        for line in out.split("\n"):
            parts = line.split()
            if parts:
                svc = parts[0]
                wd_out, _ = run_cmd(f"systemctl show {svc} -p WatchdogUSec 2>/dev/null")
                if wd_out and "0" not in wd_out.replace("WatchdogUSec=", ""):
                    watchdog_services.append((svc, wd_out.replace("WatchdogUSec=", "")))

        if watchdog_services:
            print(f"  Services with watchdog: {len(watchdog_services)}")
            for svc, timeout in watchdog_services:
                print(f"    {svc}: timeout={timeout}")
        else:
            print("  No services with watchdog timers found")


def check_crash_logs():
    print("\n=== Recent Service Crashes ===")
    out, rc = run_cmd("journalctl --since '24 hours ago' -p err --no-pager -q 2>/dev/null | grep -i 'segfault\\|killed\\|crash\\|abort\\|core dump' | tail -10")
    if rc == 0 and out:
        print(f"  Recent crash-related entries:")
        for line in out.split("\n"):
            print(f"    {line}")
    else:
        print("  No recent crash logs found")


def main():
    parser = argparse.ArgumentParser(description="Service Auto-Restart Monitor")
    parser.add_argument("--failed", action="store_true", help="Show failed services")
    parser.add_argument("--restarts", action="store_true", help="Show restart counts")
    parser.add_argument("--policy", action="store_true", help="Show restart policies")
    parser.add_argument("--watchdog", action="store_true", help="Show watchdog status")
    parser.add_argument("--crashes", action="store_true", help="Show recent crashes")
    args = parser.parse_args()

    print("Service Restart Monitor")
    print("=" * 40)

    if args.failed:
        check_failed_services()
    elif args.restarts:
        check_restart_counts()
    elif args.policy:
        check_restart_policy()
    elif args.watchdog:
        check_watchdog()
    elif args.crashes:
        check_crash_logs()
    else:
        check_failed_services()
        check_restart_counts()
        check_restart_policy()
        check_crash_logs()

    print("\n" + "=" * 40)
    print("Powered by dargslan.com")


if __name__ == "__main__":
    main()
