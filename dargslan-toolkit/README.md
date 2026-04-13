# 🛠️ dargslan-toolkit

**The Complete Linux Sysadmin Toolkit** — 118 professional CLI tools for Linux server management, security auditing, performance monitoring, and DevOps operations. One install. All tools.

[![PyPI version](https://img.shields.io/pypi/v/dargslan-toolkit)](https://pypi.org/project/dargslan-toolkit/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Tools](https://img.shields.io/badge/tools-118-green.svg)](https://dargslan.com)

---

## ⚡ Quick Install

```bash
pip install dargslan-toolkit
```

One command installs **all 118 CLI tools** — ready to use immediately from your terminal.

---

## 📋 Complete Tool Reference

### 🖥️ System Monitoring & Performance (16 tools)

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
| 15 | [dargslan-cpu-freq](https://pypi.org/project/dargslan-cpu-freq/) | CPU frequency & governor monitor — scaling, turbo boost, power states |
| 16 | [dargslan-thermal-monitor](https://pypi.org/project/dargslan-thermal-monitor/) | Thermal zone monitor — CPU/GPU temps, fan speeds, throttling alerts |

### 🔒 Security & Hardening (23 tools)

| # | Tool | Description |
|---|------|-------------|
| 17 | [dargslan-firewall-audit](https://pypi.org/project/dargslan-firewall-audit/) | iptables/nftables rule auditing — open ports, default policies |
| 18 | [dargslan-ssh-hardening](https://pypi.org/project/dargslan-ssh-hardening/) | SSH server hardening — sshd_config audit, root login, key auth |
| 19 | [dargslan-ssh-audit](https://pypi.org/project/dargslan-ssh-audit/) | SSH server & key auditing — algorithms, ciphers, key strength |
| 20 | [dargslan-sshkey-audit](https://pypi.org/project/dargslan-sshkey-audit/) | SSH key auditor — authorized_keys scan, weak keys, key sprawl |
| 21 | [dargslan-sudoers-audit](https://pypi.org/project/dargslan-sudoers-audit/) | Sudoers file analysis — NOPASSWD detection, privilege escalation |
| 22 | [dargslan-pam-audit](https://pypi.org/project/dargslan-pam-audit/) | PAM configuration auditing — auth modules, password policies |
| 23 | [dargslan-sysctl-audit](https://pypi.org/project/dargslan-sysctl-audit/) | Kernel parameter audit — security hardening, network settings |
| 24 | [dargslan-env-audit](https://pypi.org/project/dargslan-env-audit/) | Environment variable security — leaked secrets, PATH analysis |
| 25 | [dargslan-file-integrity](https://pypi.org/project/dargslan-file-integrity/) | File integrity monitoring — checksum tracking, change detection |
| 26 | [dargslan-acl-check](https://pypi.org/project/dargslan-acl-check/) | File ACL & permission checker — SUID, world-writable, POSIX ACLs |
| 27 | [dargslan-audit-log](https://pypi.org/project/dargslan-audit-log/) | Auditd log analyzer — file access, privilege escalation, user activity |
| 28 | [dargslan-login-history](https://pypi.org/project/dargslan-login-history/) | Login history — wtmp/btmp analysis, failed attempts, session tracking |
| 29 | [dargslan-login-tracker](https://pypi.org/project/dargslan-login-tracker/) | Login session tracker — active sessions, IP tracking, brute force |
| 30 | [dargslan-lastlog-audit](https://pypi.org/project/dargslan-lastlog-audit/) | Last login audit — dormant accounts, never-logged-in users |
| 31 | [dargslan-passwd-audit](https://pypi.org/project/dargslan-passwd-audit/) | Password policy auditor — shadow file, empty passwords, aging |
| 32 | [dargslan-security-scan](https://pypi.org/project/dargslan-security-scan/) | General security scanner — comprehensive system hardening check |
| 33 | [dargslan-selinux-check](https://pypi.org/project/dargslan-selinux-check/) | SELinux status checker — mode, policy, booleans, denials |
| 34 | [dargslan-user-audit](https://pypi.org/project/dargslan-user-audit/) | User account auditing — UID 0 check, shell assignment, groups |
| 35 | [dargslan-apparmor-check](https://pypi.org/project/dargslan-apparmor-check/) | AppArmor profile status checker — enforcement mode, violations |
| 36 | [dargslan-lsof-audit](https://pypi.org/project/dargslan-lsof-audit/) | Open files & ports auditor — lsof analysis, deleted files, connections |
| 37 | [dargslan-ipv6-audit](https://pypi.org/project/dargslan-ipv6-audit/) | IPv6 configuration auditor — dual-stack, privacy extensions, router ads |
| 38 | [dargslan-fail2ban-audit](https://pypi.org/project/dargslan-fail2ban-audit/) | Fail2ban status checker — jail configs, banned IPs, filter audit |
| 39 | [dargslan-crypt-audit](https://pypi.org/project/dargslan-crypt-audit/) | Encryption audit — LUKS volumes, dm-crypt, key management check |

### 🌐 Networking & DNS (19 tools)

| # | Tool | Description |
|---|------|-------------|
| 40 | [dargslan-net-scanner](https://pypi.org/project/dargslan-net-scanner/) | Network scanner — ping sweep, port scanning, service detection |
| 41 | [dargslan-port-monitor](https://pypi.org/project/dargslan-port-monitor/) | Listening port monitor — open ports, bound services, PID mapping |
| 42 | [dargslan-dns-check](https://pypi.org/project/dargslan-dns-check/) | DNS record verification — A, AAAA, MX, TXT, CNAME lookups |
| 43 | [dargslan-dns-resolver](https://pypi.org/project/dargslan-dns-resolver/) | DNS resolver analysis — nameserver testing, resolution performance |
| 44 | [dargslan-resolv-check](https://pypi.org/project/dargslan-resolv-check/) | resolv.conf checker — nameserver configuration, search domains |
| 45 | [dargslan-bandwidth-monitor](https://pypi.org/project/dargslan-bandwidth-monitor/) | Network bandwidth monitor — per-interface throughput tracking |
| 46 | [dargslan-interface-monitor](https://pypi.org/project/dargslan-interface-monitor/) | Network interface status — link state, speed, errors, traffic |
| 47 | [dargslan-ssl-checker](https://pypi.org/project/dargslan-ssl-checker/) | SSL certificate validator — expiry, chain, cipher analysis |
| 48 | [dargslan-ip-geo](https://pypi.org/project/dargslan-ip-geo/) | IP geolocation lookup — country, city, ISP, ASN |
| 49 | [dargslan-tcp-monitor](https://pypi.org/project/dargslan-tcp-monitor/) | TCP connection monitor — established, TIME_WAIT, connection states |
| 50 | [dargslan-socket-stats](https://pypi.org/project/dargslan-socket-stats/) | Socket statistics — summary by protocol, state, per-process |
| 51 | [dargslan-network-latency](https://pypi.org/project/dargslan-network-latency/) | Network latency tester — ping, traceroute, jitter analysis |
| 52 | [dargslan-route-check](https://pypi.org/project/dargslan-route-check/) | Routing table analyzer — routes, gateways, default route, policy |
| 53 | [dargslan-hostname-check](https://pypi.org/project/dargslan-hostname-check/) | Hostname & DNS identity — FQDN, reverse DNS, /etc/hosts check |
| 54 | [dargslan-hostname-info](https://pypi.org/project/dargslan-hostname-info/) | Hostname information utility — system identity, domain details |
| 55 | [dargslan-bridge-monitor](https://pypi.org/project/dargslan-bridge-monitor/) | Network bridge monitor — Linux bridges, VLANs, virtual switching |
| 56 | [dargslan-ethtool-check](https://pypi.org/project/dargslan-ethtool-check/) | Network interface diagnostics — ethtool stats, driver info, link status |
| 57 | [dargslan-bonding-check](https://pypi.org/project/dargslan-bonding-check/) | Network bonding checker — bond mode, slave status, LACP, failover |
| 58 | [dargslan-snmp-check](https://pypi.org/project/dargslan-snmp-check/) | SNMP configuration auditor — community strings, v3 auth, MIB walk |

### 🔥 Firewall & Network Security (3 tools)

| # | Tool | Description |
|---|------|-------------|
| 59 | [dargslan-iptables-export](https://pypi.org/project/dargslan-iptables-export/) | iptables rule exporter — backup, diff, migration to nftables |
| 60 | [dargslan-netfilter-check](https://pypi.org/project/dargslan-netfilter-check/) | Netfilter conntrack analyzer — connection tracking, NAT, chains |
| 61 | [dargslan-arp-monitor](https://pypi.org/project/dargslan-arp-monitor/) | ARP table monitor — cache, duplicate MAC detection, spoofing alerts |

### 📊 Log Analysis (8 tools)

| # | Tool | Description |
|---|------|-------------|
| 62 | [dargslan-log-parser](https://pypi.org/project/dargslan-log-parser/) | Multi-format log parser — syslog, auth.log, nginx, Apache |
| 63 | [dargslan-journald-analyzer](https://pypi.org/project/dargslan-journald-analyzer/) | Systemd journal analyzer — priority filtering, unit analysis |
| 64 | [dargslan-journal-export](https://pypi.org/project/dargslan-journal-export/) | Journal log exporter — stats, priorities, time-range export |
| 65 | [dargslan-dmesg-analyzer](https://pypi.org/project/dargslan-dmesg-analyzer/) | Kernel dmesg analyzer — hardware errors, OOM, storage failures |
| 66 | [dargslan-log-rotate](https://pypi.org/project/dargslan-log-rotate/) | Logrotate config validator — rotation rules, compression, paths |
| 67 | [dargslan-log-stats](https://pypi.org/project/dargslan-log-stats/) | Log statistics — line counts, growth rates, size tracking |
| 68 | [dargslan-nginx-analyzer](https://pypi.org/project/dargslan-nginx-analyzer/) | Nginx log analyzer — access patterns, error rates, top IPs |
| 69 | [dargslan-syslog-monitor](https://pypi.org/project/dargslan-syslog-monitor/) | Syslog monitor — rsyslog/syslog-ng config audit, facility analysis |

### ⚙️ System Configuration (17 tools)

| # | Tool | Description |
|---|------|-------------|
| 70 | [dargslan-crontab-backup](https://pypi.org/project/dargslan-crontab-backup/) | Crontab backup & restore — export, diff, system cron jobs |
| 71 | [dargslan-cron-audit](https://pypi.org/project/dargslan-cron-audit/) | Cron job auditing — schedule analysis, permission checks |
| 72 | [dargslan-cron-parser](https://pypi.org/project/dargslan-cron-parser/) | Cron expression parser — schedule validation, next-run calculation |
| 73 | [dargslan-systemd-timer](https://pypi.org/project/dargslan-systemd-timer/) | Systemd timer analyzer — active timers, calendar expressions |
| 74 | [dargslan-systemd-analyze](https://pypi.org/project/dargslan-systemd-analyze/) | Systemd boot analyzer — startup time, service bottlenecks |
| 75 | [dargslan-systemd-unit](https://pypi.org/project/dargslan-systemd-unit/) | Systemd unit manager — unit status, dependencies, overrides |
| 76 | [dargslan-grub-check](https://pypi.org/project/dargslan-grub-check/) | GRUB bootloader validator — kernel entries, boot parameters |
| 77 | [dargslan-fstab-check](https://pypi.org/project/dargslan-fstab-check/) | fstab syntax validator — mount options, UUID verification |
| 78 | [dargslan-locale-check](https://pypi.org/project/dargslan-locale-check/) | Locale & encoding checker — UTF-8, language configuration |
| 79 | [dargslan-timezone-info](https://pypi.org/project/dargslan-timezone-info/) | Timezone & NTP info — clock sync, time zone configuration |
| 80 | [dargslan-ntp-check](https://pypi.org/project/dargslan-ntp-check/) | NTP sync checker — clock offset, stratum, chrony/timesyncd |
| 81 | [dargslan-ulimit-check](https://pypi.org/project/dargslan-ulimit-check/) | Resource limits checker — open files, processes, memory limits |
| 82 | [dargslan-kernel-module](https://pypi.org/project/dargslan-kernel-module/) | Kernel module manager — lsmod, modinfo, unused module detection |
| 83 | [dargslan-kernel-check](https://pypi.org/project/dargslan-kernel-check/) | Kernel version checker — config, available updates, parameters |
| 84 | [dargslan-motd-manager](https://pypi.org/project/dargslan-motd-manager/) | MOTD manager — login banners, dynamic system info display |
| 85 | [dargslan-at-scheduler](https://pypi.org/project/dargslan-at-scheduler/) | at/batch scheduler auditor — pending jobs, access control |
| 86 | [dargslan-modprobe-check](https://pypi.org/project/dargslan-modprobe-check/) | Kernel module & blacklist checker — loaded modules, security audit |

### 💾 Storage & Filesystems (12 tools)

| # | Tool | Description |
|---|------|-------------|
| 87 | [dargslan-disk-cleaner](https://pypi.org/project/dargslan-disk-cleaner/) | Disk space cleaner — find large files, old logs, cache cleanup |
| 88 | [dargslan-disk-benchmark](https://pypi.org/project/dargslan-disk-benchmark/) | Disk I/O benchmarking — sequential/random read/write speed |
| 89 | [dargslan-disk-quota](https://pypi.org/project/dargslan-disk-quota/) | Disk quota manager — user/group quotas, usage reporting |
| 90 | [dargslan-disk-health](https://pypi.org/project/dargslan-disk-health/) | Disk health monitor — SMART data, I/O errors, wear level |
| 91 | [dargslan-lvm-check](https://pypi.org/project/dargslan-lvm-check/) | LVM volume checker — VGs, LVs, PVs, free space analysis |
| 92 | [dargslan-raid-monitor](https://pypi.org/project/dargslan-raid-monitor/) | RAID array monitor — mdadm status, degraded detection |
| 93 | [dargslan-nfs-health](https://pypi.org/project/dargslan-nfs-health/) | NFS share health checker — mount status, stale detection |
| 94 | [dargslan-tmpfile-cleaner](https://pypi.org/project/dargslan-tmpfile-cleaner/) | Temp file cleaner — /tmp, /var/tmp cleanup and analysis |
| 95 | [dargslan-tmpfile-clean](https://pypi.org/project/dargslan-tmpfile-clean/) | Temporary file analyzer — old files, large files, cache dirs |
| 96 | [dargslan-backup-monitor](https://pypi.org/project/dargslan-backup-monitor/) | Backup file monitor — age verification, size tracking, alerts |
| 97 | [dargslan-xfs-check](https://pypi.org/project/dargslan-xfs-check/) | XFS filesystem health checker — fragmentation, repair, status |
| 98 | [dargslan-btrfs-check](https://pypi.org/project/dargslan-btrfs-check/) | Btrfs filesystem checker — subvolumes, snapshots, scrub, balance |

### 🐳 DevOps & Containers (5 tools)

| # | Tool | Description |
|---|------|-------------|
| 99 | [dargslan-docker-health](https://pypi.org/project/dargslan-docker-health/) | Docker health monitor — container status, resource usage, logs |
| 100 | [dargslan-container-audit](https://pypi.org/project/dargslan-container-audit/) | Container security audit — image scanning, privilege checks |
| 101 | [dargslan-cgroup-monitor](https://pypi.org/project/dargslan-cgroup-monitor/) | Cgroup resource monitor — CPU/memory limits, usage tracking |
| 102 | [dargslan-cgroup-audit](https://pypi.org/project/dargslan-cgroup-audit/) | Cgroup v2 auditor — resource limits, slices, controller status |
| 103 | [dargslan-git-audit](https://pypi.org/project/dargslan-git-audit/) | Git repository auditor — large files, secrets, commit hygiene |

### 🗄️ Database Health (3 tools)

| # | Tool | Description |
|---|------|-------------|
| 104 | [dargslan-mysql-health](https://pypi.org/project/dargslan-mysql-health/) | MySQL health monitor — connections, queries, replication status |
| 105 | [dargslan-postgres-health](https://pypi.org/project/dargslan-postgres-health/) | PostgreSQL health monitor — connections, locks, vacuum status |
| 106 | [dargslan-redis-health](https://pypi.org/project/dargslan-redis-health/) | Redis health monitor — memory, connections, persistence status |

### 📦 Package & Service Management (10 tools)

| # | Tool | Description |
|---|------|-------------|
| 107 | [dargslan-apt-history](https://pypi.org/project/dargslan-apt-history/) | APT package history — install/upgrade/remove timeline |
| 108 | [dargslan-apt-check](https://pypi.org/project/dargslan-apt-check/) | APT health checker — broken packages, pending updates |
| 109 | [dargslan-package-audit](https://pypi.org/project/dargslan-package-audit/) | Package security audit — CVE scanning, outdated packages |
| 110 | [dargslan-service-monitor](https://pypi.org/project/dargslan-service-monitor/) | Systemd service monitor — active/failed/inactive services |
| 111 | [dargslan-service-restart](https://pypi.org/project/dargslan-service-restart/) | Service restart monitor — failed services, restart loops |
| 112 | [dargslan-apache-analyzer](https://pypi.org/project/dargslan-apache-analyzer/) | Apache log & config analyzer — vhosts, modules, access logs |
| 113 | [dargslan-cert-manager](https://pypi.org/project/dargslan-cert-manager/) | SSL certificate manager — renewal tracking, expiry alerts |
| 114 | [dargslan-bash-alias](https://pypi.org/project/dargslan-bash-alias/) | Bash alias manager — list, suggest, conflict detection |
| 115 | [dargslan-yum-history](https://pypi.org/project/dargslan-yum-history/) | YUM/DNF package history analyzer — transaction rollback, audit |
| 116 | [dargslan-numa-check](https://pypi.org/project/dargslan-numa-check/) | NUMA topology checker — node mapping, memory affinity, CPU pinning |

### 🔧 System Diagnostics (2 tools)

| # | Tool | Description |
|---|------|-------------|
| 117 | [dargslan-coredump-check](https://pypi.org/project/dargslan-coredump-check/) | Core dump analyzer — crash detection, limits, storage usage |
| 118 | [dargslan-entropy-check](https://pypi.org/project/dargslan-entropy-check/) | System entropy monitor — random pool, crypto readiness, RNG |

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
dargslan-fail2ban-audit
dargslan-crypt-audit

# Performance monitoring
dargslan-load-average
dargslan-io-monitor
dargslan-proc-monitor
dargslan-cpu-freq
dargslan-thermal-monitor

# Network analysis
dargslan-net-scanner
dargslan-port-monitor
dargslan-ssl-checker
dargslan-bonding-check
dargslan-snmp-check

# Log analysis
dargslan-log-parser
dargslan-dmesg-analyzer
dargslan-journal-export
dargslan-syslog-monitor

# Storage management
dargslan-disk-health
dargslan-disk-cleaner
dargslan-lvm-check
dargslan-btrfs-check
```

---

## ✅ Why dargslan-toolkit?

| Feature | Details |
|---------|---------|
| **118 tools, 1 install** | Everything a Linux sysadmin needs in a single `pip install` |
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
| **384+ Free Cheat Sheets (PDF)** | [dargslan.com/cheat-sheets](https://dargslan.com/cheat-sheets) |
| **433+ Blog Posts & Tutorials** | [dargslan.com/blog](https://dargslan.com/blog) |
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
