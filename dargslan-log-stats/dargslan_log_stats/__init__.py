"""dargslan-log-stats — Linux log file statistics.

Analyze log file sizes, growth rates, rotation status, and disk usage.
Part of the Dargslan Linux Sysadmin Toolkit: https://dargslan.com
"""

__version__ = "1.0.0"

import os
import subprocess
from datetime import datetime


LOG_DIRS = ["/var/log"]
COMMON_LOGS = [
    "/var/log/syslog", "/var/log/messages", "/var/log/auth.log",
    "/var/log/kern.log", "/var/log/dmesg", "/var/log/boot.log",
    "/var/log/nginx/access.log", "/var/log/nginx/error.log",
    "/var/log/apache2/access.log", "/var/log/apache2/error.log",
    "/var/log/mysql/error.log", "/var/log/postgresql/postgresql-main.log",
]


def get_log_files(directory="/var/log", min_size=0):
    """Find log files in directory with size information."""
    logs = []
    try:
        for root, dirs, files in os.walk(directory):
            for f in files:
                path = os.path.join(root, f)
                try:
                    stat = os.stat(path)
                    if stat.st_size >= min_size:
                        logs.append({
                            "path": path,
                            "size": stat.st_size,
                            "size_human": _human_size(stat.st_size),
                            "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                            "is_compressed": f.endswith((".gz", ".bz2", ".xz", ".zst")),
                        })
                except (OSError, IOError):
                    pass
    except (OSError, IOError):
        pass
    return sorted(logs, key=lambda x: x["size"], reverse=True)


def _human_size(size):
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024:
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}PB"


def get_largest_logs(directory="/var/log", count=10):
    """Get the largest log files."""
    return get_log_files(directory)[:count]


def get_log_disk_usage(directory="/var/log"):
    """Get total disk usage of log directory."""
    total = 0
    count = 0
    try:
        for root, dirs, files in os.walk(directory):
            for f in files:
                try:
                    total += os.path.getsize(os.path.join(root, f))
                    count += 1
                except OSError:
                    pass
    except OSError:
        pass
    return {"total_bytes": total, "total_human": _human_size(total), "file_count": count}


def check_rotation_status():
    """Check logrotate configuration status."""
    status = {"configured": False, "config_file": None, "last_run": None}
    if os.path.exists("/etc/logrotate.conf"):
        status["configured"] = True
        status["config_file"] = "/etc/logrotate.conf"
    state_file = "/var/lib/logrotate/status"
    if not os.path.exists(state_file):
        state_file = "/var/lib/logrotate.status"
    if os.path.exists(state_file):
        try:
            mtime = os.path.getmtime(state_file)
            status["last_run"] = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
        except OSError:
            pass
    return status


def get_unrotated_logs(directory="/var/log", max_size_mb=100):
    """Find large unrotated log files."""
    threshold = max_size_mb * 1024 * 1024
    logs = get_log_files(directory, min_size=threshold)
    return [l for l in logs if not l["is_compressed"]]


def generate_report():
    """Generate comprehensive log statistics report."""
    usage = get_log_disk_usage()
    largest = get_largest_logs(count=15)
    rotation = check_rotation_status()
    unrotated = get_unrotated_logs()

    lines = []
    lines.append("=" * 60)
    lines.append("LOG FILE STATISTICS REPORT")
    lines.append("=" * 60)
    lines.append(f"\nTotal log disk usage: {usage['total_human']}")
    lines.append(f"Total log files: {usage['file_count']}")
    lines.append(f"Logrotate configured: {'Yes' if rotation['configured'] else 'No'}")
    if rotation["last_run"]:
        lines.append(f"Logrotate last run: {rotation['last_run']}")

    if largest:
        lines.append("\n--- Largest Log Files ---")
        for l in largest:
            flag = " [UNROTATED]" if not l["is_compressed"] and l["size"] > 100*1024*1024 else ""
            lines.append(f"  {l['size_human']:>10s}  {l['modified']}  {l['path']}{flag}")

    if unrotated:
        lines.append(f"\n--- Unrotated Large Files (>100MB) ---")
        for l in unrotated:
            lines.append(f"  [WARNING] {l['path']} ({l['size_human']})")

    lines.append("\n" + "=" * 60)
    lines.append("More tools: https://dargslan.com | pip install dargslan-toolkit")
    lines.append("=" * 60)
    return "\n".join(lines)
