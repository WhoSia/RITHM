"""Start the R49 operator-only rehearsal on localhost."""

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from r49_store import Conflict, Ledger


def server(ledger, port=0):
    html = Path(__file__).with_name("r49_pilot.html").read_bytes()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            return

        def send(self, status, body, mime="application/json"):
            self.send_response(status)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def reply(self, status, value):
            self.send(status, json.dumps(value).encode())

        def api(self, data=None):
            parts = self.path.strip("/").split("/")
            try:
                if data is not None and parts == ["allocate"]:
                    ledger.allocate(data.get("id"), data.get("start"), data.get("rounds"))
                    response = ledger.view(data["id"])
                elif parts[0] == "study" and len(parts) in (2, 3):
                    study = parts[1]
                    if len(parts) == 2 and data is None:
                        response = ledger.view(study)
                    elif parts[2:] == ["export"] and data is None:
                        response = ledger.export(study)
                    elif len(parts) == 3 and data is not None:
                        response = ledger.action(study, parts[2], data.get("round"),
                                                 seat=data.get("seat"), route=data.get("route"),
                                                 receipt=data.get("receipt"))
                    else:
                        raise KeyError("unknown route")
                else:
                    raise KeyError("unknown route")
            except KeyError:
                self.reply(404, {"error": "리허설을 찾을 수 없습니다."})
            except Conflict as error:
                self.reply(409, {"error": str(error)})
            except ValueError as error:
                self.reply(400, {"error": str(error)})
            else:
                self.reply(200, response)

        def do_GET(self):
            if self.path == "/":
                self.send(200, html, "text/html; charset=utf-8")
            else:
                self.api()

        def do_POST(self):
            try:
                size = int(self.headers.get("Content-Length", 0))
                if not 0 < size <= 4096 or self.headers.get_content_type() != "application/json":
                    raise ValueError("invalid JSON")
                data = json.loads(self.rfile.read(size))
                if not isinstance(data, dict):
                    raise ValueError("expected JSON object")
            except (UnicodeError, ValueError):
                self.reply(400, {"error": "잘못된 요청입니다."})
            else:
                self.api(data)

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


if __name__ == "__main__":
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument("--port", type=int, default=8765)
    args.add_argument("--db", default="r49_rehearsal.sqlite3")
    options = args.parse_args()
    with server(Ledger(options.db), options.port) as app:
        print(f"R49 rehearsal: http://127.0.0.1:{app.server_port}", flush=True)
        app.serve_forever()
