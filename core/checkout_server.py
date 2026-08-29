from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import json

from core.payment import PaymentGateway


class CheckoutHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if urlparse(self.path).path != "/create-payment":
            self.send_response(404)
            self.end_headers()
            return

        gateway = PaymentGateway()

        result = gateway.create_payment(
            product="AI Invoice Generator",
            price=9.99,
            customer_name="Customer",
            customer_email="test@example.com"
        )

        body = json.dumps(result).encode()

        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        print(format % args)


server = HTTPServer(("127.0.0.1", 8090), CheckoutHandler)

print("Automaton Checkout Server")
print("Listening on port: 8090")

server.serve_forever()
