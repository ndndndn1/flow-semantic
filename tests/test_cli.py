import io
import json

import pytest

from career_semantic.cli import main


def assert_result(capsys, expected_output):
    captured = capsys.readouterr()
    assert captured.err == ""
    result = json.loads(captured.out)
    assert set(result) == {"schema_version", "run_id", "module", "output", "lineage"}
    assert result["schema_version"] == "1.0.0"
    assert isinstance(result["run_id"], str)
    assert result["run_id"]
    assert result["module"] == "classify-extract"
    assert result["output"] == expected_output
    assert result["lineage"] == {
        "run_id": result["run_id"],
        "module": "classify-extract",
    }


def test_stdin_input(monkeypatch, capsys):
    monkeypatch.setattr(
        "sys.stdin",
        io.StringIO(json.dumps({"text": "Python", "labels": {"language": ["python"]}})),
    )
    assert main(["classify-extract", "--input", "-"]) == 0
    assert_result(capsys, {"labels": ["language"], "extracted": {}})


@pytest.mark.parametrize(
    ("raw", "message"),
    [
        ("", "invalid JSON input"),
        ("{", "invalid JSON input"),
        ('{} trailing', "invalid JSON input"),
        ("[]", "input must be a JSON object"),
        ("null", "input must be a JSON object"),
        ('"text"', "input must be a JSON object"),
        ("42", "input must be a JSON object"),
        ("true", "input must be a JSON object"),
    ],
)
def test_invalid_stdin_input(monkeypatch, capsys, raw, message):
    monkeypatch.setattr("sys.stdin", io.StringIO(raw))
    with pytest.raises(SystemExit) as exc:
        main(["classify-extract", "--input", "-"])
    assert exc.value.code == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert message in captured.err


def test_file_input(tmp_path, capsys):
    path = tmp_path / "input.json"
    path.write_text(json.dumps({"text": "Python", "spans": {"name": [0, 6]}}))
    assert main(["classify-extract", "--input", str(path)]) == 0
    assert_result(capsys, {"labels": [], "extracted": {"name": "Python"}})


def test_default_input(capsys):
    assert main(["classify-extract"]) == 0
    assert_result(capsys, {"labels": [], "extracted": {}})
