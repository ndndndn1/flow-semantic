import pytest

from career_semantic.runtime import OPERATIONS, dispatch


@pytest.mark.parametrize("module", sorted(OPERATIONS))
def test_every_module_honors_common_envelope(module):
    result = dispatch({"module": module, "input": {}, "run_id": "test-run"})
    assert result["schema_version"] == "1.0.0"
    assert result["run_id"] == "test-run"
    assert result["module"] == module
    assert isinstance(result["output"], dict)


def test_unknown_module_fails_closed():
    with pytest.raises(ValueError):
        dispatch({"module": "unknown", "input": {}})
