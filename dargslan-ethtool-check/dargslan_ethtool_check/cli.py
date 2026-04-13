#!/usr/bin/env python3
"""Network interface diagnostics — check link speed, duplex, driver info, and NIC capabilities."""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


def get_interfaces():
    net_dir = Path("/sys/class/net")
    if not net_dir.exists():
        return []
    ifaces = []
    for iface in sorted(net_dir.iterdir()):
        name = iface.name
        if name == "lo":
            continue
        ifaces.append(name)
    return ifaces


def read_sysfs(iface, attr):
    path = Path(f"/sys/class/net/{iface}/{attr}")
    try:
        return path.read_text().strip()
    except (FileNotFoundError, PermissionError, OSError):
        return None


def get_interface_info(iface):
    info = {
        "interface": iface,
        "state": read_sysfs(iface, "operstate") or "unknown",
        "mac_address": read_sysfs(iface, "address") or "N/A",
        "mtu": read_sysfs(iface, "mtu") or "N/A",
        "speed_mbps": None,
        "duplex": None,
        "driver": None,
        "firmware": None,
        "link_detected": None,
        "auto_negotiation": None,
        "rx_bytes": read_sysfs(iface, "statistics/rx_bytes"),
        "tx_bytes": read_sysfs(iface, "statistics/tx_bytes"),
        "rx_packets": read_sysfs(iface, "statistics/rx_packets"),
        "tx_packets": read_sysfs(iface, "statistics/tx_packets"),
        "rx_errors": read_sysfs(iface, "statistics/rx_errors"),
        "tx_errors": read_sysfs(iface, "statistics/tx_errors"),
        "rx_dropped": read_sysfs(iface, "statistics/rx_dropped"),
        "tx_dropped": read_sysfs(iface, "statistics/tx_dropped"),
    }

    speed = read_sysfs(iface, "speed")
    if speed and speed.lstrip("-").isdigit():
        val = int(speed)
        if val > 0:
            info["speed_mbps"] = val

    info["duplex"] = read_sysfs(iface, "duplex")

    driver_link = Path(f"/sys/class/net/{iface}/device/driver")
    if driver_link.exists():
        try:
            info["driver"] = driver_link.resolve().name
        except OSError:
            pass

    try:
        result = subprocess.run(
            ["ethtool", iface],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            output = result.stdout
            for line in output.splitlines():
                line = line.strip()
                if line.startswith("Speed:"):
                    m = re.search(r"(\d+)", line)
                    if m:
                        info["speed_mbps"] = int(m.group(1))
                elif line.startswith("Duplex:"):
                    info["duplex"] = line.split(":", 1)[1].strip()
                elif line.startswith("Link detected:"):
                    info["link_detected"] = line.split(":", 1)[1].strip()
                elif line.startswith("Auto-negotiation:"):
                    info["auto_negotiation"] = line.split(":", 1)[1].strip()
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass

    try:
        result = subprocess.run(
            ["ethtool", "-i", iface],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if line.startswith("driver:"):
                    info["driver"] = line.split(":", 1)[1].strip()
                elif line.startswith("firmware-version:"):
                    info["firmware"] = line.split(":", 1)[1].strip()
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass

    return info


def format_bytes(b):
    if b is None:
        return "N/A"
    b = int(b)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} PB"


def print_interface(info, verbose=False):
    state_colors = {"up": "\033[32m", "down": "\033[31m", "unknown": "\033[33m"}
    reset = "\033[0m"
    bold = "\033[1m"

    state = info["state"]
    color = state_colors.get(state, "\033[33m")

    print(f"\n{bold}{'='*60}{reset}")
    print(f"{bold}  Interface: {info['interface']}{reset}  [{color}{state.upper()}{reset}]")
    print(f"{'='*60}")

    print(f"  MAC Address      : {info['mac_address']}")
    print(f"  MTU              : {info['mtu']}")

    if info["speed_mbps"]:
        speed = info["speed_mbps"]
        if speed >= 1000:
            print(f"  Link Speed       : {speed // 1000} Gbps ({speed} Mbps)")
        else:
            print(f"  Link Speed       : {speed} Mbps")
    else:
        print(f"  Link Speed       : N/A")

    print(f"  Duplex           : {info['duplex'] or 'N/A'}")
    print(f"  Driver           : {info['driver'] or 'N/A'}")
    print(f"  Firmware         : {info['firmware'] or 'N/A'}")
    print(f"  Link Detected    : {info['link_detected'] or 'N/A'}")
    print(f"  Auto-negotiation : {info['auto_negotiation'] or 'N/A'}")

    if verbose:
        print(f"\n  {bold}Traffic Statistics:{reset}")
        print(f"  RX Bytes     : {format_bytes(info['rx_bytes']):>12}   TX Bytes   : {format_bytes(info['tx_bytes']):>12}")
        print(f"  RX Packets   : {info['rx_packets'] or 'N/A':>12}   TX Packets : {info['tx_packets'] or 'N/A':>12}")
        print(f"  RX Errors    : {info['rx_errors'] or '0':>12}   TX Errors  : {info['tx_errors'] or '0':>12}")
        print(f"  RX Dropped   : {info['rx_dropped'] or '0':>12}   TX Dropped : {info['tx_dropped'] or '0':>12}")


def print_summary(interfaces_info):
    print(f"\n\033[1m{'='*60}\033[0m")
    print(f"\033[1m  SUMMARY — {len(interfaces_info)} interface(s)\033[0m")
    print(f"{'='*60}")
    print(f"  {'Interface':<15} {'State':<8} {'Speed':<12} {'Driver':<15} {'Link'}")
    print(f"  {'-'*55}")
    for info in interfaces_info:
        state = info["state"].upper()
        speed = f"{info['speed_mbps']} Mbps" if info["speed_mbps"] else "N/A"
        driver = info["driver"] or "N/A"
        link = info["link_detected"] or "N/A"
        print(f"  {info['interface']:<15} {state:<8} {speed:<12} {driver:<15} {link}")


def main():
    parser = argparse.ArgumentParser(
        description="Network interface diagnostics — check link speed, duplex, driver, and NIC capabilities.",
        epilog="More Linux tools: https://dargslan.com | Cheat sheets: https://dargslan.com/cheat-sheets"
    )
    parser.add_argument("-i", "--interface", help="Check specific interface only")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show traffic statistics")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--summary", action="store_true", help="Show summary table only")
    parser.add_argument("--errors-only", action="store_true", help="Show only interfaces with errors")
    args = parser.parse_args()

    if args.interface:
        ifaces = [args.interface]
    else:
        ifaces = get_interfaces()

    if not ifaces:
        print("No network interfaces found.")
        sys.exit(1)

    results = []
    for iface in ifaces:
        info = get_interface_info(iface)
        results.append(info)

    if args.errors_only:
        results = [r for r in results if (
            int(r.get("rx_errors") or 0) > 0 or
            int(r.get("tx_errors") or 0) > 0 or
            int(r.get("rx_dropped") or 0) > 0 or
            int(r.get("tx_dropped") or 0) > 0
        )]

    if args.json:
        print(json.dumps(results, indent=2, default=str))
        return

    if not results:
        print("No interfaces match the criteria.")
        sys.exit(0)

    if args.summary:
        print_summary(results)
    else:
        print(f"\033[1m  Dargslan Ethtool Check — Network Interface Diagnostics\033[0m")
        print(f"  https://dargslan.com")
        for info in results:
            print_interface(info, verbose=args.verbose)
        print_summary(results)

    has_issues = any(
        int(r.get("rx_errors") or 0) > 0 or int(r.get("tx_errors") or 0) > 0
        for r in results
    )
    if has_issues:
        print(f"\n\033[33m  ⚠ Some interfaces have errors — investigate with: ethtool -S <interface>\033[0m")

    print(f"\n  Free Linux cheat sheets → https://dargslan.com/cheat-sheets")


if __name__ == "__main__":
    main()
