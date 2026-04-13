"""dargslan-network-latency — Network latency tester."""

__version__ = "1.0.0"

import subprocess
import re
import json
import time
import socket
from datetime import datetime
from statistics import mean, stdev


def _run(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return r.stdout.strip()
    except Exception:
        return ""


def ping_host(host, count=10):
    out = _run(f"ping -c {count} -W 3 {host} 2>/dev/null")
    if not out:
        return {"host": host, "reachable": False, "error": "No response"}
    times = [float(m) for m in re.findall(r'time=(\d+\.?\d*)', out)]
    if not times:
        return {"host": host, "reachable": False, "error": "No timing data"}
    loss_m = re.search(r'(\d+)% packet loss', out)
    rtt_m = re.search(r'rtt min/avg/max/mdev = ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)', out)
    result = {
        "host": host,
        "reachable": True,
        "packets_sent": count,
        "packet_loss": int(loss_m.group(1)) if loss_m else 0,
        "min_ms": float(rtt_m.group(1)) if rtt_m else min(times),
        "avg_ms": float(rtt_m.group(2)) if rtt_m else mean(times),
        "max_ms": float(rtt_m.group(3)) if rtt_m else max(times),
        "mdev_ms": float(rtt_m.group(4)) if rtt_m else (stdev(times) if len(times) > 1 else 0),
        "jitter_ms": round(stdev(times), 2) if len(times) > 1 else 0,
        "samples": times,
    }
    return result


def tcp_latency(host, port=443, count=5):
    times = []
    for _ in range(count):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            start = time.time()
            s.connect((host, port))
            elapsed = (time.time() - start) * 1000
            times.append(round(elapsed, 2))
            s.close()
        except Exception:
            pass
    if not times:
        return {"host": host, "port": port, "reachable": False}
    return {
        "host": host,
        "port": port,
        "reachable": True,
        "min_ms": min(times),
        "avg_ms": round(mean(times), 2),
        "max_ms": max(times),
        "jitter_ms": round(stdev(times), 2) if len(times) > 1 else 0,
        "samples": times,
    }


def traceroute(host, max_hops=20):
    hops = []
    out = _run(f"traceroute -n -m {max_hops} -w 2 {host} 2>/dev/null")
    if not out:
        out = _run(f"tracepath -n {host} 2>/dev/null")
    for line in out.splitlines()[1:]:
        m = re.match(r'\s*(\d+)\s+([\d.]+|[\*])\s+([\d.]+\s*ms|\*)', line)
        if m:
            hop_num = int(m.group(1))
            ip = m.group(2) if m.group(2) != "*" else None
            times = [float(t) for t in re.findall(r'([\d.]+)\s*ms', line)]
            hops.append({
                "hop": hop_num,
                "ip": ip,
                "times_ms": times,
                "avg_ms": round(mean(times), 2) if times else None,
            })
    return hops


def compare_hosts(hosts, count=5):
    results = []
    for host in hosts:
        r = ping_host(host, count)
        results.append(r)
    results.sort(key=lambda x: x.get("avg_ms", 9999))
    return results


def generate_report(hosts=None):
    if hosts is None:
        hosts = ["8.8.8.8", "1.1.1.1", "9.9.9.9"]
    results = []
    issues = []
    for host in hosts:
        r = ping_host(host, 5)
        results.append(r)
        if not r.get("reachable"):
            issues.append({"severity": "critical", "message": f"Host unreachable: {host}"})
        elif r.get("packet_loss", 0) > 0:
            issues.append({"severity": "warning", "message": f"Packet loss to {host}: {r['packet_loss']}%"})
        elif r.get("avg_ms", 0) > 100:
            issues.append({"severity": "warning", "message": f"High latency to {host}: {r['avg_ms']}ms"})
        if r.get("jitter_ms", 0) > 20:
            issues.append({"severity": "warning", "message": f"High jitter to {host}: {r['jitter_ms']}ms"})
    return {
        "timestamp": datetime.now().isoformat(),
        "hosts_tested": len(results),
        "results": results,
        "issues": issues,
        "issues_count": len(issues),
    }


def audit():
    return generate_report()["issues"]
