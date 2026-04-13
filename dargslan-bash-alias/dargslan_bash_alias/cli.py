#!/usr/bin/env python3
"""Bash Alias Manager - Manage and analyze bash aliases."""

import subprocess
import os
import argparse
import re


def get_aliases():
    out, err = subprocess.Popen(
        ["bash", "-ic", "alias"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    ).communicate()
    aliases = {}
    for line in out.decode().strip().split("\n"):
        match = re.match(r"alias\s+(\S+?)='(.+)'$", line)
        if match:
            aliases[match.group(1)] = match.group(2)
    return aliases


def list_aliases():
    print("=== Current Bash Aliases ===")
    aliases = get_aliases()
    if aliases:
        max_name = max(len(k) for k in aliases) if aliases else 10
        for name, cmd in sorted(aliases.items()):
            print(f"  {name:<{max_name+2}} -> {cmd}")
        print(f"\nTotal aliases: {len(aliases)}")
    else:
        print("  No aliases found")


def suggest_aliases():
    print("=== Suggested Linux Aliases ===")
    suggestions = {
        "ll": "ls -alF",
        "la": "ls -A",
        "..": "cd ..",
        "...": "cd ../..",
        "grep": "grep --color=auto",
        "df": "df -h",
        "du": "du -h",
        "free": "free -h",
        "ports": "netstat -tulanp",
        "myip": "curl -s ifconfig.me",
        "cls": "clear",
        "h": "history",
        "mkdir": "mkdir -pv",
        "ping": "ping -c 5",
        "psg": "ps aux | grep -v grep | grep -i",
    }
    existing = get_aliases()
    max_name = max(len(k) for k in suggestions)
    for name, cmd in suggestions.items():
        status = " [EXISTS]" if name in existing else ""
        print(f"  alias {name:<{max_name+2}}='{cmd}'{status}")


def check_conflicts():
    print("=== Alias Conflict Check ===")
    aliases = get_aliases()
    conflicts = 0
    for name in aliases:
        result = subprocess.run(
            ["bash", "-c", f"type -t {name} 2>/dev/null"],
            capture_output=True, text=True
        )
        builtin_type = result.stdout.strip()
        if builtin_type in ("file", "builtin", "keyword"):
            print(f"  WARNING: '{name}' shadows a {builtin_type}")
            conflicts += 1
    if conflicts == 0:
        print("  No conflicts found")
    else:
        print(f"\n  Total conflicts: {conflicts}")


def find_alias_files():
    print("=== Alias Configuration Files ===")
    home = os.path.expanduser("~")
    files = [".bashrc", ".bash_aliases", ".bash_profile", ".profile", ".zshrc"]
    for f in files:
        path = os.path.join(home, f)
        if os.path.exists(path):
            count = 0
            with open(path) as fh:
                for line in fh:
                    if line.strip().startswith("alias "):
                        count += 1
            print(f"  {path}: {count} aliases defined")


def main():
    parser = argparse.ArgumentParser(description="Bash Alias Manager")
    parser.add_argument("--list", action="store_true", help="List current aliases")
    parser.add_argument("--suggest", action="store_true", help="Suggest useful aliases")
    parser.add_argument("--conflicts", action="store_true", help="Check for alias conflicts")
    parser.add_argument("--files", action="store_true", help="Find alias configuration files")
    args = parser.parse_args()

    print("Bash Alias Manager")
    print("=" * 40)

    if args.list:
        list_aliases()
    elif args.suggest:
        suggest_aliases()
    elif args.conflicts:
        check_conflicts()
    elif args.files:
        find_alias_files()
    else:
        list_aliases()
        print()
        suggest_aliases()
        print()
        find_alias_files()

    print("\n" + "=" * 40)
    print("Powered by dargslan.com")


if __name__ == "__main__":
    main()
