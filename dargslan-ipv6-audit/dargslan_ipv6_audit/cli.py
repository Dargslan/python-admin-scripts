#!/usr/bin/env python3
"""IPv6 configuration and security auditor."""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def get_ipv6_info():
    interfaces = []
    net_dir = Path("/sys/class/net")
    if not net_dir.exists():
        return interfaces

    for iface in sorted(net_dir.iterdir()):
        name = iface.name
        if name == "lo":
            continue
        info = {"interface": name, "ipv6_enabled": True, "addresses": [], "privacy": None,
                "accept_ra": None, "forwarding": None, "autoconf": None}

        conf_dir = Path(f"/proc/sys/net/ipv6/conf/{name}")
        for param in ["disable_ipv6", "accept_ra", "forwarding", "autoconf",
                      "use_tempaddr", "accept_redirects", "accept_source_route"]:
            try:
                val = (conf_dir / param).read_text().strip()
                if param == "disable_ipv6":
                    info["ipv6_enabled"] = val == "0"
                elif param == "use_tempaddr":
                    info["privacy"] = "enabled" if val in ("1", "2") else "disabled"
                else:
                    info[param] = val
            except (FileNotFoundError, PermissionError):
                pass

        try:
            result = subprocess.run(["ip", "-6", "addr", "show", name],
                                    capture_output=True, text=True, timeout=5)
            for line in result.stdout.splitlines():
                line = line.strip()
                if line.startswith("inet6"):
                    parts = line.split()
                    if len(parts) >= 2:
                        info["addresses"].append(parts[1])
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        interfaces.append(info)
    return interfaces


def check_security(interfaces):
    issues = []
    for iface in interfaces:
        if iface.get("accept_redirects") == "1":
            issues.append(f"{iface['interface']}: accepts ICMPv6 redirects (potential MITM)")
        if iface.get("accept_source_route") == "1":
            issues.append(f"{iface['interface']}: accepts source routing (security risk)")
        if iface.get("privacy") == "disabled" and iface["ipv6_enabled"]:
            issues.append(f"{iface['interface']}: IPv6 privacy extensions disabled")
    return issues


def main():
    parser = argparse.ArgumentParser(
        description="IPv6 configuration and security auditor",
        epilog="More tools: https://dargslan.com | pip install dargslan-toolkit"
    )
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--security", action="store_true", help="Security audit only")
    args = parser.parse_args()

    interfaces = get_ipv6_info()
    issues = check_security(interfaces)

    if args.json:
        print(json.dumps({"interfaces": interfaces, "security_issues": issues}, indent=2))
        return

    print("\033[1m  Dargslan IPv6 Audit\033[0m\n")

    if args.security:
        if issues:
            for i in issues:
                print(f"  \033[33m! {i}\033[0m")
        else:
            print("  \033[32mNo IPv6 security issues found.\033[0m")
    else:
        for iface in interfaces:
            status = "\033[32mON\033[0m" if iface["ipv6_enabled"] else "\033[31mOFF\033[0m"
            print(f"  \033[1m{iface['interface']}\033[0m: IPv6 {status} | "
                  f"Privacy: {iface.get('privacy', 'N/A')} | "
                  f"RA: {iface.get('accept_ra', 'N/A')} | "
                  f"Fwd: {iface.get('forwarding', 'N/A')} | "
                  f"Addrs: {len(iface['addresses'])}")
            for addr in iface["addresses"]:
                print(f"    {addr}")

        if issues:
            print(f"\n  \033[33mSecurity Issues ({len(issues)}):\033[0m")
            for i in issues:
                print(f"    ! {i}")

    print(f"\n  Free cheat sheets: https://dargslan.com/cheat-sheets")


if __name__ == "__main__":
    main()
