from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from .fund_flow import get_sector_fund_flows


HOST = "127.0.0.1"
PORT = 8000


def greet(name: str = "World") -> str:
    return f"Hello, {name}!"


class ApiHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        path = urlparse(self.path).path

        if path == "/api/health":
            self.send_json({"status": "ok"})
            return

        if path == "/api/sectors/fund-flows":
            self.send_json(get_sector_fund_flows())
            return

        self.send_json({"message": "Not found"}, status=404)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_cors_headers()
        self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        return

    def send_json(self, data: object, status: int = 200) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")


def run_server(host: str = HOST, port: int = PORT) -> None:
    server = ThreadingHTTPServer((host, port), ApiHandler)
    print(f"Python API running at http://{host}:{port}")
    print("Fund flow API: /api/sectors/fund-flows")
    server.serve_forever()


def main() -> None:
    run_server()


if __name__ == "__main__":
    main()
