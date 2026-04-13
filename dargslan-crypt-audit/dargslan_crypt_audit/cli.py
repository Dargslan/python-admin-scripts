#!/usr/bin/env python3
"""LUKS and dm-crypt encryption auditor — check encrypted volumes, key slots, cipher."""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return result.stdout.strip() if result.returncode == 0 else None
    except (FileNotFoundError, subprocess.TimeoutExpired, PermissionError):
        return None


def get_dm_crypt_devices():
    devices = []
    dm_dir = Path("/sys/block")
    if not dm_dir.exists():
        return devices

    for dev in dm_dir.iterdir():
        if dev.name.startswith("dm-"):
            uuid_path = dev / "dm" / "uuid"
            try:
                uuid = uuid_path.read_text().strip()
                if uuid.startswith("CRYPT-"):
                    name_path = dev / "dm" / "name"
                    name = name_path.read_text().strip() if name_path.exists() else dev.name
                    devices.append({"dm_device": dev.name, "name": name, "uuid": uuid})
            except (FileNotFoundError, PermissionError):
                pass

    try:
        result = subprocess.run(["dmsetup", "table", "--target", "crypt"],
                                capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            for line in result.stdout.strip().splitlines():
                parts = line.split(":")
                if len(parts) >= 2:
                    name = parts[0].strip()
                    if not any(d["name"] == name for d in devices):
                        devices.append({"dm_device": "N/A", "name": name, "uuid": "N/A"})
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return devices


def get_luks_info(device_path):
    info = {"device": device_path, "version": None, "cipher": None,
            "key_size": None, "key_slots": [], "status": "unknown"}

    dump = run_cmd(["cryptsetup", "luksDump", device_path])
    if dump:
        for line in dump.splitlines():
            line = line.strip()
            if line.startswith("Version:"):
                info["version"] = line.split(":", 1)[1].strip()
            elif line.startswith("Cipher name:") or line.startswith("Cipher:"):
                info["cipher"] = line.split(":", 1)[1].strip()
            elif line.startswith("Cipher mode:"):
                if info["cipher"]:
                    info["cipher"] += "-" + line.split(":", 1)[1].strip()
            elif "Key Slot" in line and "ENABLED" in line.upper():
                info["key_slots"].append(line.strip())
            elif line.startswith("MK bits:") or line.startswith("Key:"):
                info["key_size"] = line.split(":", 1)[1].strip()

    return info


def main():
    parser = argparse.ArgumentParser(
        description="LUKS and dm-crypt encryption auditor",
        epilog="More tools: https://dargslan.com | pip install dargslan-toolkit"
    )
    parser.add_argument("-d", "--device", help="Check specific device (e.g., /dev/sda2)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    dm_devices = get_dm_crypt_devices()

    if args.json:
        result = {"dm_crypt_devices": dm_devices}
        if args.device:
            result["luks_info"] = get_luks_info(args.device)
        print(json.dumps(result, indent=2))
        return

    print("\033[1m  Dargslan Crypt Audit\033[0m\n")

    if dm_devices:
        print(f"  \033[1mdm-crypt Devices ({len(dm_devices)}):\033[0m")
        for d in dm_devices:
            print(f"    {d['name']} (dm: {d['dm_device']}) — {d['uuid']}")
    else:
        print("  No dm-crypt devices found.")

    if args.device:
        luks = get_luks_info(args.device)
        print(f"\n  \033[1mLUKS Info ({args.device}):\033[0m")
        print(f"    Version: {luks.get('version', 'N/A')}")
        print(f"    Cipher: {luks.get('cipher', 'N/A')}")
        print(f"    Key Size: {luks.get('key_size', 'N/A')}")
        if luks["key_slots"]:
            print(f"    Active Key Slots: {len(luks['key_slots'])}")
            for slot in luks["key_slots"]:
                print(f"      {slot}")

    print(f"\n  Free cheat sheets: https://dargslan.com/cheat-sheets")


if __name__ == "__main__":
    main()
