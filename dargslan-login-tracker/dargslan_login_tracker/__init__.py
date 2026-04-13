"""dargslan-login-tracker — Linux login and SSH session tracker."""

__version__ = "1.0.0"

import subprocess
import re
import os
import json
from datetime import datetime
from collections import defaultdict


def _run(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return r.stdout.strip()
    except Exception:
        return ""


def get_current_sessions():
    sessions = []
    out = _run("who -u 2>/dev/null || who 2>/dev/null")
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 3:
            sessions.append({
                "user": parts[0],
                "terminal": parts[1],
                "login_time": " ".join(parts[2:4]) if len(parts) > 3 else parts[2],
                "from": parts[-1].strip("()") if parts[-1].startswith("(") else "",
            })
    return sessions


def get_last_logins(count=20):
    logins = []
    out = _run(f"last -n {count} -F 2>/dev/null || last -n {count} 2>/dev/null")
    for line in out.splitlines():
        if not line.strip() or line.startswith("wtmp") or line.startswith("reboot"):
            continue
        parts = line.split()
        if len(parts) >= 4:
            logins.append({
                "user": parts[0],
                "terminal": parts[1],
                "from": parts[2] if not parts[2].startswith(("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")) else "",
                "raw": line.strip(),
            })
    return logins


def get_failed_logins(count=50):
    failures = []
    out = _run(f"lastb -n {count} 2>/dev/null")
    if not out:
        out = _run("journalctl -u sshd -g 'Failed password' --no-pager -n 50 2>/dev/null")
    for line in out.splitlines():
        if not line.strip() or line.startswith("btmp"):
            continue
        parts = line.split()
        if len(parts) >= 3:
            failures.append({
                "user": parts[0],
                "from": parts[2] if len(parts) > 2 and re.match(r'\d+\.\d+', parts[2]) else "",
                "raw": line.strip(),
            })
    return failures


def get_ssh_sessions():
    sessions = []
    out = _run("ss -tnp | grep ':22 ' 2>/dev/null || ss -tnp state established '( dport = :22 or sport = :22 )' 2>/dev/null")
    for line in out.splitlines():
        if "ssh" in line.lower() or ":22 " in line:
            parts = line.split()
            if len(parts) >= 5:
                sessions.append({
                    "state": parts[0],
                    "local": parts[3],
                    "remote": parts[4],
                })
    return sessions


def detect_brute_force(threshold=5):
    failed = get_failed_logins(200)
    ip_counts = defaultdict(int)
    user_counts = defaultdict(int)
    for f in failed:
        if f["from"]:
            ip_counts[f["from"]] += 1
        if f["user"]:
            user_counts[f["user"]] += 1
    suspicious_ips = {ip: count for ip, count in ip_counts.items() if count >= threshold}
    suspicious_users = {user: count for user, count in user_counts.items() if count >= threshold}
    return {
        "suspicious_ips": suspicious_ips,
        "suspicious_users": suspicious_users,
        "total_failed": len(failed),
    }


def generate_report():
    current = get_current_sessions()
    last = get_last_logins()
    failed = get_failed_logins()
    ssh = get_ssh_sessions()
    brute = detect_brute_force()
    issues = []

    if brute["suspicious_ips"]:
        for ip, count in brute["suspicious_ips"].items():
            issues.append({
                "severity": "critical",
                "message": f"Possible brute force from {ip}: {count} failed attempts"
            })

    if brute["suspicious_users"]:
        for user, count in brute["suspicious_users"].items():
            if user not in ("root", "admin"):
                issues.append({
                    "severity": "warning",
                    "message": f"Multiple failed logins for user '{user}': {count} attempts"
                })

    root_sessions = [s for s in current if s["user"] == "root"]
    if root_sessions:
        issues.append({
            "severity": "warning",
            "message": f"Root user has {len(root_sessions)} active session(s)"
        })

    if brute["total_failed"] > 50:
        issues.append({
            "severity": "warning",
            "message": f"High number of failed logins: {brute['total_failed']}"
        })

    return {
        "timestamp": datetime.now().isoformat(),
        "current_sessions": current,
        "active_users": len(current),
        "ssh_connections": len(ssh),
        "recent_logins": last,
        "failed_logins": len(failed),
        "brute_force_detection": brute,
        "issues": issues,
        "issues_count": len(issues),
    }


def audit():
    return generate_report()["issues"]
