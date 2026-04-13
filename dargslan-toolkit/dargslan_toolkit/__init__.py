"""
dargslan-toolkit — The Complete Linux Sysadmin Toolkit

108 professional CLI tools for Linux server management, security auditing,
performance monitoring, and DevOps operations. One install. All tools.

Categories:
  - System Monitoring & Performance (14 tools)
  - Security & Hardening (20 tools)
  - Networking & DNS (17 tools)
  - Firewall & Network Security (3 tools)
  - Log Analysis (7 tools)
  - System Configuration (17 tools)
  - Storage & Filesystems (11 tools)
  - DevOps & Containers (5 tools)
  - Database Health (3 tools)
  - Package & Service Management (9 tools)
  - System Diagnostics (2 tools)

Install: pip install dargslan-toolkit

Homepage: https://dargslan.com
eBooks: https://dargslan.com/books
Cheat Sheets: https://dargslan.com/cheat-sheets
Blog: https://dargslan.com/blog
"""

__version__ = "1.19.0"
__author__ = "Dargslan"
__url__ = "https://dargslan.com"

TOOL_COUNT = 108
CATEGORIES = {
    "monitoring": [
        "dargslan-sysinfo", "dargslan-process-monitor", "dargslan-proc-monitor",
        "dargslan-load-average", "dargslan-memory-profiler", "dargslan-swap-analyzer",
        "dargslan-swap-manager", "dargslan-uptime-report", "dargslan-inode-monitor",
        "dargslan-mount-monitor", "dargslan-zombie-kill", "dargslan-process-killer",
        "dargslan-io-monitor", "dargslan-user-sessions",
    ],
    "security": [
        "dargslan-firewall-audit", "dargslan-ssh-hardening", "dargslan-ssh-audit",
        "dargslan-sshkey-audit", "dargslan-sudoers-audit", "dargslan-pam-audit",
        "dargslan-sysctl-audit", "dargslan-env-audit", "dargslan-file-integrity",
        "dargslan-acl-check", "dargslan-audit-log", "dargslan-login-history",
        "dargslan-login-tracker", "dargslan-lastlog-audit", "dargslan-passwd-audit",
        "dargslan-security-scan", "dargslan-selinux-check", "dargslan-user-audit",
        "dargslan-apparmor-check", "dargslan-lsof-audit",
    ],
    "networking": [
        "dargslan-net-scanner", "dargslan-port-monitor", "dargslan-dns-check",
        "dargslan-dns-resolver", "dargslan-resolv-check", "dargslan-bandwidth-monitor",
        "dargslan-interface-monitor", "dargslan-ssl-checker", "dargslan-ip-geo",
        "dargslan-tcp-monitor", "dargslan-socket-stats", "dargslan-network-latency",
        "dargslan-route-check", "dargslan-hostname-check", "dargslan-hostname-info",
        "dargslan-bridge-monitor", "dargslan-ethtool-check",
    ],
    "firewall": [
        "dargslan-iptables-export", "dargslan-netfilter-check", "dargslan-arp-monitor",
    ],
    "logs": [
        "dargslan-log-parser", "dargslan-journald-analyzer", "dargslan-journal-export",
        "dargslan-dmesg-analyzer", "dargslan-log-rotate", "dargslan-log-stats",
        "dargslan-nginx-analyzer",
    ],
    "config": [
        "dargslan-crontab-backup", "dargslan-cron-audit", "dargslan-cron-parser",
        "dargslan-systemd-timer", "dargslan-systemd-analyze", "dargslan-systemd-unit",
        "dargslan-grub-check", "dargslan-fstab-check", "dargslan-locale-check",
        "dargslan-timezone-info", "dargslan-ntp-check", "dargslan-ulimit-check",
        "dargslan-kernel-module", "dargslan-kernel-check", "dargslan-motd-manager",
        "dargslan-at-scheduler", "dargslan-modprobe-check",
    ],
    "storage": [
        "dargslan-disk-cleaner", "dargslan-disk-benchmark", "dargslan-disk-quota",
        "dargslan-disk-health", "dargslan-lvm-check", "dargslan-raid-monitor",
        "dargslan-nfs-health", "dargslan-tmpfile-cleaner", "dargslan-tmpfile-clean",
        "dargslan-backup-monitor", "dargslan-xfs-check",
    ],
    "devops": [
        "dargslan-docker-health", "dargslan-container-audit", "dargslan-cgroup-monitor",
        "dargslan-cgroup-audit", "dargslan-git-audit",
    ],
    "databases": [
        "dargslan-mysql-health", "dargslan-postgres-health", "dargslan-redis-health",
    ],
    "packages": [
        "dargslan-apt-history", "dargslan-apt-check", "dargslan-package-audit",
        "dargslan-service-monitor", "dargslan-service-restart", "dargslan-apache-analyzer",
        "dargslan-cert-manager", "dargslan-bash-alias", "dargslan-yum-history",
    ],
    "diagnostics": [
        "dargslan-coredump-check", "dargslan-entropy-check",
    ],
}


def list_tools():
    """List all available tools grouped by category."""
    total = 0
    for cat, tools in CATEGORIES.items():
        print(f"\n{'=' * 40}")
        print(f"  {cat.upper()} ({len(tools)} tools)")
        print(f"{'=' * 40}")
        for t in tools:
            print(f"  {t}")
        total += len(tools)
    print(f"\nTotal: {total} tools")
    print(f"Install all: pip install dargslan-toolkit")
    print(f"More info: https://dargslan.com")


__all__ = ["__version__", "TOOL_COUNT", "CATEGORIES", "list_tools"]
