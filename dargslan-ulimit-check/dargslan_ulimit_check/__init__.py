"""dargslan-ulimit-check -- Ulimit and resource limits checker.
Audit open files, process limits, memory limits, and PAM limits.
Part of the Dargslan Linux Sysadmin Toolkit: https://dargslan.com
"""
__version__ = "1.0.0"
import subprocess, os

def get_current_limits():
    limits = {}
    try:
        r = subprocess.run(["bash", "-c", "ulimit -a"], capture_output=True, text=True, timeout=10)
        for line in r.stdout.strip().split("\n"):
            if ")" in line:
                parts = line.rsplit(")", 1)
                name = parts[0].strip() + ")"
                value = parts[1].strip() if len(parts) > 1 else ""
                limits[name] = value
    except (subprocess.SubprocessError, OSError): pass
    return limits

def get_process_limits(pid=None):
    if pid is None: pid = os.getpid()
    limits = []
    path = f"/proc/{pid}/limits"
    try:
        with open(path) as f:
            for line in f:
                if line.startswith("Max") or line.startswith("Limit"):
                    limits.append(line.strip())
    except (IOError, OSError): pass
    return limits

def get_system_limits():
    params = {"fs.file-max": None, "fs.nr_open": None, "kernel.pid_max": None, "kernel.threads-max": None, "vm.max_map_count": None}
    for p in params:
        try:
            r = subprocess.run(["sysctl", "-n", p], capture_output=True, text=True, timeout=5)
            if r.returncode == 0: params[p] = r.stdout.strip()
        except (subprocess.SubprocessError, FileNotFoundError): pass
    return params

def get_open_files_count():
    try:
        with open("/proc/sys/fs/file-nr") as f:
            parts = f.read().strip().split()
            return {"allocated": int(parts[0]), "free": int(parts[1]) if len(parts)>1 else 0, "max": int(parts[2]) if len(parts)>2 else 0}
    except (IOError, OSError, ValueError): pass
    return None

def check_limits_conf():
    entries = []
    for path in ["/etc/security/limits.conf", "/etc/security/limits.d/"]:
        if os.path.isfile(path):
            try:
                with open(path) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"): entries.append({"source": path, "rule": line})
            except OSError: pass
        elif os.path.isdir(path):
            for fname in sorted(os.listdir(path)):
                fpath = os.path.join(path, fname)
                try:
                    with open(fpath) as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith("#"): entries.append({"source": fpath, "rule": line})
                except OSError: pass
    return entries

def generate_report():
    current = get_current_limits()
    sys_limits = get_system_limits()
    open_files = get_open_files_count()
    limits_conf = check_limits_conf()
    lines = ["="*60, "RESOURCE LIMITS REPORT", "="*60]
    if open_files:
        pct = round(open_files["allocated"]/open_files["max"]*100, 1) if open_files["max"]>0 else 0
        lines.append(f"\nOpen files: {open_files['allocated']}/{open_files['max']} ({pct}% used)")
    lines.append("\n--- System Limits ---")
    for k, v in sys_limits.items():
        if v: lines.append(f"  {k:25s} = {v}")
    if current:
        lines.append("\n--- Current Shell Limits ---")
        for k, v in list(current.items())[:15]: lines.append(f"  {k:45s} {v}")
    if limits_conf:
        lines.append(f"\n--- limits.conf Rules ({len(limits_conf)}) ---")
        for e in limits_conf[:10]: lines.append(f"  {e['rule']}")
    lines += ["\n"+"="*60, "More tools: https://dargslan.com | pip install dargslan-toolkit", "="*60]
    return "\n".join(lines)
