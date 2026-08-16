import json
import threading
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from flow_semantic.api import Handler, ThreadingHTTPServer
from flow_semantic.catalog import CATALOG


@pytest.fixture
def server_url():
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def read_json(url):
    with urlopen(url, timeout=2) as response:
        return response.status, json.loads(response.read())


def test_list_modules_returns_catalog(server_url):
    status, payload = read_json(f"{server_url}/v1/modules")
    assert status == 200
    assert payload == CATALOG


@pytest.mark.parametrize("module", [item["id"] for item in CATALOG["modules"]])
def test_module_detail_returns_versioned_schema(server_url, module):
    status, payload = read_json(f"{server_url}/v1/modules/{module}")
    assert status == 200
    assert payload["id"] == module
    assert payload["version"] == "0.2.0"
    assert payload["schema_hash"].startswith("sha256:")
    assert "input_ports" in payload
    assert "output_ports" in payload


def test_unknown_module_detail_returns_404(server_url):
    with pytest.raises(HTTPError) as error:
        read_json(f"{server_url}/v1/modules/not-present")
    assert error.value.code == 404


def test_run_endpoint_keeps_the_existing_envelope(server_url):
    module = CATALOG["modules"][0]["id"]
    body = {"module": module, "input": {}, "run_id": "compat-run"}
    request = Request(
        f"{server_url}/v1/run",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=2) as response:
        status = response.status
        payload = json.loads(response.read())
    assert status == 200
    assert payload["run_id"] == "compat-run"
    assert payload["module"] == module
    assert isinstance(payload["output"], dict)
    assert payload["lineage"] == {"run_id": "compat-run", "module": module}
