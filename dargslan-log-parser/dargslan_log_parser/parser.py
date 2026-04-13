"""
Log file parser for Linux system logs.

Part of dargslan-log-parser — https://dargslan.com
"""

import re
from collections import Counter
from datetime import datetime


class LogParser:
    """Parse and analyze Linux log files."""

    SYSLOG_PATTERN = re.compile(
        r"(\w{3}\s+\d+\s+\d{2}:\d{2}:\d{2})\s+(\S+)\s+(\S+?)(?:\[\d+\])?:\s+(.*)"
    )

    AUTH_FAILED_PATTERN = re.compile(
        r"Failed password for (?:invalid user )?(\S+) from (\d+\.\d+\.\d+\.\d+)"
    )

    AUTH_ACCEPTED_PATTERN = re.compile(
        r"Accepted (?:password|publickey) for (\S+) from (\d+\.\d+\.\d+\.\d+)"
    )

    NGINX_ACCESS_PATTERN = re.compile(
        r'(\d+\.\d+\.\d+\.\d+)\s+-\s+-\s+\[(.+?)\]\s+"(\w+)\s+(\S+)\s+\S+"\s+(\d+)\s+(\d+)\s+"([^"]*)"\s+"([^"]*)"'
    )

    def _read_lines(self, filepath, tail=None):
        """Read lines from a log file, optionally only the last N lines."""
        try:
            with open(filepath, "r", errors="replace") as f:
                lines = f.readlines()
            if tail:
                lines = lines[-tail:]
            return lines
        except (FileNotFoundError, PermissionError) as e:
            raise RuntimeError(f"Cannot read {filepath}: {e}")

    def parse_syslog(self, filepath, tail=None):
        """Parse a syslog-format file."""
        entries = []
        for line in self._read_lines(filepath, tail):
            match = self.SYSLOG_PATTERN.match(line.strip())
            if match:
                entries.append({
                    "timestamp": match.group(1),
                    "hostname": match.group(2),
                    "service": match.group(3),
                    "message": match.group(4),
                })
        return entries

    def parse_auth_log(self, filepath="/var/log/auth.log", tail=None):
        """Parse auth.log for login attempts."""
        entries = []
        for line in self._read_lines(filepath, tail):
            failed = self.AUTH_FAILED_PATTERN.search(line)
            if failed:
                ts_match = re.match(r"(\w{3}\s+\d+\s+\d{2}:\d{2}:\d{2})", line)
                entries.append({
                    "type": "failed",
                    "user": failed.group(1),
                    "ip": failed.group(2),
                    "timestamp": ts_match.group(1) if ts_match else "",
                })
                continue

            accepted = self.AUTH_ACCEPTED_PATTERN.search(line)
            if accepted:
                ts_match = re.match(r"(\w{3}\s+\d+\s+\d{2}:\d{2}:\d{2})", line)
                entries.append({
                    "type": "accepted",
                    "user": accepted.group(1),
                    "ip": accepted.group(2),
                    "timestamp": ts_match.group(1) if ts_match else "",
                })

        return entries

    def parse_nginx_access(self, filepath="/var/log/nginx/access.log", tail=None):
        """Parse nginx access log."""
        entries = []
        for line in self._read_lines(filepath, tail):
            match = self.NGINX_ACCESS_PATTERN.match(line.strip())
            if match:
                entries.append({
                    "ip": match.group(1),
                    "timestamp": match.group(2),
                    "method": match.group(3),
                    "path": match.group(4),
                    "status": int(match.group(5)),
                    "bytes": int(match.group(6)),
                    "referer": match.group(7),
                    "user_agent": match.group(8),
                })
        return entries

    def search(self, filepath, pattern, case_insensitive=False, tail=None):
        """Search a log file for matching lines."""
        flags = re.IGNORECASE if case_insensitive else 0
        regex = re.compile(pattern, flags)
        matches = []
        for i, line in enumerate(self._read_lines(filepath, tail), 1):
            if regex.search(line):
                matches.append({"line_number": i, "content": line.strip()})
        return matches

    def summary(self, filepath, log_type="syslog"):
        """Generate a summary report for a log file."""
        if log_type == "auth":
            entries = self.parse_auth_log(filepath)
            failed = [e for e in entries if e["type"] == "failed"]
            accepted = [e for e in entries if e["type"] == "accepted"]
            ip_counter = Counter(e["ip"] for e in failed)
            user_counter = Counter(e["user"] for e in failed)
            return {
                "total_entries": len(entries),
                "failed_logins": len(failed),
                "accepted_logins": len(accepted),
                "top_ips": ip_counter.most_common(10),
                "top_users": user_counter.most_common(10),
            }
        elif log_type == "nginx":
            entries = self.parse_nginx_access(filepath)
            status_counter = Counter(e["status"] for e in entries)
            ip_counter = Counter(e["ip"] for e in entries)
            path_counter = Counter(e["path"] for e in entries)
            errors = [e for e in entries if e["status"] >= 400]
            return {
                "total_requests": len(entries),
                "error_count": len(errors),
                "status_codes": dict(status_counter.most_common(20)),
                "top_ips": ip_counter.most_common(10),
                "top_paths": path_counter.most_common(10),
            }
        else:
            entries = self.parse_syslog(filepath)
            service_counter = Counter(e["service"] for e in entries)
            return {
                "total_entries": len(entries),
                "services": dict(service_counter.most_common(20)),
            }

    def print_summary(self, filepath, log_type="syslog"):
        """Print formatted summary to terminal."""
        report = self.summary(filepath, log_type)

        print("\n" + "=" * 50)
        print("  DARGSLAN LOG ANALYSIS REPORT")
        print("=" * 50)

        if log_type == "auth":
            print(f"\n  Total entries:    {report['total_entries']}")
            print(f"  Failed logins:    {report['failed_logins']}")
            print(f"  Accepted logins:  {report['accepted_logins']}")
            if report['top_ips']:
                print(f"\n  Top attacker IPs:")
                for ip, count in report['top_ips'][:5]:
                    print(f"    {ip:20s} {count:5d} attempts")
        elif log_type == "nginx":
            print(f"\n  Total requests:   {report['total_requests']}")
            print(f"  Errors (4xx/5xx): {report['error_count']}")
            if report['status_codes']:
                print(f"\n  Status codes:")
                for code, count in sorted(report['status_codes'].items()):
                    print(f"    {code}: {count}")
        else:
            print(f"\n  Total entries:    {report['total_entries']}")
            if report['services']:
                print(f"\n  Services:")
                for svc, count in list(report['services'].items())[:10]:
                    print(f"    {svc:25s} {count:5d}")

        print("\n" + "-" * 50)
        print("  dargslan.com — Linux & DevOps eBooks")
        print("=" * 50 + "\n")
