"""dargslan-process-killer — Zombie and runaway process hunter."""

__version__ = "1.0.0"

import subprocess
import re
import os
import signal
import json
from datetime import datetime


def _run(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return r.stdout.strip()
    except Exception:
        return ""


def get_zombies():
    zombies = []
    out = _run("ps aux | awk '$8 ~ /Z/ {print $0}'")
    for line in out.splitlines():
        parts = line.split(None, 10)
        if len(parts) >= 11:
            zombies.append({
                "user": parts[0],
                "pid": int(parts[1]),
                "ppid": _run(f"ps -o ppid= -p {parts[1]}").strip(),
                "cpu": parts[2],
                "mem": parts[3],
                "command": parts[10],
            })
    return zombies


def get_resource_hogs(cpu_threshold=80, mem_threshold=50):
    hogs = []
    out = _run("ps aux --sort=-%cpu 2>/dev/null")
    for line in out.splitlines()[1:21]:
        parts = line.split(None, 10)
        if len(parts) >= 11:
            cpu = float(parts[2])
            mem = float(parts[3])
            if cpu >= cpu_threshold or mem >= mem_threshold:
                hogs.append({
                    "user": parts[0],
                    "pid": int(parts[1]),
                    "cpu_percent": cpu,
                    "mem_percent": mem,
                    "vsz_kb": int(parts[4]),
                    "rss_kb": int(parts[5]),
                    "stat": parts[7],
                    "command": parts[10],
                })
    return hogs


def get_long_running(hours=24):
    processes = []
    out = _run(f"ps -eo pid,user,etimes,comm --sort=-etimes 2>/dev/null")
    threshold_seconds = hours * 3600
    for line in out.splitlines()[1:]:
        parts = line.split(None, 3)
        if len(parts) >= 4:
            try:
                elapsed = int(parts[2])
                if elapsed > threshold_seconds:
                    days = elapsed // 86400
                    hrs = (elapsed % 86400) // 3600
                    processes.append({
                        "pid": int(parts[0]),
                        "user": parts[1],
                        "elapsed_seconds": elapsed,
                        "elapsed_human": f"{days}d {hrs}h",
                        "command": parts[3],
                    })
            except ValueError:
                pass
    return processes[:20]


def get_orphans():
    orphans = []
    out = _run("ps -eo pid,ppid,user,comm | awk '$2 == 1 && $1 != 1'")
    for line in out.splitlines():
        parts = line.split(None, 3)
        if len(parts) >= 4:
            try:
                orphans.append({
                    "pid": int(parts[0]),
                    "ppid": int(parts[1]),
                    "user": parts[2],
                    "command": parts[3],
                })
            except ValueError:
                pass
    return orphans


def get_top_cpu(count=10):
    processes = []
    out = _run("ps aux --sort=-%cpu 2>/dev/null")
    for line in out.splitlines()[1:count+1]:
        parts = line.split(None, 10)
        if len(parts) >= 11:
            processes.append({
                "pid": int(parts[1]),
                "user": parts[0],
                "cpu_percent": float(parts[2]),
                "mem_percent": float(parts[3]),
                "rss_mb": round(int(parts[5]) / 1024, 1),
                "command": parts[10][:60],
            })
    return processes


def get_top_mem(count=10):
    processes = []
    out = _run("ps aux --sort=-%mem 2>/dev/null")
    for line in out.splitlines()[1:count+1]:
        parts = line.split(None, 10)
        if len(parts) >= 11:
            processes.append({
                "pid": int(parts[1]),
                "user": parts[0],
                "cpu_percent": float(parts[2]),
                "mem_percent": float(parts[3]),
                "rss_mb": round(int(parts[5]) / 1024, 1),
                "command": parts[10][:60],
            })
    return processes


def generate_report():
    zombies = get_zombies()
    hogs = get_resource_hogs()
    long_running = get_long_running()
    top_cpu = get_top_cpu()
    top_mem = get_top_mem()
    issues = []

    if zombies:
        issues.append({
            "severity": "warning",
            "message": f"Found {len(zombies)} zombie process(es)"
        })
        for z in zombies[:3]:
            issues.append({
                "severity": "info",
                "message": f"  Zombie PID {z['pid']}: {z['command']} (parent: {z['ppid']})"
            })

    for h in hogs:
        if h["cpu_percent"] >= 90:
            issues.append({
                "severity": "critical",
                "message": f"PID {h['pid']} using {h['cpu_percent']}% CPU: {h['command'][:40]}"
            })
        elif h["mem_percent"] >= 80:
            issues.append({
                "severity": "critical",
                "message": f"PID {h['pid']} using {h['mem_percent']}% memory: {h['command'][:40]}"
            })

    return {
        "timestamp": datetime.now().isoformat(),
        "zombies": zombies,
        "zombie_count": len(zombies),
        "resource_hogs": hogs,
        "long_running": long_running,
        "top_cpu": top_cpu,
        "top_mem": top_mem,
        "issues": issues,
        "issues_count": len(issues),
    }


def audit():
    return generate_report()["issues"]
