#!/usr/bin/env python3
"""Serve ./dist on a local port, with the branded 404 page for missing paths."""
import http.server
import sys
from functools import partial
from pathlib import Path

DIST = Path(__file__).parent / "dist"
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 4175


class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, must-revalidate")
        super().end_headers()

    def send_error(self, code, message=None, explain=None):
        if code == 404:
            body = (DIST / ("en/404.html" if self.path.startswith("/en/") else "404.html")).read_bytes()
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().send_error(code, message, explain)


if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), partial(Handler, directory=str(DIST)))
    print(f"Serving {DIST} at http://localhost:{PORT}")
    server.serve_forever()
