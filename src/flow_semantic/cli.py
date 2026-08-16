from __future__ import annotations

import argparse
import json
from pathlib import Path

from .runtime import OPERATIONS, dispatch


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("module", choices=sorted(OPERATIONS))
    parser.add_argument("--input", type=Path)
    args = parser.parse_args(argv)
    payload = json.loads(args.input.read_text()) if args.input else {}
    print(json.dumps(dispatch({"module": args.module, "input": payload}), indent=2))
    return 0
