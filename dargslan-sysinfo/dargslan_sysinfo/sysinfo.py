"""
Linux System Information collector.

Part of dargslan-sysinfo — https://dargslan.com
Free Linux Cheat Sheets: https://dargslan.com/cheat-sheets
"""

import os
import platform
import subprocess
import re
from datetime import timedelta


class SystemInfo:
    """Collect and display Linux system information."""

    def cpu_info(self):
        """Get CPU information."""
        info = {
            "model": "Unknown",
            "cores": 0,
            "threads": 0,
            "load_avg": [0.0, 0.0, 0.0],
            "usage_percent": 0.0,
        }

        try:
            with open("/proc/cpuinfo", "r") as f:
                content = f.read()
                models = re.findall(r"model name\s*:\s*(.*)", content)
                if models:
                    info["model"] = models[0].strip()
                processors = re.findall(r"^processor\s*:", content, re.M)
                info["threads"] = len(processors)
                cores = set(re.findall(r"core id\s*:\s*(\d+)", content))
                info["cores"] = len(cores) if cores else info["threads"]
        except (FileNotFoundError, PermissionError):
            pass

        try:
            load = os.getloadavg()
            info["load_avg"] = [round(x, 2) for x in load]
        except OSError:
            pass

        try:
            with open("/proc/stat", "r") as f:
                line = f.readline()
                parts = line.split()
                if len(parts) >= 5:
                    total = sum(int(x) for x in parts[1:])
                    idle = int(parts[4])
                    if total > 0:
                        info["usage_percent"] = round((1 - idle / total) * 100, 1)
        except (FileNotFoundError, PermissionError):
            pass

        return info

    def memory_info(self):
        """Get memory information."""
        info = {
            "total_gb": 0.0,
            "used_gb": 0.0,
            "available_gb": 0.0,
            "usage_percent": 0.0,
            "swap_total_gb": 0.0,
            "swap_used_gb": 0.0,
        }

        try:
            with open("/proc/meminfo", "r") as f:
                meminfo = {}
                for line in f:
                    parts = line.split(":")
                    if len(parts) == 2:
                        key = parts[0].strip()
                        val = int(parts[1].strip().split()[0])
                        meminfo[key] = val

            total = meminfo.get("MemTotal", 0)
            available = meminfo.get("MemAvailable", 0)
            swap_total = meminfo.get("SwapTotal", 0)
            swap_free = meminfo.get("SwapFree", 0)

            info["total_gb"] = round(total / 1048576, 1)
            info["available_gb"] = round(available / 1048576, 1)
            info["used_gb"] = round((total - available) / 1048576, 1)
            info["usage_percent"] = round((total - available) / total * 100, 1) if total > 0 else 0
            info["swap_total_gb"] = round(swap_total / 1048576, 1)
            info["swap_used_gb"] = round((swap_total - swap_free) / 1048576, 1)
        except (FileNotFoundError, PermissionError):
            pass

        return info

    def disk_info(self):
        """Get disk usage information."""
        disks = []
        try:
            result = subprocess.run(
                ["df", "-BG", "--output=target,size,used,avail,pcent"],
                capture_output=True, text=True, timeout=5
            )
            lines = result.stdout.strip().split("\n")[1:]
            for line in lines:
                parts = line.split()
                if len(parts) >= 5 and parts[0].startswith("/"):
                    mount = parts[0]
                    if mount in ("/", "/home", "/var", "/tmp", "/boot") or mount.startswith("/mnt"):
                        disks.append({
                            "mount": mount,
                            "total_gb": int(parts[1].rstrip("G")),
                            "used_gb": int(parts[2].rstrip("G")),
                            "available_gb": int(parts[3].rstrip("G")),
                            "usage_percent": int(parts[4].rstrip("%")),
                        })
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return disks

    def network_info(self):
        """Get network interface information."""
        interfaces = []
        try:
            with open("/proc/net/dev", "r") as f:
                lines = f.readlines()[2:]
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 10:
                        iface = parts[0].rstrip(":")
                        if iface == "lo":
                            continue
                        rx_bytes = int(parts[1])
                        tx_bytes = int(parts[9])
                        interfaces.append({
                            "name": iface,
                            "rx_gb": round(rx_bytes / 1073741824, 2),
                            "tx_gb": round(tx_bytes / 1073741824, 2),
                        })
        except (FileNotFoundError, PermissionError):
            pass

        for iface in interfaces:
            try:
                result = subprocess.run(
                    ["ip", "-4", "addr", "show", iface["name"]],
                    capture_output=True, text=True, timeout=5
                )
                ips = re.findall(r"inet\s+(\d+\.\d+\.\d+\.\d+)", result.stdout)
                iface["ip"] = ips[0] if ips else "N/A"
            except (subprocess.TimeoutExpired, FileNotFoundError):
                iface["ip"] = "N/A"

        return interfaces

    def uptime_info(self):
        """Get system uptime."""
        try:
            with open("/proc/uptime", "r") as f:
                seconds = float(f.read().split()[0])
                td = timedelta(seconds=seconds)
                days = td.days
                hours, remainder = divmod(td.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                return {
                    "seconds": int(seconds),
                    "human": f"{days} days, {hours} hours, {minutes} minutes",
                }
        except (FileNotFoundError, PermissionError):
            return {"seconds": 0, "human": "Unknown"}

    def os_info(self):
        """Get OS information."""
        info = {
            "hostname": platform.node(),
            "kernel": platform.release(),
            "arch": platform.machine(),
            "os": "Unknown",
        }

        try:
            with open("/etc/os-release", "r") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME="):
                        info["os"] = line.split("=", 1)[1].strip().strip('"')
                        break
        except FileNotFoundError:
            info["os"] = f"{platform.system()} {platform.release()}"

        return info

    def top_processes(self, n=10):
        """Get top N processes by CPU usage."""
        processes = []
        try:
            result = subprocess.run(
                ["ps", "aux", "--sort=-pcpu"],
                capture_output=True, text=True, timeout=5
            )
            lines = result.stdout.strip().split("\n")[1:n+1]
            for line in lines:
                parts = line.split(None, 10)
                if len(parts) >= 11:
                    processes.append({
                        "user": parts[0],
                        "pid": int(parts[1]),
                        "cpu": float(parts[2]),
                        "mem": float(parts[3]),
                        "command": parts[10][:60],
                    })
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return processes

    def full_report(self):
        """Get complete system information report."""
        return {
            "os": self.os_info(),
            "uptime": self.uptime_info(),
            "cpu": self.cpu_info(),
            "memory": self.memory_info(),
            "disk": self.disk_info(),
            "network": self.network_info(),
            "top_processes": self.top_processes(5),
        }

    def print_report(self, sections=None):
        """Print formatted system report to terminal."""
        if sections is None:
            sections = ["os", "cpu", "memory", "disk", "network"]

        report = self.full_report()

        print("\n" + "=" * 60)
        print("          DARGSLAN SYSTEM INFORMATION REPORT")
        print("=" * 60)

        if "os" in sections:
            os_data = report["os"]
            uptime = report["uptime"]
            print(f"\n  HOSTNAME:     {os_data['hostname']}")
            print(f"  OS:           {os_data['os']}")
            print(f"  KERNEL:       {os_data['kernel']}")
            print(f"  ARCH:         {os_data['arch']}")
            print(f"  UPTIME:       {uptime['human']}")

        if "cpu" in sections:
            cpu = report["cpu"]
            print(f"\n  CPU")
            print(f"    Model:      {cpu['model']}")
            print(f"    Cores:      {cpu['cores']} ({cpu['threads']} threads)")
            print(f"    Load Avg:   {cpu['load_avg'][0]}, {cpu['load_avg'][1]}, {cpu['load_avg'][2]}")
            print(f"    Usage:      {cpu['usage_percent']}%")

        if "memory" in sections:
            mem = report["memory"]
            print(f"\n  MEMORY")
            print(f"    Total:      {mem['total_gb']} GB")
            print(f"    Used:       {mem['used_gb']} GB ({mem['usage_percent']}%)")
            print(f"    Available:  {mem['available_gb']} GB")
            print(f"    Swap:       {mem['swap_total_gb']} GB ({mem['swap_used_gb']} GB used)")

        if "disk" in sections:
            disks = report["disk"]
            print(f"\n  DISK")
            for d in disks:
                print(f"    {d['mount']:12s}  {d['used_gb']}G / {d['total_gb']}G ({d['usage_percent']}%)")

        if "network" in sections:
            nets = report["network"]
            print(f"\n  NETWORK")
            for n in nets:
                print(f"    {n['name']:10s}  IP: {n['ip']}  RX: {n['rx_gb']}GB  TX: {n['tx_gb']}GB")

        if "processes" in sections:
            procs = report["top_processes"]
            print(f"\n  TOP PROCESSES")
            print(f"    {'PID':>6s}  {'CPU%':>5s}  {'MEM%':>5s}  COMMAND")
            for p in procs:
                print(f"    {p['pid']:6d}  {p['cpu']:5.1f}  {p['mem']:5.1f}  {p['command']}")

        print("\n" + "-" * 60)
        print("  dargslan.com — Linux & DevOps eBooks and Cheat Sheets")
        print("=" * 60 + "\n")
