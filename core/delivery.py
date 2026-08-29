from pathlib import Path
import shutil
from datetime import datetime


class ProductDelivery:

    # Only these files are allowed to reach the customer.
    ALLOWED_FILES = {
        "product.pdf",
        "PRODUCT_INFO.txt",
    }

    def __init__(self, delivery_dir="deliveries"):
        self.delivery_dir = Path(delivery_dir)
        self.delivery_dir.mkdir(parents=True, exist_ok=True)

    def deliver(self, product_path, payment):
        if payment.get("status") != "PAYMENT_SUCCESS":
            return {
                "status": "NOT_DELIVERED",
                "reason": "Payment was not confirmed."
            }

        source = Path(product_path)

        if not source.exists():
            return {
                "status": "DELIVERY_FAILED",
                "reason": "Product path does not exist."
            }

        if not source.is_dir():
            return {
                "status": "DELIVERY_FAILED",
                "reason": "Product path must be a directory."
            }

        # Verify that the required customer-facing product exists.
        missing = [
            filename
            for filename in self.ALLOWED_FILES
            if not (source / filename).is_file()
        ]

        if missing:
            return {
                "status": "DELIVERY_FAILED",
                "reason": f"Required product files missing: {', '.join(missing)}"
            }

        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        payment_id = payment.get("payment_id", "unknown")

        # Add payment ID to avoid collisions if two deliveries happen
        # during the same second.
        safe_payment_id = "".join(
            ch for ch in str(payment_id)
            if ch.isalnum() or ch in ("-", "_")
        )

        destination = self.delivery_dir / (
            f"delivery_{timestamp}_{safe_payment_id}"
        )

        destination.mkdir(parents=True, exist_ok=True)

        # Copy ONLY customer-facing files.
        for filename in self.ALLOWED_FILES:
            shutil.copy2(
                source / filename,
                destination / filename
            )

        return {
            "status": "DELIVERED",
            "delivery_path": str(destination),
            "payment_id": payment.get("payment_id"),
            "files": sorted(self.ALLOWED_FILES),
            "real_money": False
        }
