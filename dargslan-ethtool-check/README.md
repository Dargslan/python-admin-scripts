# dargslan-ethtool-check

Network interface diagnostics tool — check link speed, duplex mode, driver info, offload settings, and NIC capabilities for all interfaces.

Part of the [Dargslan Linux Admin Toolkit](https://dargslan.com) — 108+ professional CLI tools for system administrators.

## Installation

```bash
pip install dargslan-ethtool-check
```

## Usage

```bash
# Check all network interfaces
dargslan-ethtool-check

# Check specific interface
dargslan-ethtool-check -i eth0

# Verbose with traffic stats
dargslan-ethtool-check -v

# Show only interfaces with errors
dargslan-ethtool-check --errors-only

# Summary table only
dargslan-ethtool-check --summary

# JSON output
dargslan-ethtool-check --json
```

## What It Checks

- **Link Speed & Duplex** — 10/100/1000/10000 Mbps, half/full duplex
- **Driver & Firmware** — NIC driver name, firmware version
- **Link Status** — carrier detect, auto-negotiation state
- **Traffic Statistics** — RX/TX bytes, packets, errors, drops
- **MAC Address & MTU** — interface identification

## Example Output

```
  Interface: eth0  [UP]
  MAC Address      : aa:bb:cc:dd:ee:ff
  MTU              : 1500
  Link Speed       : 1 Gbps (1000 Mbps)
  Duplex           : Full
  Driver           : virtio_net
  Link Detected    : yes
  Auto-negotiation : off
```

## More Tools

- **[dargslan-toolkit](https://pypi.org/project/dargslan-toolkit/)** — All 108+ tools in one install
- **[Free Cheat Sheets](https://dargslan.com/cheat-sheets)** — 380+ Linux & DevOps cheat sheets
- **[Blog & Tutorials](https://dargslan.com/blog)** — 430+ Linux admin guides

## License

MIT — [dargslan.com](https://dargslan.com)
