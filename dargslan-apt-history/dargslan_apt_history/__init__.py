"""dargslan-apt-history -- Package install history analyzer.
Track installations, upgrades, removals, and security updates.
Part of the Dargslan Linux Sysadmin Toolkit: https://dargslan.com
"""
__version__ = "1.0.0"
import os, subprocess, gzip
from datetime import datetime

APT_LOG = "/var/log/apt/history.log"
DPKG_LOG = "/var/log/dpkg.log"

def parse_apt_history(max_entries=50):
    entries = []
    logs = []
    if os.path.exists(APT_LOG): logs.append(APT_LOG)
    for gz in sorted([f for f in os.listdir("/var/log/apt/") if f.startswith("history.log.") and f.endswith(".gz")]) if os.path.isdir("/var/log/apt/") else []:
        logs.append(os.path.join("/var/log/apt/", gz))
    for logfile in logs:
        try:
            if logfile.endswith(".gz"):
                with gzip.open(logfile, "rt") as f: content = f.read()
            else:
                with open(logfile) as f: content = f.read()
            current = {}
            for line in content.split("\n"):
                if line.startswith("Start-Date:"):
                    current = {"date": line.split(":", 1)[1].strip(), "action": "", "packages": ""}
                elif line.startswith("Commandline:"): current["action"] = line.split(":", 1)[1].strip()
                elif line.startswith("Install:"): current["packages"] = line.split(":", 1)[1].strip()[:200]; current["type"] = "install"
                elif line.startswith("Upgrade:"): current["packages"] = line.split(":", 1)[1].strip()[:200]; current["type"] = "upgrade"
                elif line.startswith("Remove:"): current["packages"] = line.split(":", 1)[1].strip()[:200]; current["type"] = "remove"
                elif line.startswith("Purge:"): current["packages"] = line.split(":", 1)[1].strip()[:200]; current["type"] = "purge"
                elif line.startswith("End-Date:"):
                    if current: entries.append(current)
                    current = {}
        except (IOError, OSError): pass
    return entries[-max_entries:]

def get_dpkg_recent(count=20):
    entries = []
    try:
        with open(DPKG_LOG) as f:
            for line in f:
                if " install " in line or " upgrade " in line or " remove " in line:
                    entries.append(line.strip())
    except (IOError, OSError): pass
    return entries[-count:]

def get_installed_count():
    try:
        r = subprocess.run(["dpkg", "--get-selections"], capture_output=True, text=True, timeout=15)
        return len([l for l in r.stdout.split("\n") if "install" in l])
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    try:
        r = subprocess.run(["rpm", "-qa"], capture_output=True, text=True, timeout=15)
        return len(r.stdout.strip().split("\n"))
    except (subprocess.SubprocessError, FileNotFoundError): pass
    return 0

def check_security_updates():
    updates = []
    try:
        r = subprocess.run(["apt", "list", "--upgradable"], capture_output=True, text=True, timeout=30, env={**os.environ, "DEBIAN_FRONTEND": "noninteractive"})
        for line in r.stdout.split("\n"):
            if "security" in line.lower(): updates.append(line.strip())
    except (subprocess.SubprocessError, FileNotFoundError): pass
    return updates

def generate_report():
    history = parse_apt_history(20)
    dpkg = get_dpkg_recent(15)
    count = get_installed_count()
    security = check_security_updates()
    lines = ["="*60, "PACKAGE INSTALL HISTORY REPORT", "="*60]
    lines.append(f"\nInstalled packages: {count}")
    lines.append(f"Pending security updates: {len(security)}")
    if history:
        lines.append(f"\n--- Recent APT History ({len(history)} entries) ---")
        for h in history[-15:]:
            t = h.get("type", "?")
            pkgs = h.get("packages", "")[:80]
            lines.append(f"  {h.get('date',''):20s} [{t:7s}] {pkgs}")
    if security:
        lines.append(f"\n--- Pending Security Updates ---")
        for s in security[:10]: lines.append(f"  [SEC] {s[:100]}")
    if dpkg:
        lines.append(f"\n--- Recent dpkg Activity ---")
        for d in dpkg[-10:]: lines.append(f"  {d[:100]}")
    lines += ["\n"+"="*60, "More tools: https://dargslan.com | pip install dargslan-toolkit", "="*60]
    return "\n".join(lines)
