"""dargslan-motd-manager -- MOTD and login banner manager.
System info display, security warnings, and dynamic MOTD generation.
Part of the Dargslan Linux Sysadmin Toolkit: https://dargslan.com
"""
__version__ = "1.0.0"
import subprocess, os, socket, platform
from datetime import datetime

def get_current_motd():
    for path in ["/etc/motd", "/run/motd.dynamic"]:
        try:
            with open(path) as f:
                content = f.read()
                if content.strip(): return {"source": path, "content": content}
        except (IOError, OSError): pass
    return None

def get_issue():
    for path in ["/etc/issue", "/etc/issue.net"]:
        try:
            with open(path) as f: return {"source": path, "content": f.read().strip()}
        except (IOError, OSError): pass
    return None

def get_motd_scripts():
    scripts = []
    motd_dir = "/etc/update-motd.d"
    if os.path.isdir(motd_dir):
        for f in sorted(os.listdir(motd_dir)):
            path = os.path.join(motd_dir, f)
            executable = os.access(path, os.X_OK)
            scripts.append({"name": f, "path": path, "executable": executable, "size": os.path.getsize(path)})
    return scripts

def generate_system_info():
    info = []
    info.append(f"Hostname: {socket.gethostname()}")
    info.append(f"OS: {platform.platform()}")
    info.append(f"Kernel: {platform.release()}")
    info.append(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        with open("/proc/uptime") as f:
            secs = float(f.read().split()[0])
            days = int(secs // 86400); hours = int((secs % 86400) // 3600)
            info.append(f"Uptime: {days}d {hours}h")
    except: pass
    try:
        with open("/proc/loadavg") as f:
            load = f.read().split()[:3]
            info.append(f"Load: {' '.join(load)}")
    except: pass
    try:
        r = subprocess.run(["free", "-h"], capture_output=True, text=True, timeout=5)
        for line in r.stdout.split("\n"):
            if line.startswith("Mem:"):
                parts = line.split()
                info.append(f"Memory: {parts[2]}/{parts[1]} used")
    except: pass
    try:
        r = subprocess.run(["df", "-h", "/"], capture_output=True, text=True, timeout=5)
        lines = r.stdout.strip().split("\n")
        if len(lines) > 1:
            parts = lines[1].split()
            info.append(f"Disk /: {parts[2]}/{parts[1]} ({parts[4]})")
    except: pass
    return info

def generate_banner():
    lines = ["=" * 50]
    lines.append(f"  Welcome to {socket.gethostname()}")
    lines.append("=" * 50)
    for info in generate_system_info():
        lines.append(f"  {info}")
    lines.append("=" * 50)
    return "\n".join(lines)

def generate_report():
    motd = get_current_motd()
    issue = get_issue()
    scripts = get_motd_scripts()
    lines = ["="*60, "MOTD & LOGIN BANNER REPORT", "="*60]
    if motd:
        lines.append(f"\n--- Current MOTD ({motd['source']}) ---")
        lines.append(motd["content"][:500])
    else: lines.append("\nNo MOTD configured.")
    if issue:
        lines.append(f"\n--- Login Issue ({issue['source']}) ---")
        lines.append(issue["content"][:200])
    if scripts:
        lines.append(f"\n--- Dynamic MOTD Scripts ({len(scripts)}) ---")
        for s in scripts:
            exec_icon = "[X]" if s["executable"] else "[ ]"
            lines.append(f"  {exec_icon} {s['name']}")
    lines.append("\n--- Generated System Banner ---")
    lines.append(generate_banner())
    lines += ["\n"+"="*60, "More tools: https://dargslan.com | pip install dargslan-toolkit", "="*60]
    return "\n".join(lines)
