from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, unquote
from pathlib import Path
import secrets
import json


HOST = "127.0.0.1"
PORT = 8092

DELIVERY_ROOT = Path("deliveries")
TOKEN_FILE = Path("data/download_tokens.json")


def load_tokens():
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not TOKEN_FILE.exists():
        return {}

    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_tokens(tokens):
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)

    temp_file = TOKEN_FILE.with_suffix(".tmp")

    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(tokens, f, indent=2)

    temp_file.replace(TOKEN_FILE)


def create_download_token(delivery_path):
    tokens = load_tokens()

    token = secrets.token_urlsafe(32)

    tokens[token] = {
        "delivery_path": str(Path(delivery_path).resolve()),
        "file": "product.pdf"
    }

    save_tokens(tokens)

    return token


class DownloadHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/health":
            self.send_json({
                "status": "OK",
                "service": "download_server"
            })
            return

        if parsed.path.startswith("/download/"):
            token = unquote(parsed.path[len("/download/"):])
            self.handle_download(token)
            return

        self.send_response(404)
        self.end_headers()

    def handle_download(self, token):
        tokens = load_tokens()
        record = tokens.get(token)

        if not record:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Invalid download link.")
            return

        delivery_dir = Path(
            record["delivery_path"]
        ).resolve()

        delivery_root = DELIVERY_ROOT.resolve()

        try:
            delivery_dir.relative_to(delivery_root)
        except ValueError:
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b"Forbidden.")
            return

        pdf_path = delivery_dir / "product.pdf"

        if not pdf_path.is_file():
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Product not found.")
            return

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "application/pdf"
        )
        self.send_header(
            "Content-Disposition",
            'attachment; filename="product.pdf"'
        )
        self.send_header(
            "Content-Length",
            str(pdf_path.stat().st_size)
        )
        self.end_headers()

        with open(pdf_path, "rb") as f:
            while True:
                chunk = f.read(64 * 1024)

                if not chunk:
                    break

                self.wfile.write(chunk)

    def send_json(self, data):
        body = json.dumps(data).encode()

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "application/json"
        )
        self.send_header(
            "Content-Length",
            str(len(body))
        )
        self.end_headers()

        self.wfile.write(body)

    def log_message(self, format, *args):
        print(format % args)


if __name__ == "__main__":
    server = HTTPServer(
        (HOST, PORT),
        DownloadHandler
    )

    print("Automaton Download Server")
    print("Listening on port:", PORT)

    server.serve_forever()
