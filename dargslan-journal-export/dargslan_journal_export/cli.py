#!/usr/bin/env python3
"""Systemd Journal Log Exporter."""

import subprocess
import os
import argparse
from datetime import datetime


def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        return result.stdout.strip(), result.returncode
    except:
        return "", 1


def show_journal_stats():
    print("=== Journal Statistics ===")
    out, rc = run_cmd("journalctl --disk-usage 2>/dev/null")
    if rc == 0 and out:
        print(f"  {out}")

    out2, _ = run_cmd("journalctl --list-boots 2>/dev/null | wc -l")
    if out2:
        print(f"  Boot records: {out2}")

    out3, _ = run_cmd("journalctl --list-boots 2>/dev/null | head -1")
    if out3:
        print(f"  Oldest boot: {out3}")

    out4, _ = run_cmd("journalctl --list-boots 2>/dev/null | tail -1")
    if out4:
        print(f"  Current boot: {out4}")


def show_units():
    print("\n=== Logging Units ===")
    out, rc = run_cmd("journalctl --field=_SYSTEMD_UNIT 2>/dev/null | head -30")
    if rc == 0 and out:
        units = out.strip().split("\n")
        print(f"  Units logging to journal: {len(units)}")
        for unit in units[:20]:
            print(f"    {unit}")
        if len(units) > 20:
            print(f"    ... and {len(units) - 20} more")
    else:
        print("  Could not list journal units")


def show_priorities():
    print("\n=== Messages by Priority ===")
    priorities = {
        0: "Emergency", 1: "Alert", 2: "Critical",
        3: "Error", 4: "Warning", 5: "Notice",
        6: "Informational", 7: "Debug"
    }
    for level, name in priorities.items():
        out, rc = run_cmd(f"journalctl -p {level} --no-pager -q 2>/dev/null | wc -l")
        count = int(out) if rc == 0 and out else 0
        if count > 0:
            marker = " !!!" if level <= 3 else ""
            print(f"  [{level}] {name:<15}: {count} messages{marker}")


def export_recent(hours=24, output_file=None):
    print(f"\n=== Recent Logs ({hours}h) ===")
    cmd = f"journalctl --since '{hours} hours ago' --no-pager -q 2>/dev/null"

    if output_file:
        out, rc = run_cmd(f"{cmd} > {output_file}")
        if rc == 0:
            size = os.path.getsize(output_file) if os.path.exists(output_file) else 0
            print(f"  Exported to: {output_file}")
            print(f"  File size: {size} bytes")
        else:
            print(f"  Export failed")
    else:
        out, rc = run_cmd(f"{cmd} | wc -l")
        count = int(out) if rc == 0 and out else 0
        print(f"  Log lines in last {hours}h: {count}")

        out2, _ = run_cmd(f"{cmd} | tail -15")
        if out2:
            print(f"\n  Latest entries:")
            for line in out2.split("\n"):
                print(f"    {line}")


def export_unit(unit, output_file=None):
    print(f"\n=== Logs for {unit} ===")
    cmd = f"journalctl -u {unit} --no-pager -q 2>/dev/null"

    if output_file:
        out, rc = run_cmd(f"{cmd} > {output_file}")
        if rc == 0:
            size = os.path.getsize(output_file) if os.path.exists(output_file) else 0
            print(f"  Exported to: {output_file}")
            print(f"  File size: {size} bytes")
    else:
        out, rc = run_cmd(f"{cmd} | wc -l")
        count = int(out) if rc == 0 and out else 0
        print(f"  Total log lines: {count}")

        out2, _ = run_cmd(f"{cmd} | tail -15")
        if out2:
            print(f"\n  Latest entries:")
            for line in out2.split("\n"):
                print(f"    {line}")


def check_journal_config():
    print("\n=== Journal Configuration ===")
    config_files = ["/etc/systemd/journald.conf"]
    for cf in config_files:
        if os.path.exists(cf):
            out, rc = run_cmd(f"grep -v '^#' {cf} | grep -v '^$' 2>/dev/null")
            if rc == 0 and out:
                print(f"  {cf}:")
                for line in out.split("\n"):
                    print(f"    {line}")

    out2, _ = run_cmd("systemctl status systemd-journald 2>/dev/null | head -5")
    if out2:
        for line in out2.split("\n"):
            print(f"  {line.strip()}")


def main():
    parser = argparse.ArgumentParser(description="Systemd Journal Log Exporter")
    parser.add_argument("--stats", action="store_true", help="Show journal statistics")
    parser.add_argument("--units", action="store_true", help="List logging units")
    parser.add_argument("--priorities", action="store_true", help="Show message counts by priority")
    parser.add_argument("--recent", type=int, metavar="HOURS", help="Show/export recent N hours")
    parser.add_argument("--unit", type=str, metavar="UNIT", help="Show/export logs for specific unit")
    parser.add_argument("--config", action="store_true", help="Show journal configuration")
    parser.add_argument("-o", "--output", type=str, metavar="FILE", help="Export to file")
    args = parser.parse_args()

    print("Systemd Journal Log Exporter")
    print("=" * 40)

    if args.stats:
        show_journal_stats()
    elif args.units:
        show_units()
    elif args.priorities:
        show_priorities()
    elif args.recent is not None:
        export_recent(args.recent, args.output)
    elif args.unit:
        export_unit(args.unit, args.output)
    elif args.config:
        check_journal_config()
    else:
        show_journal_stats()
        show_priorities()
        show_units()
        check_journal_config()

    print("\n" + "=" * 40)
    print("Powered by dargslan.com")


if __name__ == "__main__":
    main()
