"""Run a localhost-only R43 rehearsal with SQLite-backed group sessions."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from r43_store import Conflict, Ledger


def server(ledger, port=8765):
    html = Path(__file__).with_name("r43_pilot.html").read_bytes()

    class Handler(BaseHTTPRequestHandler):
        def send(self, status, body, kind="application/json"):
            self.send_response(status)
            self.send_header("Content-Type", kind)
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def handle_api(self, data=None):
            if self.path == "/" and data is None:
                self.send(200, html, "text/html; charset=utf-8")
                return
            try:
                parts = self.path.strip("/").split("/")
                if parts == ["group"] and data is not None:
                    result = {"id": ledger.allocate(data.get("blocks"), data.get("request_id"))}
                elif len(parts) in (2, 3) and parts[0] == "group":
                    group_id = parts[1]
                    suffix = parts[2] if len(parts) == 3 else None
                    if data is None and suffix == "export":
                        result = ledger.export(group_id)
                    elif data is None and suffix is None:
                        result = ledger.view(group_id)
                    elif data is not None and suffix == "choice":
                        ledger.choose(group_id, data.get("step"), data.get("route"), data.get("response_ms"))
                        result = ledger.view(group_id)
                    else:
                        raise KeyError("unknown route")
                else:
                    raise KeyError("unknown route")
                self.send(200, json.dumps(result).encode())
            except KeyError:
                self.send(404, b'{"error":"unknown group or route"}')
            except Conflict as error:
                self.send(409, json.dumps({"error": str(error)}).encode())
            except ValueError as error:
                self.send(400, json.dumps({"error": str(error)}).encode())

        def do_GET(self):
            self.handle_api()

        def do_POST(self):
            try:
                length = int(self.headers.get("Content-Length", 0))
                if not 0 < length <= 4096 or self.headers.get_content_type() != "application/json":
                    raise ValueError("expected JSON request")
                data = json.loads(self.rfile.read(length))
                if not isinstance(data, dict):
                    raise ValueError("expected JSON object")
            except (UnicodeError, ValueError):
                self.send(400, b'{"error":"invalid request"}')
                return
            self.handle_api(data)

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--db", default="r43_rehearsal.sqlite3")
    args = parser.parse_args()
    with server(Ledger(args.db), args.port) as app:
        print(f"R43 rehearsal: http://127.0.0.1:{app.server_port}", flush=True)
        app.serve_forever()
