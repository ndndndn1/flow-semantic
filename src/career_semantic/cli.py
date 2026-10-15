from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .runtime import OPERATIONS, dispatch


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("module", choices=sorted(OPERATIONS))
    parser.add_argument("--input", type=Path, help="JSON object file, or - for stdin")
    args = parser.parse_args(argv)
    try:
        if args.input == Path("-"):
            payload = json.load(sys.stdin)
        elif args.input:
            payload = json.loads(args.input.read_text())
        else:
            payload = {}
    except json.JSONDecodeError as exc:
        parser.error(f"invalid JSON input: {exc}")
    if not isinstance(payload, dict):
        parser.error("input must be a JSON object")
    print(json.dumps(dispatch({"module": args.module, "input": payload}), indent=2))
    return 0
