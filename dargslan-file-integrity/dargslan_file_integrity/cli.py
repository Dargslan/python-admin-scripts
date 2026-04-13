"""CLI for dargslan-file-integrity."""

import sys
import json
from . import generate_report, scan_paths, create_baseline, compare_with_baseline, hash_file, audit, __version__, BASELINE_FILE


def print_report(data):
    print(f"File Integrity Report")
    print(f"{'=' * 60}")
    print(f"Timestamp: {data['timestamp']}")
    print(f"Files Scanned: {data['files_scanned']}")
    print(f"Files Accessible: {data['files_accessible']}")
    print()

    comp = data.get("comparison")
    if comp:
        print(f"Baseline Comparison:")
        print(f"  Baseline Date: {comp.get('baseline_date', 'N/A')}")
        print(f"  Total Changes: {comp.get('total_changes', 0)}")
        changes = comp.get("changes", {})
        if changes.get("modified"):
            print(f"\n  Modified Files ({len(changes['modified'])}):")
            for m in changes["modified"]:
                print(f"    {m['path']}")
                print(f"      {m['old_hash']}... → {m['new_hash']}...")
        if changes.get("added"):
            print(f"\n  New Files ({len(changes['added'])}):")
            for a in changes["added"]:
                print(f"    + {a['path']}")
        if changes.get("removed"):
            print(f"\n  Removed Files ({len(changes['removed'])}):")
            for r in changes["removed"]:
                print(f"    - {r['path']}")
        if changes.get("permission_changed"):
            print(f"\n  Permission Changes ({len(changes['permission_changed'])}):")
            for p in changes["permission_changed"]:
                print(f"    {p['path']}: {p['old_mode']} → {p['new_mode']}")
    else:
        print("No baseline found. Run 'dargslan-fim baseline' to create one.")

    print()
    if data["issues"]:
        print(f"Issues Found: {data['issues_count']}")
        for issue in data["issues"]:
            print(f"  [{issue['severity'].upper()}] {issue['message']}")
    else:
        print("No integrity issues found.")

    print(f"\nMore Linux tools: https://dargslan.com/cheat-sheets")


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(f"dargslan-file-integrity v{__version__}")
        print(f"File integrity checker with hash-based change detection")
        print(f"\nUsage: dargslan-fim <command> [options]")
        print(f"\nCommands:")
        print(f"  report     Full integrity report with baseline comparison")
        print(f"  baseline   Create a new baseline snapshot")
        print(f"  check      Compare current state with baseline")
        print(f"  scan       Scan and list file hashes")
        print(f"  hash FILE  Calculate SHA-256 hash of a file")
        print(f"  audit      Security audit (issues only)")
        print(f"  json       Full report as JSON")
        print(f"  version    Show version")
        print(f"\nBaseline stored at: {BASELINE_FILE}")
        print(f"\nhttps://dargslan.com — Linux & DevOps Books")
        return

    cmd = args[0]
    if cmd == "version":
        print(f"dargslan-file-integrity v{__version__}")
    elif cmd == "report":
        print_report(generate_report())
    elif cmd == "baseline":
        bl = create_baseline()
        count = len(bl.get("files", {}))
        print(f"Baseline created with {count} files at {BASELINE_FILE}")
    elif cmd == "check":
        result = compare_with_baseline()
        if "error" in result:
            print(result["error"])
            return
        print(f"Baseline: {result['baseline_date']}")
        print(f"Changes: {result['total_changes']}")
        changes = result.get("changes", {})
        for mod in changes.get("modified", []):
            print(f"  [MODIFIED] {mod['path']}")
        for add in changes.get("added", []):
            print(f"  [ADDED] {add['path']}")
        for rem in changes.get("removed", []):
            print(f"  [REMOVED] {rem['path']}")
        for perm in changes.get("permission_changed", []):
            print(f"  [PERMS] {perm['path']}: {perm['old_mode']} → {perm['new_mode']}")
    elif cmd == "scan":
        scanned = scan_paths()
        for f in scanned:
            if "error" in f:
                print(f"  [ERROR] {f['path']}: {f['error']}")
            else:
                h = f.get("hash", "?")[:16]
                print(f"  {h}...  {f['path']}  ({f.get('mode', '?')})")
    elif cmd == "hash":
        if len(args) < 2:
            print("Usage: dargslan-fim hash <filepath>")
            sys.exit(1)
        h = hash_file(args[1])
        if h:
            print(f"{h}  {args[1]}")
        else:
            print(f"Cannot hash: {args[1]}")
    elif cmd == "audit":
        issues = audit()
        if not issues:
            print("No issues found.")
        for i in issues:
            print(f"[{i['severity'].upper()}] {i['message']}")
    elif cmd == "json":
        print(json.dumps(generate_report(), indent=2))
    else:
        print(f"Unknown command: {cmd}. Use --help for usage.")
        sys.exit(1)


if __name__ == "__main__":
    main()
