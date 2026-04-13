# 🐧 python-admin-scripts

**107 Professional Linux Sysadmin CLI Tools** — Open-source Python scripts for server management, security auditing, performance monitoring, networking, and DevOps operations.

[![PyPI - dargslan-toolkit](https://img.shields.io/pypi/v/dargslan-toolkit?label=dargslan-toolkit)](https://pypi.org/project/dargslan-toolkit/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Tools](https://img.shields.io/badge/tools-107-green.svg)](https://dargslan.com)

---

## ⚡ Install Everything

```bash
pip install dargslan-toolkit
```

One command installs **all 107 CLI tools** — ready to use immediately.

Or install individual tools:

```bash
pip install dargslan-sysinfo
pip install dargslan-firewall-audit
pip install dargslan-ssh-hardening
```

---

## 📋 All 107 Tools

### 🖥️ System Monitoring & Performance (14 tools)

| Tool | Command | Description |
|------|---------|-------------|
| [dargslan-sysinfo](dargslan-sysinfo/) | `sysinfo` | Full system overview — CPU, memory, disk, network, OS |
| [dargslan-process-monitor](dargslan-process-monitor/) | `process-monitor` | Real-time process monitoring |
| [dargslan-proc-monitor](dargslan-proc-monitor/) | `proc-monitor` | Top CPU/memory consumers, load average |
| [dargslan-load-average](dargslan-load-average/) | `load-average` | Load average analyzer — bottleneck detection |
| [dargslan-memory-profiler](dargslan-memory-profiler/) | `memory-profiler` | Deep memory analysis — buffers, cache, slab |
| [dargslan-swap-analyzer](dargslan-swap-analyzer/) | `swap-analyzer` | Swap usage analysis — pressure detection |
| [dargslan-swap-manager](dargslan-swap-manager/) | `swap-manager` | Swap space management — priorities, auto-config |
| [dargslan-uptime-report](dargslan-uptime-report/) | `uptime-report` | System uptime tracking — boot history |
| [dargslan-inode-monitor](dargslan-inode-monitor/) | `inode-monitor` | Inode usage — detect exhaustion |
| [dargslan-mount-monitor](dargslan-mount-monitor/) | `mount-monitor` | Mount point monitor — stale NFS, options |
| [dargslan-zombie-kill](dargslan-zombie-kill/) | `zombie-kill` | Zombie process finder and cleaner |
| [dargslan-process-killer](dargslan-process-killer/) | `process-killer` | Terminate resource-hungry processes |
| [dargslan-io-monitor](dargslan-io-monitor/) | `io-monitor` | Disk I/O — IOPS, throughput per device |
| [dargslan-user-sessions](dargslan-user-sessions/) | `user-sessions` | Active user session monitoring |

### 🔒 Security & Hardening (20 tools)

| Tool | Command | Description |
|------|---------|-------------|
| [dargslan-firewall-audit](dargslan-firewall-audit/) | `firewall-audit` | iptables/nftables rule auditing |
| [dargslan-ssh-hardening](dargslan-ssh-hardening/) | `ssh-hardening` | SSH server hardening audit |
| [dargslan-ssh-audit](dargslan-ssh-audit/) | `ssh-audit` | SSH algorithms, ciphers, key strength |
| [dargslan-sshkey-audit](dargslan-sshkey-audit/) | `sshkey-audit` | authorized_keys scan, weak keys |
| [dargslan-sudoers-audit](dargslan-sudoers-audit/) | `sudoers-audit` | Sudoers file analysis — NOPASSWD detection |
| [dargslan-pam-audit](dargslan-pam-audit/) | `pam-audit` | PAM configuration auditing |
| [dargslan-sysctl-audit](dargslan-sysctl-audit/) | `sysctl-audit` | Kernel parameter security audit |
| [dargslan-env-audit](dargslan-env-audit/) | `env-audit` | Environment variable security |
| [dargslan-file-integrity](dargslan-file-integrity/) | `file-integrity` | File integrity monitoring — checksums |
| [dargslan-acl-check](dargslan-acl-check/) | `acl-check` | File ACL & SUID/SGID checker |
| [dargslan-audit-log](dargslan-audit-log/) | `audit-log` | Auditd log analyzer |
| [dargslan-login-history](dargslan-login-history/) | `login-history` | wtmp/btmp login analysis |
| [dargslan-login-tracker](dargslan-login-tracker/) | `login-tracker` | Active session & brute force tracking |
| [dargslan-lastlog-audit](dargslan-lastlog-audit/) | `lastlog-audit` | Dormant accounts, never-logged-in users |
| [dargslan-passwd-audit](dargslan-passwd-audit/) | `passwd-audit` | Password policy audit — shadow file |
| [dargslan-security-scan](dargslan-security-scan/) | `security-scan` | Comprehensive system hardening check |
| [dargslan-selinux-check](dargslan-selinux-check/) | `selinux-check` | SELinux status — mode, policy, denials |
| [dargslan-user-audit](dargslan-user-audit/) | `user-audit` | User account auditing — UID 0, groups |
| [dargslan-apparmor-check](dargslan-apparmor-check/) | `apparmor-check` | AppArmor profile status checker |
| [dargslan-lsof-audit](dargslan-lsof-audit/) | `lsof-audit` | Open files & ports auditor |

### 🌐 Networking & DNS (16 tools)

| Tool | Command | Description |
|------|---------|-------------|
| [dargslan-net-scanner](dargslan-net-scanner/) | `net-scanner` | Network scanner — ping sweep, port scan |
| [dargslan-port-monitor](dargslan-port-monitor/) | `port-monitor` | Listening ports, bound services |
| [dargslan-dns-check](dargslan-dns-check/) | `dns-check` | DNS record verification |
| [dargslan-dns-resolver](dargslan-dns-resolver/) | `dns-resolver` | DNS resolver analysis |
| [dargslan-resolv-check](dargslan-resolv-check/) | `resolv-check` | resolv.conf checker |
| [dargslan-bandwidth-monitor](dargslan-bandwidth-monitor/) | `bandwidth-monitor` | Per-interface throughput tracking |
| [dargslan-interface-monitor](dargslan-interface-monitor/) | `interface-monitor` | Interface status — link, speed, errors |
| [dargslan-ssl-checker](dargslan-ssl-checker/) | `ssl-checker` | SSL certificate validator |
| [dargslan-ip-geo](dargslan-ip-geo/) | `ip-geo` | IP geolocation lookup |
| [dargslan-tcp-monitor](dargslan-tcp-monitor/) | `tcp-monitor` | TCP connection states monitor |
| [dargslan-socket-stats](dargslan-socket-stats/) | `socket-stats` | Socket statistics by protocol |
| [dargslan-network-latency](dargslan-network-latency/) | `network-latency` | Ping, traceroute, jitter analysis |
| [dargslan-route-check](dargslan-route-check/) | `route-check` | Routing table analyzer |
| [dargslan-hostname-check](dargslan-hostname-check/) | `hostname-check` | FQDN, reverse DNS, /etc/hosts |
| [dargslan-hostname-info](dargslan-hostname-info/) | `hostname-info` | System identity, domain details |
| [dargslan-bridge-monitor](dargslan-bridge-monitor/) | `bridge-monitor` | Network bridge & VLAN monitor |

### 🔥 Firewall & Network Security (3 tools)

| Tool | Command | Description |
|------|---------|-------------|
| [dargslan-iptables-export](dargslan-iptables-export/) | `iptables-export` | iptables rule backup & export |
| [dargslan-netfilter-check](dargslan-netfilter-check/) | `netfilter-check` | Netfilter conntrack analyzer |
| [dargslan-arp-monitor](dargslan-arp-monitor/) | `arp-monitor` | ARP cache & spoofing detection |

### 📊 Log Analysis (7 tools)

| Tool | Command | Description |
|------|---------|-------------|
| [dargslan-log-parser](dargslan-log-parser/) | `log-parser` | Multi-format log parser |
| [dargslan-journald-analyzer](dargslan-journald-analyzer/) | `journald-analyzer` | Systemd journal analyzer |
| [dargslan-journal-export](dargslan-journal-export/) | `journal-export` | Journal log exporter |
| [dargslan-dmesg-analyzer](dargslan-dmesg-analyzer/) | `dmesg-analyzer` | Kernel dmesg analyzer |
| [dargslan-log-rotate](dargslan-log-rotate/) | `log-rotate` | Logrotate config validator |
| [dargslan-log-stats](dargslan-log-stats/) | `log-stats` | Log statistics & growth rates |
| [dargslan-nginx-analyzer](dargslan-nginx-analyzer/) | `nginx-analyzer` | Nginx log analyzer |

### ⚙️ System Configuration (17 tools)

| Tool | Command | Description |
|------|---------|-------------|
| [dargslan-crontab-backup](dargslan-crontab-backup/) | `crontab-backup` | Crontab backup & restore |
| [dargslan-cron-audit](dargslan-cron-audit/) | `cron-audit` | Cron job auditing |
| [dargslan-cron-parser](dargslan-cron-parser/) | `cron-parser` | Cron expression parser |
| [dargslan-systemd-timer](dargslan-systemd-timer/) | `systemd-timer` | Systemd timer analyzer |
| [dargslan-systemd-analyze](dargslan-systemd-analyze/) | `systemd-analyze` | Boot time analyzer |
| [dargslan-systemd-unit](dargslan-systemd-unit/) | `systemd-unit` | Unit status & dependencies |
| [dargslan-grub-check](dargslan-grub-check/) | `grub-check` | GRUB bootloader validator |
| [dargslan-fstab-check](dargslan-fstab-check/) | `fstab-check` | fstab syntax validator |
| [dargslan-locale-check](dargslan-locale-check/) | `locale-check` | Locale & encoding checker |
| [dargslan-timezone-info](dargslan-timezone-info/) | `timezone-info` | Timezone & NTP info |
| [dargslan-ntp-check](dargslan-ntp-check/) | `ntp-check` | NTP sync checker |
| [dargslan-ulimit-check](dargslan-ulimit-check/) | `ulimit-check` | Resource limits checker |
| [dargslan-kernel-module](dargslan-kernel-module/) | `kernel-module` | Kernel module manager |
| [dargslan-kernel-check](dargslan-kernel-check/) | `kernel-check` | Kernel version checker |
| [dargslan-motd-manager](dargslan-motd-manager/) | `motd-manager` | MOTD / login banner manager |
| [dargslan-at-scheduler](dargslan-at-scheduler/) | `at-scheduler` | at/batch scheduler auditor |
| [dargslan-modprobe-check](dargslan-modprobe-check/) | `modprobe-check` | Kernel module & blacklist checker |

### 💾 Storage & Filesystems (11 tools)

| Tool | Command | Description |
|------|---------|-------------|
| [dargslan-disk-cleaner](dargslan-disk-cleaner/) | `disk-cleaner` | Disk space cleaner |
| [dargslan-disk-benchmark](dargslan-disk-benchmark/) | `disk-benchmark` | Disk I/O benchmarking |
| [dargslan-disk-quota](dargslan-disk-quota/) | `disk-quota` | Disk quota manager |
| [dargslan-disk-health](dargslan-disk-health/) | `disk-health` | SMART data & health monitor |
| [dargslan-lvm-check](dargslan-lvm-check/) | `lvm-check` | LVM volume checker |
| [dargslan-raid-monitor](dargslan-raid-monitor/) | `raid-monitor` | RAID array monitor |
| [dargslan-nfs-health](dargslan-nfs-health/) | `nfs-health` | NFS share health checker |
| [dargslan-tmpfile-cleaner](dargslan-tmpfile-cleaner/) | `tmpfile-cleaner` | /tmp cleanup and analysis |
| [dargslan-tmpfile-clean](dargslan-tmpfile-clean/) | `tmpfile-clean` | Temp file analyzer |
| [dargslan-backup-monitor](dargslan-backup-monitor/) | `backup-monitor` | Backup file monitor |
| [dargslan-xfs-check](dargslan-xfs-check/) | `xfs-check` | XFS filesystem health checker |

### 🐳 DevOps & Containers (5 tools)

| Tool | Command | Description |
|------|---------|-------------|
| [dargslan-docker-health](dargslan-docker-health/) | `docker-health` | Docker container health monitor |
| [dargslan-container-audit](dargslan-container-audit/) | `container-audit` | Container security audit |
| [dargslan-cgroup-monitor](dargslan-cgroup-monitor/) | `cgroup-monitor` | Cgroup resource monitor |
| [dargslan-cgroup-audit](dargslan-cgroup-audit/) | `cgroup-audit` | Cgroup v2 auditor |
| [dargslan-git-audit](dargslan-git-audit/) | `git-audit` | Git repo auditor — secrets, large files |

### 🗄️ Database Health (3 tools)

| Tool | Command | Description |
|------|---------|-------------|
| [dargslan-mysql-health](dargslan-mysql-health/) | `mysql-health` | MySQL health monitor |
| [dargslan-postgres-health](dargslan-postgres-health/) | `postgres-health` | PostgreSQL health monitor |
| [dargslan-redis-health](dargslan-redis-health/) | `redis-health` | Redis health monitor |

### 📦 Package & Service Management (9 tools)

| Tool | Command | Description |
|------|---------|-------------|
| [dargslan-apt-history](dargslan-apt-history/) | `apt-history` | APT package history |
| [dargslan-apt-check](dargslan-apt-check/) | `apt-check` | APT health checker |
| [dargslan-package-audit](dargslan-package-audit/) | `package-audit` | Package security audit |
| [dargslan-service-monitor](dargslan-service-monitor/) | `service-monitor` | Systemd service monitor |
| [dargslan-service-restart](dargslan-service-restart/) | `service-restart` | Service restart monitor |
| [dargslan-apache-analyzer](dargslan-apache-analyzer/) | `apache-analyzer` | Apache log & config analyzer |
| [dargslan-cert-manager](dargslan-cert-manager/) | `cert-manager` | SSL certificate manager |
| [dargslan-bash-alias](dargslan-bash-alias/) | `bash-alias` | Bash alias manager |
| [dargslan-yum-history](dargslan-yum-history/) | `yum-history` | YUM/DNF history analyzer |

### 🔧 System Diagnostics (2 tools)

| Tool | Command | Description |
|------|---------|-------------|
| [dargslan-coredump-check](dargslan-coredump-check/) | `coredump-check` | Core dump analyzer |
| [dargslan-entropy-check](dargslan-entropy-check/) | `entropy-check` | System entropy monitor |

---

## 🚀 Quick Start

```bash
pip install dargslan-toolkit

dargslan-sysinfo
dargslan-firewall-audit
dargslan-ssh-hardening --json
dargslan-load-average
dargslan-disk-health
```

Every tool supports `--help` and `--json` output format.

---

## 📂 Repository Structure

```
python-admin-scripts/
├── dargslan-toolkit/          # Meta-package (installs all 107 tools)
├── dargslan-sysinfo/          # Individual tool packages
├── dargslan-firewall-audit/
├── dargslan-ssh-hardening/
├── ...                        # 107 tool directories
└── README.md
```

Each tool directory contains:
- `pyproject.toml` — Package configuration
- `README.md` — Tool documentation
- `<module_name>/cli.py` — CLI entry point
- `<module_name>/__init__.py` — Package metadata

---

## 📚 More from Dargslan

| Resource | Link |
|----------|------|
| **210+ Linux & DevOps eBooks** | [dargslan.com/books](https://dargslan.com/books) |
| **380+ Free Cheat Sheets (PDF)** | [dargslan.com/cheat-sheets](https://dargslan.com/cheat-sheets) |
| **430+ Blog Posts & Tutorials** | [dargslan.com/blog](https://dargslan.com/blog) |
| **PyPI — dargslan-toolkit** | [pypi.org/project/dargslan-toolkit](https://pypi.org/project/dargslan-toolkit/) |

---

## 📄 License

MIT License — Free for personal and commercial use.

---

<p align="center">
  <strong>Made by <a href="https://dargslan.com">Dargslan</a></strong><br>
  Professional Linux & DevOps tools, eBooks, and resources.<br><br>
  <a href="https://dargslan.com">Website</a> •
  <a href="https://dargslan.com/books">eBooks</a> •
  <a href="https://dargslan.com/cheat-sheets">Cheat Sheets</a> •
  <a href="https://dargslan.com/blog">Blog</a> •
  <a href="https://pypi.org/project/dargslan-toolkit/">PyPI</a>
</p>
