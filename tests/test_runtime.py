import hashlib
import json

import pytest

from flow_semantic.catalog import CATALOG, MODULES_BY_ID
from flow_semantic.runtime import OPERATIONS, dispatch


@pytest.mark.parametrize("module", sorted(OPERATIONS))
def test_every_module_honors_common_envelope(module):
    result = dispatch({"module": module, "input": {}, "run_id": "test-run"})
    assert result["schema_version"] == "1.1.0"
    assert result["run_id"] == "test-run"
    assert result["module"] == module
    assert isinstance(result["output"], dict)


def test_unknown_module_fails_closed():
    with pytest.raises(ValueError):
        dispatch({"module": "unknown", "input": {}})


def test_catalog_exactly_describes_every_operation():
    assert CATALOG["schema_version"] == "1.1.0"
    assert CATALOG["package_version"] == "0.2.0"
    assert set(MODULES_BY_ID) == set(OPERATIONS)
    for module_id, module in MODULES_BY_ID.items():
        assert module["module_ref"] == f"flow-semantic/{module_id}@0.2.0"
        assert module["version"] == "0.2.0"
        assert module["input_ports"]["type"] == "object"
        assert module["input_ports"]["additionalProperties"] is True
        assert module["output_ports"]["type"] == "object"
        assert module["output_ports"]["additionalProperties"] is True
        schema_document = {
            "input_ports": module["input_ports"],
            "output_ports": module["output_ports"],
        }
        digest = hashlib.sha256(
            json.dumps(
                schema_document, sort_keys=True, separators=(",", ":")
            ).encode()
        ).hexdigest()
        assert module["schema_hash"] == f"sha256:{digest}"
