#!/usr/bin/env python3
"""System thermal monitor — check CPU temperatures, thermal zones, cooling devices."""

import argparse
import json
import sys
from pathlib import Path


def get_thermal_zones():
    zones = []
    thermal_dir = Path("/sys/class/thermal")
    if not thermal_dir.exists():
        return zones

    for zone_path in sorted(thermal_dir.glob("thermal_zone*")):
        info = {"zone": zone_path.name, "type": None, "temp_c": None, "trips": []}
        try:
            info["type"] = (zone_path / "type").read_text().strip()
        except (FileNotFoundError, PermissionError):
            pass
        try:
            temp = int((zone_path / "temp").read_text().strip())
            info["temp_c"] = temp / 1000.0
        except (FileNotFoundError, PermissionError, ValueError):
            pass

        for i in range(10):
            try:
                trip_type = (zone_path / f"trip_point_{i}_type").read_text().strip()
                trip_temp = int((zone_path / f"trip_point_{i}_temp").read_text().strip()) / 1000.0
                info["trips"].append({"type": trip_type, "temp_c": trip_temp})
            except (FileNotFoundError, PermissionError, ValueError):
                break

        zones.append(info)
    return zones


def get_cooling_devices():
    devices = []
    thermal_dir = Path("/sys/class/thermal")
    for cool_path in sorted(thermal_dir.glob("cooling_device*")):
        info = {"device": cool_path.name, "type": None, "state": None, "max_state": None}
        try:
            info["type"] = (cool_path / "type").read_text().strip()
        except (FileNotFoundError, PermissionError):
            pass
        try:
            info["state"] = (cool_path / "cur_state").read_text().strip()
        except (FileNotFoundError, PermissionError):
            pass
        try:
            info["max_state"] = (cool_path / "max_state").read_text().strip()
        except (FileNotFoundError, PermissionError):
            pass
        devices.append(info)
    return devices


def get_hwmon_temps():
    temps = []
    hwmon_dir = Path("/sys/class/hwmon")
    if not hwmon_dir.exists():
        return temps

    for hw in sorted(hwmon_dir.iterdir()):
        name = None
        try:
            name = (hw / "name").read_text().strip()
        except (FileNotFoundError, PermissionError):
            pass

        for temp_input in sorted(hw.glob("temp*_input")):
            idx = temp_input.stem.replace("temp", "").replace("_input", "")
            label = None
            try:
                label = (hw / f"temp{idx}_label").read_text().strip()
            except (FileNotFoundError, PermissionError):
                pass
            try:
                val = int(temp_input.read_text().strip()) / 1000.0
                temps.append({"sensor": name, "label": label or f"temp{idx}", "temp_c": val})
            except (FileNotFoundError, PermissionError, ValueError):
                pass
    return temps


def main():
    parser = argparse.ArgumentParser(
        description="System thermal monitor",
        epilog="More tools: https://dargslan.com | pip install dargslan-toolkit"
    )
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--warn", type=float, default=80.0, help="Warning threshold (C)")
    parser.add_argument("--crit", type=float, default=95.0, help="Critical threshold (C)")
    args = parser.parse_args()

    zones = get_thermal_zones()
    cooling = get_cooling_devices()
    hwmon = get_hwmon_temps()

    if args.json:
        print(json.dumps({"thermal_zones": zones, "cooling_devices": cooling, "hwmon": hwmon}, indent=2))
        return

    print("\033[1m  Dargslan Thermal Monitor\033[0m\n")

    if hwmon:
        print("  \033[1mHardware Sensors:\033[0m")
        for h in hwmon:
            color = "\033[31m" if h["temp_c"] >= args.crit else "\033[33m" if h["temp_c"] >= args.warn else "\033[32m"
            print(f"    {h['sensor']}/{h['label']}: {color}{h['temp_c']:.1f}C\033[0m")

    if zones:
        print(f"\n  \033[1mThermal Zones ({len(zones)}):\033[0m")
        for z in zones:
            temp = f"{z['temp_c']:.1f}C" if z['temp_c'] is not None else "N/A"
            print(f"    {z['zone']} ({z.get('type', 'unknown')}): {temp}")

    if cooling:
        print(f"\n  \033[1mCooling Devices ({len(cooling)}):\033[0m")
        for c in cooling:
            print(f"    {c['device']} ({c.get('type', 'unknown')}): state {c.get('state', '?')}/{c.get('max_state', '?')}")

    hot = [h for h in hwmon if h["temp_c"] >= args.warn]
    if hot:
        print(f"\n  \033[33m! {len(hot)} sensor(s) above {args.warn}C warning threshold\033[0m")

    print(f"\n  Free cheat sheets: https://dargslan.com/cheat-sheets")


if __name__ == "__main__":
    main()
