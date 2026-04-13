"""
Firewall audit tool — https://dargslan.com
"""

import subprocess
import re
import socket


class FirewallAudit:
    """Audit Linux firewall configuration."""

    def _run(self, cmd):
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return r.stdout.strip(), r.returncode
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return "", 1

    def check_iptables(self):
        """Check iptables rules and policies."""
        output, rc = self._run(["iptables", "-L", "-n", "-v"])
        if rc != 0:
            return {"available": False, "rules": [], "policies": {}}

        policies = {}
        rules = []
        current_chain = ""

        for line in output.split("\n"):
            chain_match = re.match(r"Chain (\S+) \(policy (\S+)", line)
            if chain_match:
                current_chain = chain_match.group(1)
                policies[current_chain] = chain_match.group(2)
                continue
            if line.strip() and not line.startswith("Chain") and "pkts" not in line:
                rules.append({"chain": current_chain, "rule": line.strip()})

        return {"available": True, "rules": rules, "policies": policies, "rule_count": len(rules)}

    def check_nftables(self):
        """Check nftables ruleset."""
        output, rc = self._run(["nft", "list", "ruleset"])
        if rc != 0:
            return {"available": False, "tables": []}

        tables = re.findall(r"table (\S+ \S+)", output)
        rule_count = len(re.findall(r"^\s+(tcp|udp|ip|ct|iif|meta|limit)", output, re.M))

        return {"available": True, "tables": tables, "rule_count": rule_count}

    def check_open_ports(self):
        """Check listening ports."""
        output, rc = self._run(["ss", "-tlnp"])
        if rc != 0:
            return []

        ports = []
        for line in output.split("\n")[1:]:
            parts = line.split()
            if len(parts) >= 4:
                addr = parts[3]
                port_match = re.search(r":(\d+)$", addr)
                if port_match:
                    port = int(port_match.group(1))
                    process = parts[-1] if len(parts) > 5 else "unknown"
                    ports.append({"port": port, "address": addr, "process": process})

        return sorted(ports, key=lambda x: x["port"])

    def check_ip_forwarding(self):
        """Check if IP forwarding is enabled."""
        try:
            with open("/proc/sys/net/ipv4/ip_forward", "r") as f:
                return f.read().strip() == "1"
        except (FileNotFoundError, PermissionError):
            return False

    def full_audit(self):
        """Run complete firewall audit."""
        issues = []
        score = 100

        ipt = self.check_iptables()
        nft = self.check_nftables()
        ports = self.check_open_ports()
        forwarding = self.check_ip_forwarding()

        if not ipt["available"] and not nft["available"]:
            issues.append({"severity": "critical", "message": "No firewall detected (iptables/nftables not available)"})
            score -= 40

        if ipt["available"]:
            input_policy = ipt["policies"].get("INPUT", "ACCEPT")
            forward_policy = ipt["policies"].get("FORWARD", "ACCEPT")

            if input_policy == "ACCEPT":
                issues.append({"severity": "critical", "message": "INPUT chain default policy is ACCEPT (should be DROP)", "fix": "iptables -P INPUT DROP"})
                score -= 25

            if forward_policy == "ACCEPT":
                issues.append({"severity": "warning", "message": "FORWARD chain default policy is ACCEPT", "fix": "iptables -P FORWARD DROP"})
                score -= 10

            has_ssh_limit = any("limit" in r["rule"] and ("22" in r["rule"] or "ssh" in r["rule"].lower()) for r in ipt["rules"])
            if not has_ssh_limit:
                issues.append({"severity": "warning", "message": "No SSH rate limiting detected", "fix": "iptables -A INPUT -p tcp --dport 22 -m limit --limit 3/min -j ACCEPT"})
                score -= 10

        if forwarding:
            issues.append({"severity": "info", "message": "IP forwarding is enabled — verify this is intentional"})

        dangerous_ports = [p for p in ports if p["port"] in (23, 21, 25, 3306, 5432, 6379, 27017)]
        for dp in dangerous_ports:
            if "0.0.0.0" in dp["address"] or "::" in dp["address"]:
                issues.append({
                    "severity": "warning",
                    "message": f"Port {dp['port']} is open on all interfaces",
                    "fix": f"Bind to 127.0.0.1 or add firewall rule to restrict access"
                })
                score -= 5

        return {
            "score": max(0, score),
            "grade": "A" if score >= 90 else "B" if score >= 75 else "C" if score >= 60 else "D" if score >= 40 else "F",
            "iptables": ipt,
            "nftables": nft,
            "open_ports": ports,
            "ip_forwarding": forwarding,
            "issues": issues,
            "issue_count": len(issues),
        }

    def print_audit(self):
        """Print formatted audit report."""
        report = self.full_audit()

        print(f"\n{'=' * 55}")
        print(f"  DARGSLAN FIREWALL AUDIT REPORT")
        print(f"{'=' * 55}")
        print(f"\n  Score: {report['score']}/100 (Grade: {report['grade']})")
        print(f"  Issues: {report['issue_count']}")

        if report['issues']:
            print(f"\n  FINDINGS:")
            for i, issue in enumerate(report['issues'], 1):
                sev = issue['severity'].upper()
                print(f"  [{sev:8s}] {issue['message']}")
                if 'fix' in issue:
                    print(f"             Fix: {issue['fix']}")

        print(f"\n  Open Ports: {len(report['open_ports'])}")
        for p in report['open_ports'][:10]:
            print(f"    {p['port']:>6d}  {p['address']}")

        print(f"\n{'-' * 55}")
        print(f"  dargslan.com — Linux Security eBooks & Cheat Sheets")
        print(f"{'=' * 55}\n")
