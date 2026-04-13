# dargslan-socket-stats

Linux socket statistics analyzer — TCP/UDP/Unix socket states, connection tracking, listening ports, and network diagnostics.

## Installation

```bash
pip install dargslan-socket-stats
```

## Usage

```bash
dargslan-socket report        # Full socket statistics report
dargslan-socket tcp           # TCP connections
dargslan-socket udp           # UDP sockets
dargslan-socket listen        # Listening sockets
dargslan-socket states        # TCP state breakdown
dargslan-socket audit         # Issues only
dargslan-socket json          # JSON output
```

## Features

- TCP connection state analysis (ESTABLISHED, TIME-WAIT, CLOSE-WAIT)
- UDP socket listing with process info
- Listening socket inventory
- Detect high TIME-WAIT and CLOSE-WAIT counts
- Receive queue overflow detection
- Zero dependencies — pure Python

## Part of dargslan-toolkit

Install all 48 Linux sysadmin tools: `pip install dargslan-toolkit`

## Links

- [Free Linux Cheat Sheets](https://dargslan.com/cheat-sheets)
- [Linux & DevOps Books](https://dargslan.com/books)
- [Blog & Tutorials](https://dargslan.com/blog)

## License

MIT
