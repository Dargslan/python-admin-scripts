"""
Docker health checker — https://dargslan.com
"""

import subprocess
import json as json_module
import re


class DockerHealth:
    """Check Docker container health and resource usage."""

    def _run(self, cmd):
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            return r.stdout.strip(), r.returncode
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return "", 1

    def is_docker_available(self):
        """Check if Docker is available."""
        _, rc = self._run(["docker", "version", "--format", "{{.Server.Version}}"])
        return rc == 0

    def list_containers(self, all_containers=False):
        """List Docker containers."""
        cmd = ["docker", "ps", "--format", "{{.ID}}\t{{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}\t{{.State}}"]
        if all_containers:
            cmd.insert(2, "-a")
        output, rc = self._run(cmd)
        if rc != 0:
            return []

        containers = []
        for line in output.split("\n"):
            if not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) >= 6:
                containers.append({
                    "id": parts[0][:12],
                    "name": parts[1],
                    "image": parts[2],
                    "status": parts[3],
                    "ports": parts[4],
                    "state": parts[5],
                })
        return containers

    def container_stats(self, container_id):
        """Get resource stats for a container."""
        output, rc = self._run([
            "docker", "stats", container_id, "--no-stream",
            "--format", "{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}"
        ])
        if rc != 0:
            return None

        parts = output.split("\t")
        if len(parts) >= 5:
            mem_parts = parts[1].split("/")
            return {
                "cpu_percent": float(parts[0].rstrip("%")),
                "memory_usage": mem_parts[0].strip() if mem_parts else "0",
                "memory_limit": mem_parts[1].strip() if len(mem_parts) > 1 else "0",
                "memory_percent": float(parts[2].rstrip("%")),
                "net_io": parts[3],
                "block_io": parts[4],
            }
        return None

    def container_health(self, container_id):
        """Check health status of a container."""
        output, rc = self._run([
            "docker", "inspect", "--format",
            "{{.State.Health.Status}}", container_id
        ])
        if rc != 0 or not output or "no value" in output.lower():
            return "no-healthcheck"
        return output.strip()

    def check_all(self):
        """Check all running containers."""
        containers = self.list_containers()
        results = []

        for c in containers:
            stats = self.container_stats(c["id"])
            health = self.container_health(c["id"])
            entry = {
                "name": c["name"],
                "image": c["image"],
                "state": c["state"],
                "status": c["status"],
                "health": health,
            }
            if stats:
                entry.update({
                    "cpu_percent": stats["cpu_percent"],
                    "memory_usage": stats["memory_usage"],
                    "memory_percent": stats["memory_percent"],
                })
            results.append(entry)

        return results

    def get_unhealthy(self):
        """Get only unhealthy or exited containers."""
        all_containers = self.list_containers(all_containers=True)
        unhealthy = []
        for c in all_containers:
            health = self.container_health(c["id"])
            if c["state"] != "running" or health == "unhealthy":
                unhealthy.append({
                    "name": c["name"],
                    "image": c["image"],
                    "state": c["state"],
                    "health": health,
                    "status": c["status"],
                })
        return unhealthy

    def print_status(self, unhealthy_only=False):
        """Print formatted status report."""
        print(f"\n{'=' * 60}")
        print(f"  DARGSLAN DOCKER HEALTH CHECK")
        print(f"{'=' * 60}")

        if not self.is_docker_available():
            print("\n  Docker is not available or not running")
            print(f"\n{'=' * 60}\n")
            return

        if unhealthy_only:
            containers = self.get_unhealthy()
            print(f"\n  Unhealthy/Stopped Containers: {len(containers)}")
        else:
            containers = self.check_all()
            print(f"\n  Running Containers: {len(containers)}")

        if containers:
            print(f"\n  {'NAME':20s}  {'STATE':10s}  {'HEALTH':12s}  {'CPU':>6s}  {'MEM':>8s}")
            print(f"  {'-' * 60}")
            for c in containers:
                cpu = f"{c.get('cpu_percent', 0):.1f}%" if 'cpu_percent' in c else "N/A"
                mem = c.get('memory_usage', 'N/A')
                print(f"  {c['name']:20s}  {c['state']:10s}  {c['health']:12s}  {cpu:>6s}  {mem:>8s}")
        else:
            print("  No containers found")

        print(f"\n{'-' * 60}")
        print(f"  dargslan.com — Docker & DevOps eBooks and Cheat Sheets")
        print(f"{'=' * 60}\n")
