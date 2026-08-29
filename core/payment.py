import os
import json
import base64
import urllib.request
from datetime import datetime


class PaymentGateway:

    def __init__(self):
        self.provider = "RAZORPAY"
        self.key_id = os.getenv("RAZORPAY_KEY_ID", "")
        self.key_secret = os.getenv("RAZORPAY_KEY_SECRET", "")
        self.mapping_file = "data/payment_links.json"

        os.makedirs("data", exist_ok=True)

    def _save_mapping(self, reference_id, product, price):
        mappings = {}

        if os.path.exists(self.mapping_file):
            try:
                with open(self.mapping_file, "r") as f:
                    mappings = json.load(f)
            except Exception:
                mappings = {}

        mappings[reference_id] = {
            "product": product,
            "price": float(price),
            "created_at": datetime.utcnow().isoformat()
        }

        with open(self.mapping_file, "w") as f:
            json.dump(mappings, f, indent=2)

    def create_payment(
        self,
        product,
        price,
        customer_name="Customer",
        customer_email=""
    ):
        if not self.key_id or not self.key_secret:
            return {
                "status": "PAYMENT_FAILED",
                "reason": "Razorpay credentials are missing."
            }

        amount_paise = int(round(float(price) * 100))

        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        reference_id = "AUTO-" + timestamp

        payload = {
            "amount": amount_paise,
            "currency": "INR",
            "description": product,
            "reference_id": reference_id,
            "customer": {
                "name": customer_name,
                "email": customer_email
            },
            "notify": {
                "email": True,
                "sms": False
            },
            "reminder_enable": True
        }

        auth = base64.b64encode(
            f"{self.key_id}:{self.key_secret}".encode()
        ).decode()

        data = json.dumps(payload).encode()

        request = urllib.request.Request(
            "https://api.razorpay.com/v1/payment_links",
            data=data,
            headers={
                "Authorization": "Basic " + auth,
                "Content-Type": "application/json"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                result = json.loads(response.read().decode())

            # Save the product mapping locally.
            self._save_mapping(
                reference_id,
                product,
                price
            )

            return {
                "status": "PAYMENT_CREATED",
                "provider": "RAZORPAY",
                "product": product,
                "amount": float(price),
                "currency": "INR",
                "payment_id": result.get("id"),
                "payment_url": result.get("short_url"),
                "reference_id": reference_id,
                "real_money": False,
                "razorpay_status": result.get("status")
            }

        except Exception as e:
            return {
                "status": "PAYMENT_FAILED",
                "provider": "RAZORPAY",
                "error": str(e),
                "real_money": False
            }

    def confirm_payment(self, payment):
        return {
            **payment,
            "status": "PAYMENT_SUCCESS",
            "confirmed_at": datetime.utcnow().isoformat(),
            "real_money": False
        }


if __name__ == "__main__":
    gateway = PaymentGateway()

    result = gateway.create_payment(
        product="AI Invoice Generator",
        price=9.99,
        customer_name="Test Customer",
        customer_email="test@example.com"
    )

    print(json.dumps(result, indent=2))

