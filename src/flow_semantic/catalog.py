from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CATALOG_PATH = Path(__file__).with_name("catalog.json")


def load_catalog() -> dict[str, Any]:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


CATALOG = load_catalog()
MODULES_BY_ID = {module["id"]: module for module in CATALOG["modules"]}
