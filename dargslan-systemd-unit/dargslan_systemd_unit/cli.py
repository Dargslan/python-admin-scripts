"""CLI for dargslan-systemd-unit."""

import sys
import json
from . import generate_report, parse_unit_file, analyze_security, lint_unit, find_unit_files, audit, __version__


def print_report(data):
    print(f"Systemd Unit File Analysis")
    print(f"{'=' * 60}")
    if "file" in data:
        print(f"File: {data['file']}")
        print(f"Name: {data['name']}")
        st = data.get("status", {})
        print(f"Active: {st.get('active', '?')}  Enabled: {st.get('enabled', '?')}")
        print()
        for section, directives in data.get("sections", {}).items():
            print(f"  [{section}]")
            for k, v in directives.items():
                print(f"    {k} = {v}")
            print()
        sec = data.get("security", {})
        print(f"Security Score: {sec.get('score', 0)}%")
        if sec.get("missing"):
            print(f"Missing hardening: {', '.join(sec['missing'][:5])}...")
    else:
        print(f"Units Scanned: {data.get('units_scanned', 0)}")
        print(f"Total Issues: {data.get('total_issues', 0)}")
        for s in data.get("summaries", [])[:15]:
            print(f"  {s['file']:<40} security={s['security_score']}%  issues={s['issues']}")
    print()
    issues = data.get("issues", [])
    if issues:
        print(f"Issues ({data.get('issues_count', len(issues))}):")
        for i in issues:
            print(f"  [{i['severity'].upper()}] {i['message']}")
    else:
        print("No issues found.")
    print(f"\nMore Linux tools: https://dargslan.com/cheat-sheets")


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(f"dargslan-systemd-unit v{__version__}")
        print(f"Systemd unit file analyzer")
        print(f"\nUsage: dargslan-unit <command> [file]")
        print(f"\nCommands:")
        print(f"  report [file]   Full analysis (single file or all)")
        print(f"  lint <file>     Lint a unit file for issues")
        print(f"  security <file> Security hardening analysis")
        print(f"  parse <file>    Parse unit file structure")
        print(f"  list            List found unit files")
        print(f"  audit [file]    Issues only")
        print(f"  json [file]     Full report as JSON")
        print(f"  version         Show version")
        print(f"\nhttps://dargslan.com — Linux & DevOps Books")
        return

    cmd = args[0]
    filepath = args[1] if len(args) > 1 else None

    if cmd == "version":
        print(f"dargslan-systemd-unit v{__version__}")
    elif cmd == "report":
        print_report(generate_report(filepath))
    elif cmd == "lint":
        if not filepath:
            print("Usage: dargslan-unit lint <file>"); sys.exit(1)
        issues = lint_unit(filepath)
        if not issues:
            print(f"No issues in {filepath}")
        for i in issues:
            print(f"[{i['severity'].upper()}] {i['message']}")
    elif cmd == "security":
        if not filepath:
            print("Usage: dargslan-unit security <file>"); sys.exit(1)
        parsed = parse_unit_file(filepath)
        sec = analyze_security(parsed)
        print(f"Security Score: {sec['score']}%")
        print(f"Found: {', '.join(sec['found']) or 'none'}")
        print(f"Missing: {', '.join(sec['missing']) or 'none'}")
    elif cmd == "parse":
        if not filepath:
            print("Usage: dargslan-unit parse <file>"); sys.exit(1)
        parsed = parse_unit_file(filepath)
        for section, directives in parsed.items():
            print(f"[{section}]")
            for k, v in directives.items():
                print(f"  {k} = {v}")
    elif cmd == "list":
        for f in find_unit_files():
            print(f)
    elif cmd == "audit":
        issues = audit(filepath)
        if not issues:
            print("No issues found.")
        for i in issues:
            print(f"[{i['severity'].upper()}] {i['message']}")
    elif cmd == "json":
        print(json.dumps(generate_report(filepath), indent=2))
    else:
        print(f"Unknown command: {cmd}. Use --help for usage.")
        sys.exit(1)


if __name__ == "__main__":
    main()
