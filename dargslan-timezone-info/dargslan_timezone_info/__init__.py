"""dargslan-timezone-info -- Timezone and NTP checker.
Verify timezone, check NTP sync status, detect clock drift, and list timezones.
Part of the Dargslan Linux Sysadmin Toolkit: https://dargslan.com
"""
__version__ = "1.0.0"
import subprocess, os, time
from datetime import datetime

def get_timezone():
    info = {"timezone": "unknown", "utc_offset": "", "local_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    try:
        r = subprocess.run(["timedatectl", "show", "--property=Timezone", "--value"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0: info["timezone"] = r.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        if os.path.exists("/etc/timezone"):
            try:
                with open("/etc/timezone") as f: info["timezone"] = f.read().strip()
            except OSError: pass
    try: info["utc_offset"] = time.strftime("%z")
    except: pass
    return info

def check_ntp_status():
    status = {"synced": False, "service": "unknown", "server": "", "offset": "", "details": ""}
    try:
        r = subprocess.run(["timedatectl", "show"], capture_output=True, text=True, timeout=10)
        if r.returncode == 0:
            for line in r.stdout.split("\n"):
                if "NTPSynchronized" in line: status["synced"] = "yes" in line.lower()
                if "NTP" in line and "=" in line: status["details"] += line.strip() + "; "
    except (subprocess.SubprocessError, FileNotFoundError): pass
    for svc in ["chronyd", "ntpd", "systemd-timesyncd"]:
        try:
            r = subprocess.run(["systemctl", "is-active", svc], capture_output=True, text=True, timeout=5)
            if r.stdout.strip() == "active": status["service"] = svc; break
        except (subprocess.SubprocessError, FileNotFoundError): pass
    if status["service"] == "chronyd":
        try:
            r = subprocess.run(["chronyc", "tracking"], capture_output=True, text=True, timeout=10)
            for line in r.stdout.split("\n"):
                if "Reference ID" in line: status["server"] = line.split(":")[-1].strip()
                if "System time" in line: status["offset"] = line.split(":")[-1].strip()
        except (subprocess.SubprocessError, FileNotFoundError): pass
    return status

def get_hardware_clock():
    try:
        r = subprocess.run(["hwclock", "--show"], capture_output=True, text=True, timeout=10)
        if r.returncode == 0: return r.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError): pass
    return None

def generate_report():
    tz = get_timezone()
    ntp = check_ntp_status()
    hw = get_hardware_clock()
    lines = ["="*60, "TIMEZONE & NTP STATUS REPORT", "="*60]
    lines.append(f"\nTimezone: {tz['timezone']}")
    lines.append(f"UTC Offset: {tz['utc_offset']}")
    lines.append(f"Local Time: {tz['local_time']}")
    lines.append(f"UTC Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
    if hw: lines.append(f"Hardware Clock: {hw}")
    lines.append(f"\n--- NTP Status ---")
    lines.append(f"  Synchronized: {'Yes' if ntp['synced'] else 'No'}")
    lines.append(f"  Service: {ntp['service']}")
    if ntp["server"]: lines.append(f"  Server: {ntp['server']}")
    if ntp["offset"]: lines.append(f"  Offset: {ntp['offset']}")
    if not ntp["synced"]: lines.append("\n  [WARNING] Time is NOT synchronized with NTP!")
    lines += ["\n"+"="*60, "More tools: https://dargslan.com | pip install dargslan-toolkit", "="*60]
    return "\n".join(lines)
