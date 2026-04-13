"""dargslan-disk-quota — Linux disk quota monitor."""

__version__ = "1.0.0"

import subprocess
import re
import os
import json
from datetime import datetime


def _run(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return r.stdout.strip()
    except Exception:
        return ""


def get_user_quotas():
    quotas = []
    out = _run("repquota -a 2>/dev/null || repquota / 2>/dev/null")
    if not out:
        return quotas
    for line in out.splitlines():
        m = re.match(r'^(\S+)\s+[-+]+\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)', line)
        if m:
            used_kb = int(m.group(2))
            soft_kb = int(m.group(3))
            hard_kb = int(m.group(4))
            quotas.append({
                "user": m.group(1),
                "used_kb": used_kb,
                "soft_limit_kb": soft_kb,
                "hard_limit_kb": hard_kb,
                "used_mb": round(used_kb / 1024, 1),
                "files_used": int(m.group(5)),
                "files_soft": int(m.group(6)),
                "files_hard": int(m.group(7)),
                "over_soft": used_kb > soft_kb > 0,
                "over_hard": used_kb > hard_kb > 0,
            })
    return quotas


def get_group_quotas():
    quotas = []
    out = _run("repquota -ag 2>/dev/null || repquota -g / 2>/dev/null")
    if not out:
        return quotas
    for line in out.splitlines():
        m = re.match(r'^(\S+)\s+[-+]+\s+(\d+)\s+(\d+)\s+(\d+)', line)
        if m:
            used_kb = int(m.group(2))
            soft_kb = int(m.group(3))
            hard_kb = int(m.group(4))
            quotas.append({
                "group": m.group(1),
                "used_kb": used_kb,
                "soft_limit_kb": soft_kb,
                "hard_limit_kb": hard_kb,
                "used_mb": round(used_kb / 1024, 1),
                "over_soft": used_kb > soft_kb > 0,
            })
    return quotas


def get_filesystem_usage():
    filesystems = []
    out = _run("df -h --output=source,size,used,avail,pcent,target 2>/dev/null")
    if not out:
        return filesystems
    for line in out.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 6 and not parts[0].startswith("tmpfs"):
            pct = parts[4].rstrip("%")
            filesystems.append({
                "device": parts[0],
                "size": parts[1],
                "used": parts[2],
                "available": parts[3],
                "use_percent": int(pct) if pct.isdigit() else 0,
                "mount": parts[5],
            })
    return filesystems


def check_quota_status():
    out = _run("quotaon -p -a 2>/dev/null")
    enabled = "is on" in out if out else False
    return {"raw": out, "enabled": enabled}


def generate_report():
    user_quotas = get_user_quotas()
    group_quotas = get_group_quotas()
    filesystems = get_filesystem_usage()
    quota_status = check_quota_status()
    issues = []

    for uq in user_quotas:
        if uq["over_hard"]:
            issues.append({
                "severity": "critical",
                "message": f"User {uq['user']} OVER hard limit: {uq['used_mb']}MB / {round(uq['hard_limit_kb']/1024,1)}MB"
            })
        elif uq["over_soft"]:
            issues.append({
                "severity": "warning",
                "message": f"User {uq['user']} over soft limit: {uq['used_mb']}MB / {round(uq['soft_limit_kb']/1024,1)}MB"
            })

    for fs in filesystems:
        if fs["use_percent"] >= 95:
            issues.append({
                "severity": "critical",
                "message": f"Filesystem {fs['mount']} at {fs['use_percent']}% capacity"
            })
        elif fs["use_percent"] >= 85:
            issues.append({
                "severity": "warning",
                "message": f"Filesystem {fs['mount']} at {fs['use_percent']}% capacity"
            })

    if not quota_status["enabled"]:
        issues.append({
            "severity": "info",
            "message": "Disk quotas are not enabled on any filesystem"
        })

    return {
        "timestamp": datetime.now().isoformat(),
        "quota_enabled": quota_status["enabled"],
        "user_quotas": user_quotas,
        "group_quotas": group_quotas,
        "filesystems": filesystems,
        "issues": issues,
        "issues_count": len(issues),
    }


def audit():
    return generate_report()["issues"]
