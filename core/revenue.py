from pathlib import Path
import json
from datetime import datetime


class RevenueTracker:

    def __init__(self, file="data/revenue.json"):
        self.file = Path(file)
        self.file.parent.mkdir(parents=True, exist_ok=True)

        if not self.file.exists():
            self.file.write_text("[]", encoding="utf-8")

    def _read(self):
        try:
            return json.loads(
                self.file.read_text(encoding="utf-8")
            )
        except Exception:
            return []

    def record_sale(self, product, amount, payment_id):
        records = self._read()

        sale = {
            "timestamp": datetime.utcnow().isoformat(),
            "product": product,
            "amount": float(amount),
            "payment_id": payment_id,
            "real_money": False
        }

        records.append(sale)

        self.file.write_text(
            json.dumps(records, indent=2),
            encoding="utf-8"
        )

        return sale

    def summary(self):
        records = self._read()

        revenue = sum(
            item.get("amount", 0)
            for item in records
        )

        return {
            "sales": len(records),
            "revenue": round(revenue, 2),
            "real_money": False
        }
