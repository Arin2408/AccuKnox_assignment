"""Small local REST API serving SYNTHETIC scores at http://127.0.0.1:8000/scores"""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

SCORES = [
    {"name": "Student A", "score": 78},
    {"name": "Student B", "score": 92},
    {"name": "Student C", "score": 64},
    {"name": "Student D", "score": 85},
    {"name": "Student E", "score": 71},
    {"name": "Student F", "score": 55},
    {"name": "Student G", "score": None},  # deliberately bad: missing
    {"name": "Student H", "score": 140},   # deliberately bad: out of range
]


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/scores":
            self.send_error(404)
            return
        body = json.dumps(SCORES).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    print("Serving http://127.0.0.1:8000/scores (Ctrl+C to stop)")
    HTTPServer(("127.0.0.1", 8000), Handler).serve_forever()
