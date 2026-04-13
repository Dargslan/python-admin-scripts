"""dargslan-socket-stats — Linux socket statistics analyzer."""

__version__ = "1.0.0"

import subprocess
import re
import json
import os
from datetime import datetime
from collections import defaultdict


def _run(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return r.stdout.strip()
    except Exception:
        return ""


def get_tcp_sockets():
    sockets = []
    out = _run("ss -tnp 2>/dev/null")
    for line in out.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 5:
            sock = {
                "state": parts[0],
                "recv_q": int(parts[1]) if parts[1].isdigit() else 0,
                "send_q": int(parts[2]) if parts[2].isdigit() else 0,
                "local": parts[3],
                "remote": parts[4],
            }
            if len(parts) > 5:
                pm = re.search(r'users:\(\("([^"]+)",pid=(\d+)', parts[5])
                if pm:
                    sock["process"] = pm.group(1)
                    sock["pid"] = int(pm.group(2))
            sockets.append(sock)
    return sockets


def get_udp_sockets():
    sockets = []
    out = _run("ss -unp 2>/dev/null")
    for line in out.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 5:
            sock = {
                "state": parts[0],
                "recv_q": int(parts[1]) if parts[1].isdigit() else 0,
                "send_q": int(parts[2]) if parts[2].isdigit() else 0,
                "local": parts[3],
                "remote": parts[4],
            }
            if len(parts) > 5:
                pm = re.search(r'users:\(\("([^"]+)",pid=(\d+)', parts[5])
                if pm:
                    sock["process"] = pm.group(1)
                    sock["pid"] = int(pm.group(2))
            sockets.append(sock)
    return sockets


def get_unix_sockets():
    sockets = []
    out = _run("ss -xlp 2>/dev/null")
    for line in out.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 5:
            sock = {
                "state": parts[0] if not parts[0].startswith("u_") else parts[1],
                "type": parts[0] if parts[0].startswith("u_") else "unix",
                "local": parts[4] if len(parts) > 4 else "",
            }
            sockets.append(sock)
    return sockets


def get_listening_sockets():
    sockets = []
    out = _run("ss -tlnp 2>/dev/null")
    for line in out.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 4:
            sock = {
                "state": "LISTEN",
                "local": parts[3],
                "protocol": "tcp",
            }
            if len(parts) > 5:
                pm = re.search(r'users:\(\("([^"]+)",pid=(\d+)', ' '.join(parts[5:]))
                if pm:
                    sock["process"] = pm.group(1)
                    sock["pid"] = int(pm.group(2))
            sockets.append(sock)
    out = _run("ss -ulnp 2>/dev/null")
    for line in out.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 4:
            sock = {
                "state": "UNCONN",
                "local": parts[3],
                "protocol": "udp",
            }
            if len(parts) > 5:
                pm = re.search(r'users:\(\("([^"]+)",pid=(\d+)', ' '.join(parts[5:]))
                if pm:
                    sock["process"] = pm.group(1)
                    sock["pid"] = int(pm.group(2))
            sockets.append(sock)
    return sockets


def get_state_summary():
    out = _run("ss -s 2>/dev/null")
    summary = {}
    for line in out.splitlines():
        if "TCP:" in line:
            m = re.search(r'TCP:\s+(\d+)', line)
            if m:
                summary["tcp_total"] = int(m.group(1))
            states = re.findall(r'(\w+)\s+(\d+)', line)
            for s, c in states:
                summary[f"tcp_{s.lower()}"] = int(c)
        elif "UDP:" in line:
            m = re.search(r'UDP:\s+(\d+)', line)
            if m:
                summary["udp_total"] = int(m.group(1))
    return summary


def get_connection_states():
    states = defaultdict(int)
    out = _run("ss -tn 2>/dev/null")
    for line in out.splitlines()[1:]:
        parts = line.split()
        if parts:
            states[parts[0]] += 1
    return dict(states)


def generate_report():
    tcp = get_tcp_sockets()
    udp = get_udp_sockets()
    listening = get_listening_sockets()
    conn_states = get_connection_states()
    summary = get_state_summary()
    issues = []

    time_wait = conn_states.get("TIME-WAIT", 0)
    close_wait = conn_states.get("CLOSE-WAIT", 0)
    if time_wait > 1000:
        issues.append({
            "severity": "warning",
            "message": f"High TIME-WAIT count: {time_wait}"
        })
    if close_wait > 100:
        issues.append({
            "severity": "warning",
            "message": f"High CLOSE-WAIT count: {close_wait} (possible connection leak)"
        })

    high_recv_q = [s for s in tcp if s["recv_q"] > 100]
    if high_recv_q:
        issues.append({
            "severity": "warning",
            "message": f"{len(high_recv_q)} sockets with high receive queue"
        })

    wildcard_listen = [s for s in listening if "0.0.0.0:" in s.get("local", "") or ":::"]
    return {
        "timestamp": datetime.now().isoformat(),
        "tcp_connections": len(tcp),
        "udp_sockets": len(udp),
        "listening": len(listening),
        "connection_states": conn_states,
        "state_summary": summary,
        "listening_sockets": listening,
        "issues": issues,
        "issues_count": len(issues),
    }


def audit():
    report = generate_report()
    return report["issues"]
