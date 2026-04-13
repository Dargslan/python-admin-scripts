#!/usr/bin/env python3
"""Syslog facility and severity monitor — analyze log sources and message rates."""

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path


SEVERITY_MAP = {
    "emerg": 0, "alert": 1, "crit": 2, "err": 3, "error": 3,
    "warning": 4, "warn": 4, "notice": 5, "info": 6, "debug": 7
}

FACILITY_PATTERNS = [
    (r"\b(kernel|kern)\b", "kern"),
    (r"\b(sshd|ssh)\b", "auth"),
    (r"\b(sudo|su)\b", "authpriv"),
    (r"\b(cron|crond|anacron)\b", "cron"),
    (r"\b(systemd|systemd-\w+)\b", "daemon"),
    (r"\b(postfix|sendmail|dovecot)\b", "mail"),
    (r"\b(named|bind)\b", "daemon"),
    (r"\b(NetworkManager|dhclient|dhcpd)\b", "daemon"),
]


def analyze_syslog(log_path, max_lines=10000):
    stats = {
        "total_lines": 0,
        "severity_counts": Counter(),
        "facility_counts": Counter(),
        "hourly_counts": Counter(),
        "top_processes": Counter(),
        "error_samples": [],
    }

    try:
        with open(log_path, "r", errors="replace") as f:
            for i, line in enumerate(f):
                if i >= max_lines:
                    break
                stats["total_lines"] += 1
                line = line.strip()

                for sev_name in ["emerg", "alert", "crit", "error", "err", "warning", "warn"]:
                    if re.search(rf"\b{sev_name}\b", line, re.IGNORECASE):
                        stats["severity_counts"][sev_name] += 1
                        if sev_name in ("error", "err", "crit") and len(stats["error_samples"]) < 5:
                            stats["error_samples"].append(line[:200])
                        break
                else:
                    stats["severity_counts"]["info"] += 1

                for pattern, facility in FACILITY_PATTERNS:
                    if re.search(pattern, line, re.IGNORECASE):
                        stats["facility_counts"][facility] += 1
                        break
                else:
                    stats["facility_counts"]["other"] += 1

                process_match = re.search(r"(\w+)\[\d+\]:", line)
                if process_match:
                    stats["top_processes"][process_match.group(1)] += 1

                time_match = re.match(r"(\w+ \d+ \d+):", line)
                if time_match:
                    try:
                        hour = time_match.group(1).split()[-1]
                        stats["hourly_counts"][hour] += 1
                    except (IndexError, ValueError):
                        pass

    except (FileNotFoundError, PermissionError) as e:
        print(f"  Cannot read {log_path}: {e}")
        return None

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Syslog facility and severity monitor",
        epilog="More tools: https://dargslan.com | pip install dargslan-toolkit"
    )
    parser.add_argument("-f", "--file", default="/var/log/syslog",
                        help="Log file to analyze (default: /var/log/syslog)")
    parser.add_argument("-n", "--lines", type=int, default=10000,
                        help="Max lines to analyze (default: 10000)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    log_path = args.file
    if not Path(log_path).exists():
        for alt in ["/var/log/messages", "/var/log/syslog"]:
            if Path(alt).exists():
                log_path = alt
                break

    stats = analyze_syslog(log_path, args.lines)

    if not stats:
        sys.exit(1)

    if args.json:
        result = {
            "file": log_path,
            "total_lines": stats["total_lines"],
            "severity": dict(stats["severity_counts"].most_common()),
            "facilities": dict(stats["facility_counts"].most_common()),
            "top_processes": dict(stats["top_processes"].most_common(10)),
            "error_samples": stats["error_samples"],
        }
        print(json.dumps(result, indent=2))
        return

    print(f"\033[1m  Dargslan Syslog Monitor\033[0m")
    print(f"  File: {log_path} | Lines analyzed: {stats['total_lines']}\n")

    print("  \033[1mSeverity Distribution:\033[0m")
    for sev, count in stats["severity_counts"].most_common():
        color = "\033[31m" if sev in ("emerg", "alert", "crit", "error", "err") else \
                "\033[33m" if sev in ("warning", "warn") else "\033[0m"
        bar = "#" * min(count * 40 // max(stats["severity_counts"].values()), 40)
        print(f"    {color}{sev:<10}\033[0m {count:>6}  {bar}")

    print(f"\n  \033[1mTop Facilities:\033[0m")
    for fac, count in stats["facility_counts"].most_common(8):
        print(f"    {fac:<15} {count:>6}")

    print(f"\n  \033[1mTop Processes:\033[0m")
    for proc, count in stats["top_processes"].most_common(8):
        print(f"    {proc:<20} {count:>6}")

    if stats["error_samples"]:
        print(f"\n  \033[31mRecent Errors:\033[0m")
        for err in stats["error_samples"][:3]:
            print(f"    {err[:120]}")

    print(f"\n  Free cheat sheets: https://dargslan.com/cheat-sheets")


if __name__ == "__main__":
    main()
