"""dargslan-uptime-report — System uptime and availability reporter."""

__version__ = "1.0.0"

import subprocess
import re
import os
import json
from datetime import datetime, timedelta
from collections import defaultdict


def _run(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return r.stdout.strip()
    except Exception:
        return ""


def get_uptime():
    try:
        with open("/proc/uptime", "r") as f:
            uptime_seconds = float(f.read().split()[0])
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        return {
            "seconds": uptime_seconds,
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "human": f"{days}d {hours}h {minutes}m",
            "boot_time": (datetime.now() - timedelta(seconds=uptime_seconds)).isoformat(),
        }
    except Exception:
        return {"seconds": 0, "human": "unknown", "boot_time": "unknown"}


def get_reboot_history(max_entries=50):
    reboots = []
    out = _run("last reboot -F 2>/dev/null || last reboot 2>/dev/null")
    for line in out.splitlines():
        if line.startswith("reboot"):
            parts = line.split()
            date_str = " ".join(parts[4:8]) if len(parts) > 7 else " ".join(parts[4:])
            reboots.append({
                "type": "reboot",
                "kernel": parts[2] if len(parts) > 2 else "unknown",
                "date": date_str,
            })
    return reboots[:max_entries]


def get_shutdown_history(max_entries=50):
    shutdowns = []
    out = _run("last -x shutdown -F 2>/dev/null || last -x shutdown 2>/dev/null")
    for line in out.splitlines():
        if "shutdown" in line:
            parts = line.split()
            date_str = " ".join(parts[4:8]) if len(parts) > 7 else " ".join(parts[4:])
            shutdowns.append({
                "type": "shutdown",
                "date": date_str,
            })
    return shutdowns[:max_entries]


def get_crash_events():
    crashes = []
    out = _run("journalctl --list-boots 2>/dev/null")
    boots = out.splitlines()
    for line in boots:
        parts = line.split()
        if len(parts) >= 4:
            boot_id = parts[1] if len(parts) > 1 else ""
            crashes.append({
                "boot_id": boot_id,
                "date": " ".join(parts[2:4]) if len(parts) > 3 else "",
            })

    kernel_panics = _run("journalctl -k -p 0 --no-pager -q 2>/dev/null")
    panic_count = len([l for l in kernel_panics.splitlines() if l.strip()])

    oom_kills = _run("journalctl --no-pager -q -g 'Out of memory' 2>/dev/null")
    oom_count = len([l for l in oom_kills.splitlines() if l.strip()])

    return {
        "total_boots": len(boots),
        "kernel_panics": panic_count,
        "oom_kills": oom_count,
    }


def get_load_average():
    try:
        with open("/proc/loadavg", "r") as f:
            parts = f.read().split()
        return {
            "1min": float(parts[0]),
            "5min": float(parts[1]),
            "15min": float(parts[2]),
        }
    except Exception:
        return {"1min": 0, "5min": 0, "15min": 0}


def calculate_availability(uptime_seconds, total_period_seconds=None):
    if total_period_seconds is None:
        total_period_seconds = 30 * 86400
    if total_period_seconds <= 0:
        return 100.0
    pct = min(100.0, (uptime_seconds / total_period_seconds) * 100)
    return round(pct, 4)


def generate_report():
    uptime = get_uptime()
    reboots = get_reboot_history()
    shutdowns = get_shutdown_history()
    crashes = get_crash_events()
    load = get_load_average()
    avail_30d = calculate_availability(uptime["seconds"])
    issues = []

    if uptime["seconds"] < 3600:
        issues.append({
            "severity": "warning",
            "message": f"System uptime very low: {uptime['human']} — recent reboot detected"
        })

    if crashes["kernel_panics"] > 0:
        issues.append({
            "severity": "critical",
            "message": f"Kernel panics detected: {crashes['kernel_panics']}"
        })

    if crashes["oom_kills"] > 0:
        issues.append({
            "severity": "warning",
            "message": f"OOM kills detected: {crashes['oom_kills']}"
        })

    cpu_count = os.cpu_count() or 1
    if load["1min"] > cpu_count * 2:
        issues.append({
            "severity": "warning",
            "message": f"High load average: {load['1min']} (CPUs: {cpu_count})"
        })

    if len(reboots) > 5:
        issues.append({
            "severity": "warning",
            "message": f"Frequent reboots detected: {len(reboots)} in recent history"
        })

    return {
        "timestamp": datetime.now().isoformat(),
        "uptime": uptime,
        "availability_30d": avail_30d,
        "load_average": load,
        "cpu_count": cpu_count,
        "reboots": reboots,
        "reboot_count": len(reboots),
        "shutdowns": shutdowns,
        "crash_info": crashes,
        "issues": issues,
        "issues_count": len(issues),
    }


def audit():
    report = generate_report()
    return report["issues"]
