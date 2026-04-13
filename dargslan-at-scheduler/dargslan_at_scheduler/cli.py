#!/usr/bin/env python3
"""dargslan-at-scheduler — at/batch scheduler auditor CLI"""

import subprocess
import json
import argparse
import sys
import os


def run_cmd(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return r.stdout.strip()
    except Exception:
        return ""


def get_at_jobs():
    output = run_cmd("atq 2>/dev/null")
    if not output:
        return []
    jobs = []
    for line in output.strip().split("\n"):
        if line.strip():
            parts = line.split()
            jobs.append({
                "id": parts[0] if parts else "?",
                "raw": line.strip()
            })
    return jobs


def check_at_allow_deny():
    results = {}
    for f in ["/etc/at.allow", "/etc/at.deny"]:
        if os.path.exists(f):
            try:
                with open(f) as fh:
                    results[f] = fh.read().strip().split("\n")
            except PermissionError:
                results[f] = ["(permission denied)"]
        else:
            results[f] = ["(file not found)"]
    return results


def check_at_installed():
    return bool(run_cmd("which at 2>/dev/null") or run_cmd("which atd 2>/dev/null"))


def check_atd_running():
    output = run_cmd("systemctl is-active atd 2>/dev/null")
    if output == "active":
        return True
    output = run_cmd("pgrep -x atd 2>/dev/null")
    return bool(output)


def main():
    parser = argparse.ArgumentParser(
        description="at/batch scheduler auditor — dargslan.com",
        epilog="More tools: pip install dargslan-toolkit | https://dargslan.com"
    )
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    results = {
        "tool": "dargslan-at-scheduler",
        "version": "1.0.0",
        "at_installed": check_at_installed(),
        "atd_running": check_atd_running(),
        "pending_jobs": get_at_jobs(),
        "access_control": check_at_allow_deny()
    }

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print("=" * 60)
        print("  at/batch Scheduler Audit — dargslan.com")
        print("=" * 60)
        print(f"\n  at installed: {'Yes' if results['at_installed'] else 'No'}")
        print(f"  atd running:  {'Yes' if results['atd_running'] else 'No'}")
        print(f"  Pending jobs: {len(results['pending_jobs'])}")
        if results["pending_jobs"]:
            print("\n  Scheduled jobs:")
            for job in results["pending_jobs"]:
                print(f"    {job['raw']}")
        print("\n  Access control:")
        for f, contents in results["access_control"].items():
            print(f"    {f}: {', '.join(contents[:3])}")
        print("\n  More tools: pip install dargslan-toolkit")
        print("  eBooks: https://dargslan.com/books")

    return 0


if __name__ == "__main__":
    sys.exit(main())
