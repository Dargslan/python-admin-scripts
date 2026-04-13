#!/usr/bin/env python3
"""dargslan-apparmor-check — AppArmor profile status checker CLI"""

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


def check_apparmor_enabled():
    if os.path.exists("/sys/module/apparmor"):
        return True
    output = run_cmd("aa-enabled 2>/dev/null")
    return output.lower() == "yes"


def get_apparmor_status():
    output = run_cmd("aa-status 2>/dev/null")
    if not output:
        output = run_cmd("apparmor_status 2>/dev/null")
    if not output:
        return {}
    result = {"raw": output[:1000]}
    for line in output.split("\n"):
        line = line.strip()
        if "profiles are loaded" in line:
            result["profiles_loaded"] = line.split()[0]
        elif "profiles are in enforce mode" in line:
            result["enforce_mode"] = line.split()[0]
        elif "profiles are in complain mode" in line:
            result["complain_mode"] = line.split()[0]
        elif "processes have profiles defined" in line:
            result["processes_with_profiles"] = line.split()[0]
    return result


def get_profiles():
    profiles = []
    profile_dir = "/etc/apparmor.d"
    if os.path.isdir(profile_dir):
        try:
            for f in os.listdir(profile_dir):
                full = os.path.join(profile_dir, f)
                if os.path.isfile(full) and not f.startswith("."):
                    profiles.append(f)
        except PermissionError:
            profiles.append("(permission denied)")
    return sorted(profiles)[:30]


def check_violations():
    output = run_cmd("dmesg 2>/dev/null | grep -i apparmor | tail -5")
    if not output:
        output = run_cmd("journalctl -k --no-pager 2>/dev/null | grep -i apparmor | tail -5")
    if output:
        return output.strip().split("\n")
    return []


def main():
    parser = argparse.ArgumentParser(
        description="AppArmor profile status checker — dargslan.com",
        epilog="More tools: pip install dargslan-toolkit | https://dargslan.com"
    )
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    enabled = check_apparmor_enabled()
    status = get_apparmor_status() if enabled else {}
    results = {
        "tool": "dargslan-apparmor-check",
        "version": "1.0.0",
        "apparmor_enabled": enabled,
        "status": status,
        "profiles": get_profiles(),
        "recent_violations": check_violations()
    }

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print("=" * 60)
        print("  AppArmor Profile Status — dargslan.com")
        print("=" * 60)
        print(f"\n  AppArmor enabled: {'Yes' if enabled else 'No'}")
        if status:
            for k, v in status.items():
                if k != "raw":
                    print(f"  {k}: {v}")
        if results["profiles"]:
            print(f"\n  Profiles found: {len(results['profiles'])}")
            for p in results["profiles"][:10]:
                print(f"    - {p}")
        if results["recent_violations"]:
            print("\n  Recent violations:")
            for v in results["recent_violations"]:
                print(f"    {v[:80]}")
        print("\n  More tools: pip install dargslan-toolkit")
        print("  eBooks: https://dargslan.com/books")

    return 0


if __name__ == "__main__":
    sys.exit(main())
