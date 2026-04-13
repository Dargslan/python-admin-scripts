"""dargslan-interface-monitor -- Network interface monitor.
Link status, speed, errors, IP addresses, and traffic statistics.
Part of the Dargslan Linux Sysadmin Toolkit: https://dargslan.com
"""
__version__ = "1.0.0"
import subprocess, os, socket

def get_interfaces():
    ifaces = []
    try:
        for name in os.listdir("/sys/class/net"):
            info = {"name": name, "state": "unknown", "mac": "", "mtu": "", "speed": "", "ips": []}
            try:
                with open(f"/sys/class/net/{name}/operstate") as f: info["state"] = f.read().strip()
            except OSError: pass
            try:
                with open(f"/sys/class/net/{name}/address") as f: info["mac"] = f.read().strip()
            except OSError: pass
            try:
                with open(f"/sys/class/net/{name}/mtu") as f: info["mtu"] = f.read().strip()
            except OSError: pass
            try:
                with open(f"/sys/class/net/{name}/speed") as f: info["speed"] = f.read().strip() + " Mbps"
            except OSError: pass
            try:
                r = subprocess.run(["ip", "-o", "addr", "show", name], capture_output=True, text=True, timeout=5)
                for line in r.stdout.strip().split("\n"):
                    if "inet " in line:
                        ip = line.split("inet ")[1].split()[0]
                        info["ips"].append(ip)
                    elif "inet6" in line:
                        ip = line.split("inet6 ")[1].split()[0]
                        if not ip.startswith("fe80"): info["ips"].append(ip)
            except (subprocess.SubprocessError, OSError): pass
            ifaces.append(info)
    except OSError: pass
    return ifaces

def get_traffic_stats():
    stats = []
    try:
        with open("/proc/net/dev") as f:
            for line in f:
                if ":" in line:
                    parts = line.split(":")
                    name = parts[0].strip()
                    vals = parts[1].split()
                    if len(vals) >= 10:
                        rx_bytes = int(vals[0]); tx_bytes = int(vals[8])
                        rx_errs = int(vals[2]); tx_errs = int(vals[10])
                        stats.append({"name": name, "rx_bytes": rx_bytes, "tx_bytes": tx_bytes, "rx_errors": rx_errs, "tx_errors": tx_errs,
                                      "rx_human": _human_size(rx_bytes), "tx_human": _human_size(tx_bytes)})
    except OSError: pass
    return stats

def _human_size(s):
    for u in ("B","KB","MB","GB","TB"):
        if s < 1024: return f"{s:.1f}{u}"
        s /= 1024
    return f"{s:.1f}PB"

def check_errors():
    return [s for s in get_traffic_stats() if s["rx_errors"] > 0 or s["tx_errors"] > 0]

def generate_report():
    ifaces = get_interfaces()
    stats = get_traffic_stats()
    errors = check_errors()
    lines = ["="*60, "NETWORK INTERFACE REPORT", "="*60]
    lines.append(f"\nInterfaces: {len(ifaces)}")
    up = [i for i in ifaces if i["state"] == "up"]
    lines.append(f"Active (up): {len(up)}")
    if errors: lines.append(f"Interfaces with errors: {len(errors)}")
    for i in ifaces:
        state_icon = "[UP]" if i["state"]=="up" else "[DN]"
        lines.append(f"\n  {state_icon} {i['name']}")
        lines.append(f"      MAC: {i['mac']}  MTU: {i['mtu']}  Speed: {i['speed'] or 'N/A'}")
        if i["ips"]: lines.append(f"      IPs: {', '.join(i['ips'])}")
        st = next((s for s in stats if s["name"]==i["name"]), None)
        if st: lines.append(f"      RX: {st['rx_human']}  TX: {st['tx_human']}  Errors: {st['rx_errors']}rx/{st['tx_errors']}tx")
    lines += ["\n"+"="*60, "More tools: https://dargslan.com | pip install dargslan-toolkit", "="*60]
    return "\n".join(lines)
