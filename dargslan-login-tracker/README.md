# dargslan-login-tracker

Linux login tracker — SSH session monitoring, failed login detection, brute force alerting, and user session history.

## Installation

```bash
pip install dargslan-login-tracker
```

## Usage

```bash
dargslan-logins report    # Full login tracker report
dargslan-logins active    # Current active sessions
dargslan-logins last      # Recent login history
dargslan-logins failed    # Failed login attempts
dargslan-logins brute     # Brute force detection
dargslan-logins audit     # Issues only
dargslan-logins json      # JSON output
```

## Features

- Current active session monitoring
- SSH connection tracking
- Failed login attempt analysis
- Brute force attack detection (IP and user threshold)
- Root session alerting
- Zero dependencies — pure Python

## Part of dargslan-toolkit

Install all 54 Linux sysadmin tools: `pip install dargslan-toolkit`

## Links

- [Free Linux Cheat Sheets](https://dargslan.com/cheat-sheets)
- [Linux & DevOps Books](https://dargslan.com/books)

## License

MIT
