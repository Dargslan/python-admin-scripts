"""dargslan-hostname-info — Hostname and domain resolver.

FQDN lookup, reverse DNS, domain info, and network identity check.
Part of the Dargslan Linux Sysadmin Toolkit: https://dargslan.com
"""

__version__ = "1.0.0"

import socket
import subprocess
import os


def get_hostname():
    """Get system hostname."""
    return socket.gethostname()


def get_fqdn():
    """Get fully qualified domain name."""
    return socket.getfqdn()


def get_all_ips():
    """Get all IP addresses for the hostname."""
    ips = []
    hostname = get_hostname()
    try:
        results = socket.getaddrinfo(hostname, None)
        seen = set()
        for r in results:
            ip = r[4][0]
            if ip not in seen:
                seen.add(ip)
                ips.append({"ip": ip, "family": "IPv6" if r[0] == socket.AF_INET6 else "IPv4"})
    except socket.gaierror:
        pass
    return ips


def reverse_dns(ip):
    """Perform reverse DNS lookup."""
    try:
        result = socket.gethostbyaddr(ip)
        return {"hostname": result[0], "aliases": result[1], "addresses": result[2]}
    except (socket.herror, socket.gaierror):
        return None


def get_domain_info():
    """Get domain-related system information."""
    info = {
        "hostname": get_hostname(),
        "fqdn": get_fqdn(),
        "domain": None,
        "ips": get_all_ips(),
    }
    fqdn = info["fqdn"]
    if "." in fqdn:
        info["domain"] = ".".join(fqdn.split(".")[1:])
    try:
        result = subprocess.run(["hostnamectl", "--json=short"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            import json
            data = json.loads(result.stdout)
            info["static_hostname"] = data.get("StaticHostname", "")
            info["icon_name"] = data.get("IconName", "")
            info["chassis"] = data.get("Chassis", "")
            info["os"] = data.get("OperatingSystemPrettyName", "")
            info["kernel"] = data.get("KernelRelease", "")
    except (subprocess.SubprocessError, FileNotFoundError, Exception):
        try:
            result = subprocess.run(["hostnamectl"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if ":" in line:
                        key, val = line.split(":", 1)
                        key = key.strip().lower().replace(" ", "_")
                        info[key] = val.strip()
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
    return info


def resolve_hostname(hostname):
    """Resolve a hostname to IP addresses."""
    results = []
    try:
        for info in socket.getaddrinfo(hostname, None):
            ip = info[4][0]
            if ip not in [r["ip"] for r in results]:
                results.append({"ip": ip, "family": "IPv6" if info[0] == socket.AF_INET6 else "IPv4"})
    except socket.gaierror:
        pass
    return results


def get_hosts_file():
    """Parse /etc/hosts entries."""
    entries = []
    try:
        with open("/etc/hosts", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    parts = line.split()
                    if len(parts) >= 2:
                        entries.append({"ip": parts[0], "hostnames": parts[1:]})
    except (IOError, OSError):
        pass
    return entries


def generate_report():
    """Generate comprehensive hostname/domain report."""
    info = get_domain_info()
    hosts = get_hosts_file()

    lines = []
    lines.append("=" * 60)
    lines.append("HOSTNAME & DOMAIN REPORT")
    lines.append("=" * 60)
    lines.append(f"\nHostname: {info['hostname']}")
    lines.append(f"FQDN: {info['fqdn']}")
    if info.get("domain"):
        lines.append(f"Domain: {info['domain']}")
    if info.get("os"):
        lines.append(f"OS: {info['os']}")
    if info.get("kernel"):
        lines.append(f"Kernel: {info['kernel']}")

    if info["ips"]:
        lines.append("\n--- IP Addresses ---")
        for ip in info["ips"]:
            rev = reverse_dns(ip["ip"])
            rev_str = f" -> {rev['hostname']}" if rev else ""
            lines.append(f"  {ip['family']:4s} {ip['ip']}{rev_str}")

    if hosts:
        lines.append("\n--- /etc/hosts Entries ---")
        for h in hosts:
            lines.append(f"  {h['ip']:20s} {' '.join(h['hostnames'])}")

    lines.append("\n" + "=" * 60)
    lines.append("More tools: https://dargslan.com | pip install dargslan-toolkit")
    lines.append("=" * 60)
    return "\n".join(lines)
