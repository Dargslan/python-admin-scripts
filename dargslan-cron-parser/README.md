# dargslan-cron-parser

Crontab expression parser — next run calculation, natural language explanation, and schedule validation.

## Installation

```bash
pip install dargslan-cron-parser
```

## Usage

```bash
dargslan-cron explain "*/5 * * * *"    # Natural language
dargslan-cron next "0 2 * * *"         # Next 5 runs
dargslan-cron validate "0 25 * * *"    # Validate
dargslan-cron parse "0 */6 * * 1-5"    # Parse fields
dargslan-cron json "0 0 1 * *"         # JSON output
```

## Features

- Natural language explanation of cron expressions
- Next N run calculations
- Expression validation with error messages
- Support for @yearly, @monthly, @daily, etc.
- Field expansion and range support
- Zero dependencies — pure Python

## Part of dargslan-toolkit

Install all 54 Linux sysadmin tools: `pip install dargslan-toolkit`

## Links

- [Free Linux Cheat Sheets](https://dargslan.com/cheat-sheets)
- [Linux & DevOps Books](https://dargslan.com/books)

## License

MIT
