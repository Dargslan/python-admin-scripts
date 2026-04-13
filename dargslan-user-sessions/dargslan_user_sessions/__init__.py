"""dargslan-user-sessions — Linux user session manager.

Monitor active sessions, detect idle users, check session limits, and TTY monitoring.
Part of the Dargslan Linux Sysadmin Toolkit: https://dargslan.com
"""

__version__ = "1.0.0"

import subprocess
import os
from datetime import datetime


def get_active_sessions():
    """Get all active user sessions using who."""
    sessions = []
    try:
        result = subprocess.run(["who", "-u"], capture_output=True, text=True, timeout=10)
        for line in result.stdout.strip().split("\n"):
            if line.strip():
                parts = line.split()
                if len(parts) >= 5:
                    sessions.append({
                        "user": parts[0],
                        "tty": parts[1],
                        "date": parts[2] if len(parts) > 2 else "",
                        "time": parts[3] if len(parts) > 3 else "",
                        "idle": parts[4] if len(parts) > 4 else "active",
                        "pid": parts[5] if len(parts) > 5 else "",
                    })
    except (subprocess.SubprocessError, OSError):
        pass
    return sessions


def get_idle_sessions(threshold_minutes=30):
    """Find sessions idle for more than threshold minutes."""
    sessions = get_active_sessions()
    idle = []
    for s in sessions:
        idle_str = s.get("idle", "")
        if idle_str and idle_str not in (".", "active", "old"):
            try:
                parts = idle_str.split(":")
                if len(parts) == 2:
                    minutes = int(parts[0]) * 60 + int(parts[1])
                    if minutes >= threshold_minutes:
                        s["idle_minutes"] = minutes
                        idle.append(s)
            except (ValueError, IndexError):
                pass
    return idle


def get_user_count():
    """Count unique logged-in users."""
    sessions = get_active_sessions()
    return len(set(s["user"] for s in sessions))


def get_session_types():
    """Categorize sessions by type (console, SSH, GUI)."""
    sessions = get_active_sessions()
    types = {"console": [], "ssh": [], "gui": [], "other": []}
    for s in sessions:
        tty = s.get("tty", "")
        if tty.startswith("pts/"):
            types["ssh"].append(s)
        elif tty.startswith("tty"):
            types["console"].append(s)
        elif tty.startswith(":"):
            types["gui"].append(s)
        else:
            types["other"].append(s)
    return types


def get_last_logins(count=10):
    """Get recent login history."""
    entries = []
    try:
        result = subprocess.run(["last", "-n", str(count)], capture_output=True, text=True, timeout=10)
        for line in result.stdout.strip().split("\n"):
            if line.strip() and not line.startswith("wtmp") and not line.startswith("reboot"):
                entries.append(line.strip())
    except (subprocess.SubprocessError, OSError):
        pass
    return entries


def get_login_limits():
    """Check configured login limits from limits.conf."""
    limits = []
    try:
        with open("/etc/security/limits.conf", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    parts = line.split()
                    if len(parts) >= 4 and parts[2] == "maxlogins":
                        limits.append({"domain": parts[0], "type": parts[1], "limit": parts[3]})
    except (IOError, OSError):
        pass
    return limits


def generate_report():
    """Generate comprehensive session report."""
    sessions = get_active_sessions()
    types = get_session_types()
    idle = get_idle_sessions()
    last = get_last_logins()

    lines = []
    lines.append("=" * 60)
    lines.append("USER SESSION REPORT")
    lines.append("=" * 60)
    lines.append(f"\nActive sessions: {len(sessions)}")
    lines.append(f"Unique users: {get_user_count()}")
    lines.append(f"SSH sessions: {len(types['ssh'])}")
    lines.append(f"Console sessions: {len(types['console'])}")
    lines.append(f"Idle sessions (>30min): {len(idle)}")

    if sessions:
        lines.append("\n--- Active Sessions ---")
        for s in sessions:
            idle_str = s.get('idle', 'active')
            if idle_str == '.':
                idle_str = 'active'
            lines.append(f"  {s['user']:15s} {s['tty']:10s} {s.get('date','')} {s.get('time','')} idle={idle_str}")

    if idle:
        lines.append("\n--- Idle Sessions (>30 min) ---")
        for s in idle:
            lines.append(f"  [IDLE] {s['user']:15s} {s['tty']:10s} idle={s.get('idle_minutes', '?')}min")

    if last:
        lines.append("\n--- Recent Login History ---")
        for entry in last[:10]:
            lines.append(f"  {entry}")

    lines.append("\n" + "=" * 60)
    lines.append("More tools: https://dargslan.com | pip install dargslan-toolkit")
    lines.append("=" * 60)
    return "\n".join(lines)
