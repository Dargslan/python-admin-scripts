"""dargslan-raid-monitor — Linux RAID array health checker."""

__version__ = "1.0.0"

import subprocess
import re
import json
import os
from datetime import datetime


def _run(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return r.stdout.strip()
    except Exception:
        return ""


def get_mdadm_detail(device):
    out = _run(f"sudo mdadm --detail {device} 2>/dev/null")
    if not out:
        out = _run(f"mdadm --detail {device} 2>/dev/null")
    info = {}
    for line in out.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            info[k.strip()] = v.strip()
    return info


def get_arrays():
    arrays = []
    mdstat = _run("cat /proc/mdstat 2>/dev/null")
    if not mdstat:
        return arrays
    for line in mdstat.splitlines():
        m = re.match(r'^(md\d+)\s*:\s*(active|inactive)\s+(\w+)\s+(.*)', line)
        if m:
            name = m.group(1)
            state = m.group(2)
            level = m.group(3)
            devices_str = m.group(4)
            devs = re.findall(r'(\w+)\[\d+\](?:\((\w)\))?', devices_str)
            device_list = []
            for d, flag in devs:
                status = "active"
                if flag == "S":
                    status = "spare"
                elif flag == "F":
                    status = "faulty"
                device_list.append({"device": d, "status": status})
            arrays.append({
                "name": f"/dev/{name}",
                "state": state,
                "level": level,
                "devices": device_list,
            })
    return arrays


def get_rebuild_progress():
    mdstat = _run("cat /proc/mdstat 2>/dev/null")
    progress = {}
    current_md = None
    for line in mdstat.splitlines():
        m = re.match(r'^(md\d+)', line)
        if m:
            current_md = m.group(1)
        if "recovery" in line or "resync" in line or "reshape" in line:
            pm = re.search(r'(\d+\.\d+)%', line)
            if pm and current_md:
                progress[f"/dev/{current_md}"] = {
                    "percentage": float(pm.group(1)),
                    "operation": "rebuild"
                }
                em = re.search(r'finish=(\S+)', line)
                if em:
                    progress[f"/dev/{current_md}"]["eta"] = em.group(1)
    return progress


def get_smart_health(device):
    out = _run(f"smartctl -H /dev/{device} 2>/dev/null")
    if "PASSED" in out:
        return "PASSED"
    elif "FAILED" in out:
        return "FAILED"
    return "unknown"


def generate_report():
    arrays = get_arrays()
    rebuild = get_rebuild_progress()
    issues = []
    report_arrays = []

    for arr in arrays:
        detail = get_mdadm_detail(arr["name"])
        arr_info = {
            "device": arr["name"],
            "state": arr["state"],
            "level": arr["level"],
            "devices": arr["devices"],
            "detail": detail,
        }
        if arr["name"] in rebuild:
            arr_info["rebuild"] = rebuild[arr["name"]]
            issues.append({
                "severity": "warning",
                "message": f"{arr['name']} is rebuilding ({rebuild[arr['name']]['percentage']}%)"
            })
        if arr["state"] == "inactive":
            issues.append({
                "severity": "critical",
                "message": f"{arr['name']} is INACTIVE"
            })
        degraded = detail.get("State", "")
        if "degraded" in degraded.lower():
            issues.append({
                "severity": "critical",
                "message": f"{arr['name']} is DEGRADED"
            })
        faulty = [d for d in arr["devices"] if d["status"] == "faulty"]
        for f in faulty:
            issues.append({
                "severity": "critical",
                "message": f"Faulty disk {f['device']} in {arr['name']}"
            })
        report_arrays.append(arr_info)

    return {
        "timestamp": datetime.now().isoformat(),
        "total_arrays": len(report_arrays),
        "arrays": report_arrays,
        "rebuild_progress": rebuild,
        "issues": issues,
        "issues_count": len(issues),
    }


def audit():
    report = generate_report()
    return report["issues"]
