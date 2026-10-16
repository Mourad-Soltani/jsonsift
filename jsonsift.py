#!/usr/bin/env python3
# JsonSift CLI
# Built by Mourad.Soltani

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Optional

__version__ = "1.0.0"


def load_json(path: str) -> Any:
    """Load JSON from file or stdin."""
    if path == "-":
        return json.load(sys.stdin)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def pretty(data: Any, indent: int = 2) -> str:
    return json.dumps(data, indent=indent, ensure_ascii=False, sort_keys=False)


def extract_path(data: Any, path: str) -> Any:
    """Simple dot/bracket path extractor. Supports a.b[0].c"""
    if not path or path == ".":
        return data
    parts = path.replace("[", ".[").split(".")
    current = data
    for part in parts:
        if not part:
            continue
        if part.startswith("[") and part.endswith("]"):
            idx = int(part[1:-1])
            if not isinstance(current, list) or idx >= len(current):
                raise KeyError(f"Index {idx} out of range")
            current = current[idx]
        else:
            if not isinstance(current, dict) or part not in current:
                raise KeyError(f"Key '{part}' not found")
            current = current[part]
    return current


def diff_json(a: Any, b: Any, path: str = "") -> list[str]:
    """Simple recursive structural diff. Returns list of change descriptions."""
    changes = []
    if type(a) != type(b):
        changes.append(f"{path or '<root>'}: type {type(a).__name__} → {type(b).__name__}")
        return changes
    if isinstance(a, dict):
        all_keys = set(a.keys()) | set(b.keys())
        for k in sorted(all_keys):
            sub = f"{path}.{k}" if path else k
            if k not in a:
                changes.append(f"{sub}: added")
            elif k not in b:
                changes.append(f"{sub}: removed")
            else:
                changes.extend(diff_json(a[k], b[k], sub))
    elif isinstance(a, list):
        if len(a) != len(b):
            changes.append(f"{path or '<root>'}: list length {len(a)} → {len(b)}")
        for i, (x, y) in enumerate(zip(a, b)):
            changes.extend(diff_json(x, y, f"{path}[{i}]" if path else f"[{i}]"))
        if len(a) < len(b):
            for i in range(len(a), len(b)):
                changes.append(f"{path}[{i}]" if path else f"[{i}]: added")
        elif len(b) < len(a):
            for i in range(len(b), len(a)):
                changes.append(f"{path}[{i}]" if path else f"[{i}]: removed")
    else:
        if a != b:
            changes.append(f"{path or '<root>'}: {a!r} → {b!r}")
    return changes


def cmd_pretty(args):
    data = load_json(args.file)
    print(pretty(data, args.indent))


def cmd_validate(args):
    try:
        load_json(args.file)
        print("Valid JSON")
        sys.exit(0)
    except Exception as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_extract(args):
    data = load_json(args.file)
    try:
        result = extract_path(data, args.path)
        print(pretty(result) if not isinstance(result, str) else result)
    except Exception as e:
        print(f"Extract failed: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_diff(args):
    a = load_json(args.left)
    b = load_json(args.right)
    changes = diff_json(a, b)
    if not changes:
        print("No differences")
    else:
        for c in changes:
            print(c)
    sys.exit(0 if not changes else 1)


def cmd_health(args):
    """Health check used by tests."""
    print(json.dumps({"status": "ok", "version": __version__, "author": "Mourad.Soltani"}))
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(
        prog="jsonsift",
        description="JsonSift — pretty-print, validate, extract, and diff JSON. Built by Mourad.Soltani",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_pretty = sub.add_parser("pretty", help="Pretty-print JSON")
    p_pretty.add_argument("file", help="JSON file or - for stdin")
    p_pretty.add_argument("--indent", type=int, default=2)
    p_pretty.set_defaults(func=cmd_pretty)

    p_val = sub.add_parser("validate", help="Validate JSON")
    p_val.add_argument("file", help="JSON file or - for stdin")
    p_val.set_defaults(func=cmd_validate)

    p_ext = sub.add_parser("extract", help="Extract value by path (e.g. user.address[0].city)")
    p_ext.add_argument("file", help="JSON file or - for stdin")
    p_ext.add_argument("path", help="Dot/bracket path")
    p_ext.set_defaults(func=cmd_extract)

    p_diff = sub.add_parser("diff", help="Structural diff of two JSON documents")
    p_diff.add_argument("left", help="Left JSON file")
    p_diff.add_argument("right", help="Right JSON file")
    p_diff.set_defaults(func=cmd_diff)

    p_health = sub.add_parser("health", help="Health check")
    p_health.set_defaults(func=cmd_health)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
