"""dargslan-kernel-module -- Kernel module manager.
List loaded modules, check dependencies, find unused, and module info.
Part of the Dargslan Linux Sysadmin Toolkit: https://dargslan.com
"""
__version__ = "1.0.0"
import subprocess, os

def get_loaded_modules():
    modules = []
    try:
        with open("/proc/modules") as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 3:
                    modules.append({"name": parts[0], "size": int(parts[1]), "used_by": int(parts[2]), "deps": parts[3].strip(",") if len(parts)>3 and parts[3]!="-" else ""})
    except OSError: pass
    return sorted(modules, key=lambda x: x["size"], reverse=True)

def get_module_info(module_name):
    try:
        r = subprocess.run(["modinfo", module_name], capture_output=True, text=True, timeout=10)
        if r.returncode == 0:
            info = {}
            for line in r.stdout.split("\n"):
                if ":" in line:
                    key, val = line.split(":", 1)
                    info[key.strip()] = val.strip()
            return info
    except (subprocess.SubprocessError, FileNotFoundError): pass
    return None

def find_unused_modules():
    return [m for m in get_loaded_modules() if m["used_by"] == 0 and not m["deps"]]

def get_blacklisted():
    blacklisted = []
    for d in ["/etc/modprobe.d"]:
        if os.path.isdir(d):
            for f in os.listdir(d):
                try:
                    with open(os.path.join(d, f)) as fh:
                        for line in fh:
                            if line.strip().startswith("blacklist"):
                                mod = line.strip().split()[-1]
                                blacklisted.append({"module": mod, "source": f})
                except OSError: pass
    return blacklisted

def _human_size(s):
    for u in ("B","KB","MB","GB"):
        if s < 1024: return f"{s:.0f}{u}"
        s /= 1024
    return f"{s:.0f}TB"

def generate_report():
    modules = get_loaded_modules()
    unused = find_unused_modules()
    blacklisted = get_blacklisted()
    total_size = sum(m["size"] for m in modules)
    lines = ["="*60, "KERNEL MODULE REPORT", "="*60]
    lines.append(f"\nLoaded modules: {len(modules)}")
    lines.append(f"Total module memory: {_human_size(total_size)}")
    lines.append(f"Unused modules: {len(unused)}")
    lines.append(f"Blacklisted: {len(blacklisted)}")
    lines.append("\n--- Largest Modules ---")
    for m in modules[:15]: lines.append(f"  {m['name']:30s} {_human_size(m['size']):>8s}  used_by: {m['used_by']}")
    if unused:
        lines.append(f"\n--- Unused Modules ({len(unused)}) ---")
        for m in unused[:10]: lines.append(f"  {m['name']:30s} {_human_size(m['size']):>8s}")
    if blacklisted:
        lines.append(f"\n--- Blacklisted Modules ---")
        for b in blacklisted: lines.append(f"  {b['module']:30s} ({b['source']})")
    lines += ["\n"+"="*60, "More tools: https://dargslan.com | pip install dargslan-toolkit", "="*60]
    return "\n".join(lines)
