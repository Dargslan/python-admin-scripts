"""dargslan-crontab-backup -- Crontab backup manager.
Export, restore, and diff user crontabs with timestamped backups.
Part of the Dargslan Linux Sysadmin Toolkit: https://dargslan.com
"""
__version__ = "1.0.0"
import subprocess, os, pwd
from datetime import datetime

BACKUP_DIR = "/var/backups/crontabs"

def get_all_users():
    users = []
    try:
        for p in pwd.getpwall():
            if p.pw_uid >= 1000 or p.pw_name == "root":
                users.append(p.pw_name)
    except: pass
    return sorted(users)

def get_user_crontab(user="root"):
    try:
        r = subprocess.run(["crontab", "-l", "-u", user], capture_output=True, text=True, timeout=10)
        if r.returncode == 0: return r.stdout
    except (subprocess.SubprocessError, FileNotFoundError): pass
    return None

def export_all_crontabs(backup_dir=None):
    if not backup_dir: backup_dir = BACKUP_DIR
    os.makedirs(backup_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    exported = []
    for user in get_all_users():
        crontab = get_user_crontab(user)
        if crontab and crontab.strip():
            fname = f"{user}_{ts}.crontab"
            path = os.path.join(backup_dir, fname)
            try:
                with open(path, "w") as f: f.write(crontab)
                exported.append({"user": user, "file": path, "lines": len(crontab.strip().split("\n"))})
            except OSError: pass
    return exported

def list_backups(backup_dir=None):
    if not backup_dir: backup_dir = BACKUP_DIR
    backups = []
    if os.path.isdir(backup_dir):
        for f in sorted(os.listdir(backup_dir)):
            if f.endswith(".crontab"):
                path = os.path.join(backup_dir, f)
                backups.append({"file": f, "path": path, "size": os.path.getsize(path), "modified": datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d %H:%M")})
    return backups

def get_system_cron_jobs():
    jobs = []
    for d in ["/etc/cron.d", "/etc/cron.daily", "/etc/cron.hourly", "/etc/cron.weekly", "/etc/cron.monthly"]:
        if os.path.isdir(d):
            for f in os.listdir(d):
                path = os.path.join(d, f)
                if os.path.isfile(path): jobs.append({"directory": d, "file": f, "path": path})
    return jobs

def generate_report():
    users = get_all_users()
    system_jobs = get_system_cron_jobs()
    backups = list_backups()
    lines = ["="*60, "CRONTAB BACKUP REPORT", "="*60]
    lines.append(f"\nSystem users with crontabs:")
    for u in users:
        ct = get_user_crontab(u)
        if ct and ct.strip():
            count = len([l for l in ct.strip().split("\n") if l.strip() and not l.startswith("#")])
            lines.append(f"  {u:20s} {count} active jobs")
    if system_jobs:
        lines.append(f"\n--- System Cron Jobs ({len(system_jobs)}) ---")
        for j in system_jobs: lines.append(f"  {j['directory']:25s} {j['file']}")
    if backups:
        lines.append(f"\n--- Saved Backups ({len(backups)}) ---")
        for b in backups[-10:]: lines.append(f"  {b['modified']}  {b['file']}")
    lines += ["\n"+"="*60, "More tools: https://dargslan.com | pip install dargslan-toolkit", "="*60]
    return "\n".join(lines)
