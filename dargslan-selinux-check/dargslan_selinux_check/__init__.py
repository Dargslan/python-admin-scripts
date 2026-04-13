"""dargslan-selinux-check — SELinux status checker.

Check SELinux mode, audit booleans, verify contexts, and analyze denials.
Part of the Dargslan Linux Sysadmin Toolkit: https://dargslan.com
"""

__version__ = "1.0.0"

import subprocess
import os


def get_selinux_status():
    """Get current SELinux status and mode."""
    status = {"installed": False, "mode": "unknown", "policy": "unknown", "enabled": False}
    try:
        result = subprocess.run(["getenforce"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            status["installed"] = True
            mode = result.stdout.strip().lower()
            status["mode"] = mode
            status["enabled"] = mode in ("enforcing", "permissive")
    except (subprocess.SubprocessError, FileNotFoundError):
        if os.path.exists("/etc/selinux/config"):
            status["installed"] = True
            try:
                with open("/etc/selinux/config") as f:
                    for line in f:
                        if line.startswith("SELINUX="):
                            status["mode"] = line.split("=")[1].strip().lower()
                        elif line.startswith("SELINUXTYPE="):
                            status["policy"] = line.split("=")[1].strip()
            except (IOError, OSError):
                pass
    try:
        result = subprocess.run(["sestatus"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            for line in result.stdout.split("\n"):
                if "policy" in line.lower() and ":" in line:
                    status["policy"] = line.split(":")[-1].strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    return status


def get_booleans():
    """Get SELinux boolean values."""
    booleans = []
    try:
        result = subprocess.run(["getsebool", "-a"], capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                if " --> " in line:
                    parts = line.split(" --> ")
                    booleans.append({"name": parts[0].strip(), "value": parts[1].strip()})
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    return booleans


def get_recent_denials(count=20):
    """Get recent SELinux denial messages from audit log."""
    denials = []
    try:
        result = subprocess.run(["ausearch", "-m", "avc", "-ts", "recent"],
                                capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                if "avc:" in line and "denied" in line:
                    denials.append(line.strip())
    except (subprocess.SubprocessError, FileNotFoundError):
        audit_log = "/var/log/audit/audit.log"
        if os.path.exists(audit_log):
            try:
                with open(audit_log, "r") as f:
                    for line in f:
                        if "avc" in line and "denied" in line:
                            denials.append(line.strip())
            except (IOError, OSError):
                pass
    return denials[-count:]


def get_file_context(path):
    """Get SELinux context for a file."""
    try:
        result = subprocess.run(["ls", "-Z", path], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.SubprocessError, OSError):
        pass
    return None


def check_security_score():
    """Calculate a basic SELinux security score."""
    status = get_selinux_status()
    score = 0
    issues = []
    if not status["installed"]:
        issues.append("SELinux is not installed")
        return {"score": 0, "max": 100, "issues": issues}
    if status["mode"] == "enforcing":
        score += 50
    elif status["mode"] == "permissive":
        score += 20
        issues.append("SELinux is in permissive mode (not enforcing)")
    else:
        issues.append("SELinux is disabled")
    denials = get_recent_denials(50)
    if len(denials) == 0:
        score += 30
    elif len(denials) < 10:
        score += 20
        issues.append(f"{len(denials)} recent AVC denials found")
    else:
        score += 5
        issues.append(f"{len(denials)} recent AVC denials found (high)")
    if status["policy"] == "targeted":
        score += 20
    elif status["policy"] != "unknown":
        score += 15
    else:
        issues.append("Cannot determine SELinux policy type")
    return {"score": min(score, 100), "max": 100, "issues": issues}


def generate_report():
    """Generate comprehensive SELinux report."""
    status = get_selinux_status()
    security = check_security_score()
    denials = get_recent_denials()

    lines = []
    lines.append("=" * 60)
    lines.append("SELINUX STATUS REPORT")
    lines.append("=" * 60)
    lines.append(f"\nInstalled: {'Yes' if status['installed'] else 'No'}")
    lines.append(f"Mode: {status['mode']}")
    lines.append(f"Policy: {status['policy']}")
    lines.append(f"Security Score: {security['score']}/{security['max']}")

    if security["issues"]:
        lines.append("\n--- Issues ---")
        for issue in security["issues"]:
            lines.append(f"  [!] {issue}")

    if denials:
        lines.append(f"\n--- Recent Denials ({len(denials)}) ---")
        for d in denials[:10]:
            lines.append(f"  {d[:120]}")

    if not status["installed"]:
        lines.append("\n--- Recommendations ---")
        lines.append("  Consider installing and enabling SELinux for enhanced security.")
        lines.append("  RHEL/CentOS: yum install selinux-policy-targeted")

    lines.append("\n" + "=" * 60)
    lines.append("More tools: https://dargslan.com | pip install dargslan-toolkit")
    lines.append("=" * 60)
    return "\n".join(lines)
