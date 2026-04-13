"""dargslan-cron-parser — Crontab expression parser and scheduler."""

__version__ = "1.0.0"

import re
import json
from datetime import datetime, timedelta
from calendar import monthrange

FIELD_NAMES = ["minute", "hour", "day_of_month", "month", "day_of_week"]
FIELD_RANGES = [(0, 59), (0, 23), (1, 31), (1, 12), (0, 7)]
MONTH_NAMES = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
}
DOW_NAMES = {
    "sun": 0, "mon": 1, "tue": 2, "wed": 3, "thu": 4, "fri": 5, "sat": 6
}
SPECIAL_EXPRESSIONS = {
    "@yearly": "0 0 1 1 *", "@annually": "0 0 1 1 *",
    "@monthly": "0 0 1 * *", "@weekly": "0 0 * * 0",
    "@daily": "0 0 * * *", "@midnight": "0 0 * * *",
    "@hourly": "0 * * * *",
}


def expand_field(field, min_val, max_val):
    if max_val == 7 and field == "7":
        field = "0"
    values = set()
    for part in field.split(","):
        step = 1
        if "/" in part:
            part, step_str = part.split("/", 1)
            step = int(step_str)
        if part == "*":
            values.update(range(min_val, max_val + 1, step))
        elif "-" in part:
            start, end = part.split("-", 1)
            start, end = int(start), int(end)
            values.update(range(start, end + 1, step))
        else:
            part_lower = part.lower()
            if part_lower in MONTH_NAMES:
                values.add(MONTH_NAMES[part_lower])
            elif part_lower in DOW_NAMES:
                values.add(DOW_NAMES[part_lower])
            else:
                values.add(int(part))
    return sorted(v for v in values if min_val <= v <= max_val)


def parse_expression(expr):
    expr = expr.strip()
    if expr.startswith("@"):
        expr = SPECIAL_EXPRESSIONS.get(expr.lower(), expr)
    parts = expr.split()
    if len(parts) != 5:
        return None
    fields = {}
    for i, (part, name) in enumerate(zip(parts, FIELD_NAMES)):
        fields[name] = expand_field(part, FIELD_RANGES[i][0], FIELD_RANGES[i][1])
    return fields


def explain(expr):
    expr_orig = expr.strip()
    if expr_orig.startswith("@"):
        mapped = SPECIAL_EXPRESSIONS.get(expr_orig.lower())
        if mapped:
            labels = {
                "@yearly": "Once a year at midnight on January 1st",
                "@annually": "Once a year at midnight on January 1st",
                "@monthly": "Once a month at midnight on the 1st",
                "@weekly": "Once a week at midnight on Sunday",
                "@daily": "Once a day at midnight",
                "@midnight": "Once a day at midnight",
                "@hourly": "Once an hour at the beginning of the hour",
            }
            return labels.get(expr_orig.lower(), f"Equivalent to: {mapped}")
    fields = parse_expression(expr)
    if not fields:
        return "Invalid cron expression"
    parts = []
    mins = fields["minute"]
    hrs = fields["hour"]
    doms = fields["day_of_month"]
    mons = fields["month"]
    dows = fields["day_of_week"]
    dow_names_rev = {0: "Sunday", 1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday"}
    month_names_rev = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}
    if len(mins) == 1:
        parts.append(f"At minute {mins[0]}")
    elif len(mins) == 60:
        parts.append("Every minute")
    else:
        parts.append(f"At minutes {', '.join(str(m) for m in mins)}")
    if len(hrs) == 1:
        parts.append(f"past hour {hrs[0]}")
    elif len(hrs) < 24:
        parts.append(f"past hours {', '.join(str(h) for h in hrs)}")
    if len(doms) < 31:
        parts.append(f"on day(s) {', '.join(str(d) for d in doms)}")
    if len(mons) < 12:
        parts.append(f"in {', '.join(month_names_rev.get(m, str(m)) for m in mons)}")
    if len(dows) < 7:
        parts.append(f"on {', '.join(dow_names_rev.get(d, str(d)) for d in dows)}")
    return " ".join(parts)


def next_run(expr, after=None, count=5):
    fields = parse_expression(expr)
    if not fields:
        return []
    if after is None:
        after = datetime.now()
    current = after.replace(second=0, microsecond=0) + timedelta(minutes=1)
    results = []
    max_iter = 525600
    for _ in range(max_iter):
        if (current.minute in fields["minute"] and
            current.hour in fields["hour"] and
            current.day in fields["day_of_month"] and
            current.month in fields["month"] and
            (current.weekday() + 1) % 7 in fields["day_of_week"]):
            results.append(current.isoformat())
            if len(results) >= count:
                break
        current += timedelta(minutes=1)
    return results


def validate(expr):
    issues = []
    expr = expr.strip()
    if expr.startswith("@"):
        if expr.lower() not in SPECIAL_EXPRESSIONS:
            issues.append(f"Unknown special expression: {expr}")
        return issues
    parts = expr.split()
    if len(parts) != 5:
        issues.append(f"Expected 5 fields, got {len(parts)}")
        return issues
    for i, (part, name) in enumerate(zip(parts, FIELD_NAMES)):
        try:
            vals = expand_field(part, FIELD_RANGES[i][0], FIELD_RANGES[i][1])
            if not vals:
                issues.append(f"Field '{name}' ({part}) expands to empty set")
        except (ValueError, IndexError):
            issues.append(f"Invalid field '{name}': {part}")
    return issues


def generate_report(expr):
    return {
        "expression": expr,
        "explanation": explain(expr),
        "validation": validate(expr),
        "is_valid": len(validate(expr)) == 0,
        "next_runs": next_run(expr),
        "parsed_fields": parse_expression(expr),
    }
