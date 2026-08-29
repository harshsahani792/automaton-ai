from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import urlopen
from pathlib import Path
import json

ROOT = Path("workspace/ai-invoice-generator-for-small-businesses")

class SalesHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/create-payment":
            try:
                with urlopen(
                    "http://127.0.0.1:8090/create-payment",
                    timeout=15
                ) as response:
                    body = response.read()

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            except Exception as e:
                body = json.dumps({
                    "status": "ERROR",
                    "error": str(e)
                }).encode()

                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            return

        if self.path.split("?")[0] == "/" or self.path.split("?")[0] == "/sales.html":
            file = ROOT / "sales.html"

            if file.exists():
                body = file.read_bytes()

                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return

        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        print(format % args)

server = HTTPServer(("127.0.0.1", 3000), SalesHandler)

print("Automaton Sales Server")
print("Listening on port: 3000")

server.serve_forever()
