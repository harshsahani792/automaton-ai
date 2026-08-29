from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
import hmac
import hashlib

from core.delivery import ProductDelivery
from core.revenue import RevenueTracker
from core.download_server import create_download_token


HOST = "0.0.0.0"
PORT = 8080


class WebhookHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        secret = os.getenv("PAYMENT_WEBHOOK_SECRET", "")
        signature = self.headers.get("X-Razorpay-Signature", "")

        if secret:
            expected = hmac.new(
                secret.encode(),
                body,
                hashlib.sha256
            ).hexdigest()

            if not hmac.compare_digest(signature, expected):
                self.send_response(401)
                self.end_headers()
                self.wfile.write(b"Invalid signature")
                return

        try:
            payload = json.loads(body.decode("utf-8"))
            event = payload.get("event", "unknown")

            print()
            print("WEBHOOK RECEIVED")
            print("================")
            print("Event:", event)

            if event != "payment_link.paid":
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"IGNORED")
                return

            entity = (
                payload
                .get("payload", {})
                .get("payment_link", {})
                .get("entity", {})
            )

            product = entity.get(
                "product",
                "AI invoice generator"
            )

            amount = float(
                entity.get("amount", 0)
            ) / 100

            payment_id = entity.get(
                "id",
                "UNKNOWN"
            )

            # Product folders
            product_paths = {
                "AI invoice generator":
                    "workspace/create-a-simple-invoice-generator-for-small-businesses",

                "Printable digital planners":
                    "workspace/create-printable-digital-planners",

                "Niche calculator":
                    "workspace/create-a-niche-calculator-or-business-utility",

                "Small AI text utility":
                    "workspace/create-a-small-ai-powered-text-utility"
            }

            product_path = product_paths.get(product)

            if not product_path:
                print("Unknown product:", product)

                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"UNKNOWN_PRODUCT")
                return

            payment = {
                "status": "PAYMENT_SUCCESS",
                "payment_id": payment_id
            }

            delivery = ProductDelivery()

            delivery_result = delivery.deliver(
                product_path,
                payment
            )

            print("Payment:", payment["status"])
            print("Product:", product)
            print("Amount:", amount)
            print("Delivery:", delivery_result["status"])

            if delivery_result["status"] == "DELIVERED":

                print(
                    "Delivery path:",
                    delivery_result["delivery_path"]
                )

                download_token = create_download_token(
                    delivery_result["delivery_path"]
                )

                download_url = (
                    "http://127.0.0.1:8092/download/"
                    + download_token
                )

                print("Download URL:", download_url)

                tracker = RevenueTracker()

                sale = tracker.record_sale(
                    product,
                    amount,
                    payment_id
                )

                print("Revenue recorded:", sale["amount"])

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")

        except Exception as e:
            print("ERROR:", e)

            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())


if __name__ == "__main__":
    print("Automaton Webhook Server")
    print("Listening on port:", PORT)

    server = HTTPServer(
        (HOST, PORT),
        WebhookHandler
    )

    server.serve_forever()
