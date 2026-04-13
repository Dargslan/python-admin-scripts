"""CLI for dargslan-cron-parser."""

import sys
import json
from . import explain, next_run, validate, parse_expression, generate_report, __version__


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(f"dargslan-cron-parser v{__version__}")
        print(f"Crontab expression parser and scheduler")
        print(f"\nUsage: dargslan-cron <command> <expression>")
        print(f"\nCommands:")
        print(f"  explain \"*/5 * * * *\"    Natural language explanation")
        print(f"  next \"0 2 * * *\"         Next 5 scheduled runs")
        print(f"  validate \"0 25 * * *\"    Validate expression")
        print(f"  parse \"0 */6 * * 1-5\"    Parse into field values")
        print(f"  report \"0 0 1 * *\"       Full analysis report")
        print(f"  json \"* * * * *\"         Full report as JSON")
        print(f"  version                   Show version")
        print(f"\nhttps://dargslan.com — Linux & DevOps Books")
        return

    cmd = args[0]
    if cmd == "version":
        print(f"dargslan-cron-parser v{__version__}")
        return

    if len(args) < 2:
        print("Error: Please provide a cron expression.")
        print("Example: dargslan-cron explain \"*/5 * * * *\"")
        sys.exit(1)

    expr = args[1]
    if cmd == "explain":
        print(explain(expr))
    elif cmd == "next":
        count = 5
        if "-n" in args:
            idx = args.index("-n")
            if idx + 1 < len(args):
                count = int(args[idx + 1])
        runs = next_run(expr, count=count)
        print(f"Next {len(runs)} runs for: {expr}")
        print(f"  {explain(expr)}")
        for r in runs:
            print(f"  {r}")
    elif cmd == "validate":
        issues = validate(expr)
        if not issues:
            print(f"Valid: {expr}")
            print(f"  {explain(expr)}")
        else:
            print(f"Invalid: {expr}")
            for i in issues:
                print(f"  [ERROR] {i}")
    elif cmd == "parse":
        fields = parse_expression(expr)
        if fields:
            for name, vals in fields.items():
                print(f"  {name}: {vals}")
        else:
            print("Invalid expression")
    elif cmd == "report":
        r = generate_report(expr)
        print(f"Cron Expression: {r['expression']}")
        print(f"Explanation: {r['explanation']}")
        print(f"Valid: {r['is_valid']}")
        if r['validation']:
            print(f"Issues:")
            for i in r['validation']:
                print(f"  {i}")
        print(f"\nNext runs:")
        for run in r['next_runs']:
            print(f"  {run}")
        print(f"\nMore Linux tools: https://dargslan.com/cheat-sheets")
    elif cmd == "json":
        print(json.dumps(generate_report(expr), indent=2))
    else:
        print(f"Unknown command: {cmd}. Use --help for usage.")
        sys.exit(1)


if __name__ == "__main__":
    main()
