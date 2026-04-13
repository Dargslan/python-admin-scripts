# dargslan-systemd-unit

Systemd unit file analyzer — syntax validation, security audit, dependency check, and best practice linting.

## Installation

```bash
pip install dargslan-systemd-unit
```

## Usage

```bash
dargslan-unit report              # Scan all unit files
dargslan-unit lint myapp.service  # Lint a specific unit
dargslan-unit security myapp.service  # Security analysis
dargslan-unit parse myapp.service # Parse unit structure
dargslan-unit list                # List all unit files
dargslan-unit json                # JSON output
```

## Features

- Unit file syntax validation
- Security hardening score (16 directives checked)
- Best practice linting (Restart policy, User, PIDFile, etc.)
- Support for .service, .timer, .socket, .mount files
- Zero dependencies — pure Python

## Part of dargslan-toolkit

Install all 54 Linux sysadmin tools: `pip install dargslan-toolkit`

## Links

- [Free Linux Cheat Sheets](https://dargslan.com/cheat-sheets)
- [Linux & DevOps Books](https://dargslan.com/books)

## License

MIT
