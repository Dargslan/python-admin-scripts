# 🛠️ dargslan-toolkit

**The Complete Linux Sysadmin Toolkit** — 107 professional CLI tools for Linux server management, security auditing, performance monitoring, and DevOps operations. One install. All tools.

[![PyPI version](https://img.shields.io/pypi/v/dargslan-toolkit)](https://pypi.org/project/dargslan-toolkit/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Tools](https://img.shields.io/badge/tools-107-green.svg)](https://dargslan.com)

---

## ⚡ Quick Install

```bash
pip install dargslan-toolkit
```

One command installs **all 107 CLI tools** — ready to use immediately from your terminal.

---

## 📋 Complete Tool Reference

### 🖥️ System Monitoring & Performance (14 tools)

| # | Tool | Description |
|---|------|-------------|
| 1 | [dargslan-sysinfo](https://pypi.org/project/dargslan-sysinfo/) | Full system overview — CPU, memory, disk, network, OS info |
| 2 | [dargslan-process-monitor](https://pypi.org/project/dargslan-process-monitor/) | Real-time process monitoring with top-like output |
| 3 | [dargslan-proc-monitor](https://pypi.org/project/dargslan-proc-monitor/) | Process resource monitor — top CPU/memory consumers, load average |
| 4 | [dargslan-load-average](https://pypi.org/project/dargslan-load-average/) | Load average analyzer — 1/5/15 min load vs CPU cores, bottleneck detection |
| 5 | [dargslan-memory-profiler](https://pypi.org/project/dargslan-memory-profiler/) | Deep memory analysis — buffers, cache, slab, per-process breakdown |
| 6 | [dargslan-swap-analyzer](https://pypi.org/project/dargslan-swap-analyzer/) | Swap usage analysis — pressure detection, swappiness tuning |
| 7 | [dargslan-swap-manager](https://pypi.org/project/dargslan-swap-manager/) | Swap space management — swap files, priorities, auto-configuration |
| 8 | [dargslan-uptime-report](https://pypi.org/project/dargslan-uptime-report/) | System uptime tracking — boot history, availability reporting |
| 9 | [dargslan-inode-monitor](https://pypi.org/project/dargslan-inode-monitor/) | Inode usage monitoring — detect exhaustion before disk-full errors |
| 10 | [dargslan-mount-monitor](https://pypi.org/project/dargslan-mount-monitor/) | Mount point monitor — filesystem mounts, stale NFS, options audit |
| 11 | [dargslan-zombie-kill](https://pypi.org/project/dargslan-zombie-kill/) | Zombie process finder — detect and clean up defunct processes |
| 12 | [dargslan-process-killer](https://pypi.org/project/dargslan-process-killer/) | Process management — find and terminate resource-hungry processes |
| 13 | [dargslan-io-monitor](https://pypi.org/project/dargslan-io-monitor/) | Disk I/O performance — IOPS, throughput, read/write stats per device |
| 14 | [dargslan-user-sessions](https://pypi.org/project/dargslan-user-sessions/) | Active user session monitoring — who's logged in, idle detection |

### 🔒 Security & Hardening (20 tools)

| # | Tool | Description |
|---|------|-------------|
| 15 | [dargslan-firewall-audit](https://pypi.org/project/dargslan-firewall-audit/) | iptables/nftables rule auditing — open ports, default policies |
| 16 | [dargslan-ssh-hardening](https://pypi.org/project/dargslan-ssh-hardening/) | SSH server hardening — sshd_config audit, root login, key auth |
| 17 | [dargslan-ssh-audit](https://pypi.org/project/dargslan-ssh-audit/) | SSH server & key auditing — algorithms, ciphers, key strength |
| 18 | [dargslan-sshkey-audit](https://pypi.org/project/dargslan-sshkey-audit/) | SSH key auditor — authorized_keys scan, weak keys, key sprawl |
| 19 | [dargslan-sudoers-audit](https://pypi.org/project/dargslan-sudoers-audit/) | Sudoers file analysis — NOPASSWD detection, privilege escalation |
| 20 | [dargslan-pam-audit](https://pypi.org/project/dargslan-pam-audit/) | PAM configuration auditing — auth modules, password policies |
| 21 | [dargslan-sysctl-audit](https://pypi.org/project/dargslan-sysctl-audit/) | Kernel parameter audit — security hardening, network settings |
| 22 | [dargslan-env-audit](https://pypi.org/project/dargslan-env-audit/) | Environment variable security — leaked secrets, PATH analysis |
| 23 | [dargslan-file-integrity](https://pypi.org/project/dargslan-file-integrity/) | File integrity monitoring — checksum tracking, change detection |
| 24 | [dargslan-acl-check](https://pypi.org/project/dargslan-acl-check/) | File ACL & permission checker — SUID, world-writable, POSIX ACLs |
| 25 | [dargslan-audit-log](https://pypi.org/project/dargslan-audit-log/) | Auditd log analyzer — file access, privilege escalation, user activity |
| 26 | [dargslan-login-history](https://pypi.org/project/dargslan-login-history/) | Login history — wtmp/btmp analysis, failed attempts, session tracking |
| 27 | [dargslan-login-tracker](https://pypi.org/project/dargslan-login-tracker/) | Login session tracker — active sessions, IP tracking, brute force |
| 28 | [dargslan-lastlog-audit](https://pypi.org/project/dargslan-lastlog-audit/) | Last login audit — dormant accounts, never-logged-in users |
| 29 | [dargslan-passwd-audit](https://pypi.org/project/dargslan-passwd-audit/) | Password policy auditor — shadow file, empty passwords, aging |
| 30 | [dargslan-security-scan](https://pypi.org/project/dargslan-security-scan/) | General security scanner — comprehensive system hardening check |
| 31 | [dargslan-selinux-check](https://pypi.org/project/dargslan-selinux-check/) | SELinux status checker — mode, policy, booleans, denials |
| 32 | [dargslan-user-audit](https://pypi.org/project/dargslan-user-audit/) | User account auditing — UID 0 check, shell assignment, groups |
| 33 | [dargslan-apparmor-check](https://pypi.org/project/dargslan-apparmor-check/) | AppArmor profile status checker — enforcement mode, violations |
| 34 | [dargslan-lsof-audit](https://pypi.org/project/dargslan-lsof-audit/) | Open files & ports auditor — lsof analysis, deleted files, connections |

### 🌐 Networking & DNS (16 tools)

| # | Tool | Description |
|---|------|-------------|
| 35 | [dargslan-net-scanner](https://pypi.org/project/dargslan-net-scanner/) | Network scanner — ping sweep, port scanning, service detection |
| 36 | [dargslan-port-monitor](https://pypi.org/project/dargslan-port-monitor/) | Listening port monitor — open ports, bound services, PID mapping |
| 37 | [dargslan-dns-check](https://pypi.org/project/dargslan-dns-check/) | DNS record verification — A, AAAA, MX, TXT, CNAME lookups |
| 38 | [dargslan-dns-resolver](https://pypi.org/project/dargslan-dns-resolver/) | DNS resolver analysis — nameserver testing, resolution performance |
| 39 | [dargslan-resolv-check](https://pypi.org/project/dargslan-resolv-check/) | resolv.conf checker — nameserver configuration, search domains |
| 40 | [dargslan-bandwidth-monitor](https://pypi.org/project/dargslan-bandwidth-monitor/) | Network bandwidth monitor — per-interface throughput tracking |
| 41 | [dargslan-interface-monitor](https://pypi.org/project/dargslan-interface-monitor/) | Network interface status — link state, speed, errors, traffic |
| 42 | [dargslan-ssl-checker](https://pypi.org/project/dargslan-ssl-checker/) | SSL certificate validator — expiry, chain, cipher analysis |
| 43 | [dargslan-ip-geo](https://pypi.org/project/dargslan-ip-geo/) | IP geolocation lookup — country, city, ISP, ASN |
| 44 | [dargslan-tcp-monitor](https://pypi.org/project/dargslan-tcp-monitor/) | TCP connection monitor — established, TIME_WAIT, connection states |
| 45 | [dargslan-socket-stats](https://pypi.org/project/dargslan-socket-stats/) | Socket statistics — summary by protocol, state, per-process |
| 46 | [dargslan-network-latency](https://pypi.org/project/dargslan-network-latency/) | Network latency tester — ping, traceroute, jitter analysis |
| 47 | [dargslan-route-check](https://pypi.org/project/dargslan-route-check/) | Routing table analyzer — routes, gateways, default route, policy |
| 48 | [dargslan-hostname-check](https://pypi.org/project/dargslan-hostname-check/) | Hostname & DNS identity — FQDN, reverse DNS, /etc/hosts check |
| 49 | [dargslan-hostname-info](https://pypi.org/project/dargslan-hostname-info/) | Hostname information utility — system identity, domain details |
| 50 | [dargslan-bridge-monitor](https://pypi.org/project/dargslan-bridge-monitor/) | Network bridge monitor — Linux bridges, VLANs, virtual switching |

### 🔥 Firewall & Network Security (3 tools)

| # | Tool | Description |
|---|------|-------------|
| 51 | [dargslan-iptables-export](https://pypi.org/project/dargslan-iptables-export/) | iptables rule exporter — backup, diff, migration to nftables |
| 52 | [dargslan-netfilter-check](https://pypi.org/project/dargslan-netfilter-check/) | Netfilter conntrack analyzer — connection tracking, NAT, chains |
| 53 | [dargslan-arp-monitor](https://pypi.org/project/dargslan-arp-monitor/) | ARP table monitor — cache, duplicate MAC detection, spoofing alerts |

### 📊 Log Analysis (7 tools)

| # | Tool | Description |
|---|------|-------------|
| 54 | [dargslan-log-parser](https://pypi.org/project/dargslan-log-parser/) | Multi-format log parser — syslog, auth.log, nginx, Apache |
| 55 | [dargslan-journald-analyzer](https://pypi.org/project/dargslan-journald-analyzer/) | Systemd journal analyzer — priority filtering, unit analysis |
| 56 | [dargslan-journal-export](https://pypi.org/project/dargslan-journal-export/) | Journal log exporter — stats, priorities, time-range export |
| 57 | [dargslan-dmesg-analyzer](https://pypi.org/project/dargslan-dmesg-analyzer/) | Kernel dmesg analyzer — hardware errors, OOM, storage failures |
| 58 | [dargslan-log-rotate](https://pypi.org/project/dargslan-log-rotate/) | Logrotate config validator — rotation rules, compression, paths |
| 59 | [dargslan-log-stats](https://pypi.org/project/dargslan-log-stats/) | Log statistics — line counts, growth rates, size tracking |
| 60 | [dargslan-nginx-analyzer](https://pypi.org/project/dargslan-nginx-analyzer/) | Nginx log analyzer — access patterns, error rates, top IPs |

### ⚙️ System Configuration (17 tools)

| # | Tool | Description |
|---|------|-------------|
| 61 | [dargslan-crontab-backup](https://pypi.org/project/dargslan-crontab-backup/) | Crontab backup & restore — export, diff, system cron jobs |
| 62 | [dargslan-cron-audit](https://pypi.org/project/dargslan-cron-audit/) | Cron job auditing — schedule analysis, permission checks |
| 63 | [dargslan-cron-parser](https://pypi.org/project/dargslan-cron-parser/) | Cron expression parser — schedule validation, next-run calculation |
| 64 | [dargslan-systemd-timer](https://pypi.org/project/dargslan-systemd-timer/) | Systemd timer analyzer — active timers, calendar expressions |
| 65 | [dargslan-systemd-analyze](https://pypi.org/project/dargslan-systemd-analyze/) | Systemd boot analyzer — startup time, service bottlenecks |
| 66 | [dargslan-systemd-unit](https://pypi.org/project/dargslan-systemd-unit/) | Systemd unit manager — unit status, dependencies, overrides |
| 67 | [dargslan-grub-check](https://pypi.org/project/dargslan-grub-check/) | GRUB bootloader validator — kernel entries, boot parameters |
| 68 | [dargslan-fstab-check](https://pypi.org/project/dargslan-fstab-check/) | fstab syntax validator — mount options, UUID verification |
| 69 | [dargslan-locale-check](https://pypi.org/project/dargslan-locale-check/) | Locale & encoding checker — UTF-8, language configuration |
| 70 | [dargslan-timezone-info](https://pypi.org/project/dargslan-timezone-info/) | Timezone & NTP info — clock sync, time zone configuration |
| 71 | [dargslan-ntp-check](https://pypi.org/project/dargslan-ntp-check/) | NTP sync checker — clock offset, stratum, chrony/timesyncd |
| 72 | [dargslan-ulimit-check](https://pypi.org/project/dargslan-ulimit-check/) | Resource limits checker — open files, processes, memory limits |
| 73 | [dargslan-kernel-module](https://pypi.org/project/dargslan-kernel-module/) | Kernel module manager — lsmod, modinfo, unused module detection |
| 74 | [dargslan-kernel-check](https://pypi.org/project/dargslan-kernel-check/) | Kernel version checker — config, available updates, parameters |
| 75 | [dargslan-motd-manager](https://pypi.org/project/dargslan-motd-manager/) | MOTD manager — login banners, dynamic system info display |
| 76 | [dargslan-at-scheduler](https://pypi.org/project/dargslan-at-scheduler/) | at/batch scheduler auditor — pending jobs, access control |
| 77 | [dargslan-modprobe-check](https://pypi.org/project/dargslan-modprobe-check/) | Kernel module & blacklist checker — loaded modules, security audit |

### 💾 Storage & Filesystems (11 tools)

| # | Tool | Description |
|---|------|-------------|
| 78 | [dargslan-disk-cleaner](https://pypi.org/project/dargslan-disk-cleaner/) | Disk space cleaner — find large files, old logs, cache cleanup |
| 79 | [dargslan-disk-benchmark](https://pypi.org/project/dargslan-disk-benchmark/) | Disk I/O benchmarking — sequential/random read/write speed |
| 80 | [dargslan-disk-quota](https://pypi.org/project/dargslan-disk-quota/) | Disk quota manager — user/group quotas, usage reporting |
| 81 | [dargslan-disk-health](https://pypi.org/project/dargslan-disk-health/) | Disk health monitor — SMART data, I/O errors, wear level |
| 82 | [dargslan-lvm-check](https://pypi.org/project/dargslan-lvm-check/) | LVM volume checker — VGs, LVs, PVs, free space analysis |
| 83 | [dargslan-raid-monitor](https://pypi.org/project/dargslan-raid-monitor/) | RAID array monitor — mdadm status, degraded detection |
| 84 | [dargslan-nfs-health](https://pypi.org/project/dargslan-nfs-health/) | NFS share health checker — mount status, stale detection |
| 85 | [dargslan-tmpfile-cleaner](https://pypi.org/project/dargslan-tmpfile-cleaner/) | Temp file cleaner — /tmp, /var/tmp cleanup and analysis |
| 86 | [dargslan-tmpfile-clean](https://pypi.org/project/dargslan-tmpfile-clean/) | Temporary file analyzer — old files, large files, cache dirs |
| 87 | [dargslan-backup-monitor](https://pypi.org/project/dargslan-backup-monitor/) | Backup file monitor — age verification, size tracking, alerts |
| 88 | [dargslan-xfs-check](https://pypi.org/project/dargslan-xfs-check/) | XFS filesystem health checker — fragmentation, repair, status |

### 🐳 DevOps & Containers (5 tools)

| # | Tool | Description |
|---|------|-------------|
| 89 | [dargslan-docker-health](https://pypi.org/project/dargslan-docker-health/) | Docker health monitor — container status, resource usage, logs |
| 90 | [dargslan-container-audit](https://pypi.org/project/dargslan-container-audit/) | Container security audit — image scanning, privilege checks |
| 91 | [dargslan-cgroup-monitor](https://pypi.org/project/dargslan-cgroup-monitor/) | Cgroup resource monitor — CPU/memory limits, usage tracking |
| 92 | [dargslan-cgroup-audit](https://pypi.org/project/dargslan-cgroup-audit/) | Cgroup v2 auditor — resource limits, slices, controller status |
| 93 | [dargslan-git-audit](https://pypi.org/project/dargslan-git-audit/) | Git repository auditor — large files, secrets, commit hygiene |

### 🗄️ Database Health (3 tools)

| # | Tool | Description |
|---|------|-------------|
| 94 | [dargslan-mysql-health](https://pypi.org/project/dargslan-mysql-health/) | MySQL health monitor — connections, queries, replication status |
| 95 | [dargslan-postgres-health](https://pypi.org/project/dargslan-postgres-health/) | PostgreSQL health monitor — connections, locks, vacuum status |
| 96 | [dargslan-redis-health](https://pypi.org/project/dargslan-redis-health/) | Redis health monitor — memory, connections, persistence status |

### 📦 Package & Service Management (9 tools)

| # | Tool | Description |
|---|------|-------------|
| 97 | [dargslan-apt-history](https://pypi.org/project/dargslan-apt-history/) | APT package history — install/upgrade/remove timeline |
| 98 | [dargslan-apt-check](https://pypi.org/project/dargslan-apt-check/) | APT health checker — broken packages, pending updates |
| 99 | [dargslan-package-audit](https://pypi.org/project/dargslan-package-audit/) | Package security audit — CVE scanning, outdated packages |
| 100 | [dargslan-service-monitor](https://pypi.org/project/dargslan-service-monitor/) | Systemd service monitor — active/failed/inactive services |
| 101 | [dargslan-service-restart](https://pypi.org/project/dargslan-service-restart/) | Service restart monitor — failed services, restart loops |
| 102 | [dargslan-apache-analyzer](https://pypi.org/project/dargslan-apache-analyzer/) | Apache log & config analyzer — vhosts, modules, access logs |
| 103 | [dargslan-cert-manager](https://pypi.org/project/dargslan-cert-manager/) | SSL certificate manager — renewal tracking, expiry alerts |
| 104 | [dargslan-bash-alias](https://pypi.org/project/dargslan-bash-alias/) | Bash alias manager — list, suggest, conflict detection |
| 105 | [dargslan-yum-history](https://pypi.org/project/dargslan-yum-history/) | YUM/DNF package history analyzer — transaction rollback, audit |

### 🔧 System Diagnostics (2 tools)

| # | Tool | Description |
|---|------|-------------|
| 106 | [dargslan-coredump-check](https://pypi.org/project/dargslan-coredump-check/) | Core dump analyzer — crash detection, limits, storage usage |
| 107 | [dargslan-entropy-check](https://pypi.org/project/dargslan-entropy-check/) | System entropy monitor — random pool, crypto readiness, RNG |

---

## 🚀 Quick Start Examples

```bash
# Install the complete toolkit
pip install dargslan-toolkit

# System overview
dargslan-sysinfo

# Security audit
dargslan-firewall-audit
dargslan-ssh-hardening
dargslan-passwd-audit

# Performance monitoring
dargslan-load-average
dargslan-io-monitor
dargslan-proc-monitor

# Network analysis
dargslan-net-scanner
dargslan-port-monitor
dargslan-ssl-checker

# Log analysis
dargslan-log-parser
dargslan-dmesg-analyzer
dargslan-journal-export

# Storage management
dargslan-disk-health
dargslan-disk-cleaner
dargslan-lvm-check
```

---

## ✅ Why dargslan-toolkit?

| Feature | Details |
|---------|---------|
| **107 tools, 1 install** | Everything a Linux sysadmin needs in a single `pip install` |
| **Zero external deps** | Built on Python standard library only |
| **CLI ready** | Every tool works from the terminal immediately |
| **Lightweight** | Minimal footprint, fast execution |
| **Production tested** | Used on real Linux servers and infrastructure |
| **Well documented** | Each tool has its own PyPI page with usage examples |
| **MIT licensed** | Free for personal and commercial use |

---

## 📚 More Resources from Dargslan

| Resource | Link |
|----------|------|
| **210+ Linux & DevOps eBooks** | [dargslan.com/books](https://dargslan.com/books) |
| **380+ Free Cheat Sheets (PDF)** | [dargslan.com/cheat-sheets](https://dargslan.com/cheat-sheets) |
| **430+ Blog Posts & Tutorials** | [dargslan.com/blog](https://dargslan.com/blog) |
| **Free Tools** | [dargslan.com/tools](https://dargslan.com/tools) |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  <strong>Made with care by <a href="https://dargslan.com">Dargslan</a></strong><br>
  Your source for Linux & DevOps knowledge.<br><br>
  <a href="https://dargslan.com">Website</a> •
  <a href="https://dargslan.com/books">eBooks</a> •
  <a href="https://dargslan.com/cheat-sheets">Cheat Sheets</a> •
  <a href="https://dargslan.com/blog">Blog</a>
</p>
