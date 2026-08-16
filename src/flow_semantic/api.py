from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse

from .catalog import CATALOG, MODULES_BY_ID
from .runtime import dispatch


class Handler(BaseHTTPRequestHandler):
    def _send(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/healthz":
            self._send(200, {"status": "ok", "modules": sorted(MODULES_BY_ID)})
        elif path == "/v1/modules":
            self._send(200, CATALOG)
        elif path.startswith("/v1/modules/"):
            module_id = unquote(path.removeprefix("/v1/modules/"))
            module = MODULES_BY_ID.get(module_id)
            if module is None:
                self._send(404, {"error": f"unknown module: {module_id}"})
            else:
                self._send(200, module)
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/v1/run":
            self._send(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            self._send(200, dispatch(json.loads(self.rfile.read(length))))
        except (ValueError, json.JSONDecodeError) as exc:
            self._send(400, {"error": str(exc)})

    def log_message(self, format, *args):
        return


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args(argv)
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
