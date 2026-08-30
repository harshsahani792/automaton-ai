from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from datetime import date
import html
import uuid
import os
import json
import hmac
import hashlib


HOST = "0.0.0.0"
PORT = int(__import__("os").environ.get("PORT", "8095"))

OUTPUT_DIR = Path(
    "workspace/ai-invoice-generator-for-small-businesses/generated"
)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


HTML_FORM = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Invoice Generator</title>
<style>
body {
    font-family: Arial, sans-serif;
    max-width: 850px;
    margin: 30px auto;
    padding: 20px;
    background: #f5f5f5;
}
.container {
    background: white;
    padding: 25px;
    border-radius: 12px;
}
h1 { margin-top: 0; }
label {
    display: block;
    margin-top: 12px;
    font-weight: bold;
}
input {
    width: 100%;
    box-sizing: border-box;
    padding: 10px;
    margin-top: 5px;
}
button {
    margin-top: 20px;
    padding: 12px 20px;
    cursor: pointer;
}
.item {
    border: 1px solid #ddd;
    padding: 12px;
    margin-top: 15px;
}
</style>
</head>

<body>
<div class="container">

<h1>AI Invoice Generator</h1>
<p>Create a professional invoice in seconds.</p>

<form method="POST" action="/generate">

<h2>Your Business</h2>

<label>Business Name</label>
<input name="business_name" required>

<label>Business Address</label>
<input name="business_address">

<label>Phone</label>
<input name="business_phone">

<label>Email</label>
<input name="business_email">

<h2>Customer</h2>

<label>Customer Name</label>
<input name="customer_name" required>

<label>Customer Address</label>
<input name="customer_address">

<label>Customer Phone</label>
<input name="customer_phone">

<h2>Invoice</h2>

<label>Invoice Number</label>
<input name="invoice_number" value="INV-0001" required>

<label>Invoice Date</label>
<input name="invoice_date" value="__TODAY__" required>

<div class="item">
<h3>Item 1</h3>

<label>Item Name</label>
<input name="item1_name" required>

<label>Quantity</label>
<input name="item1_qty" type="number" min="1" value="1" required>

<label>Price per Item (Rs. )</label>
<input name="item1_price" type="number" min="0" step="0.01" required>
</div>

<div class="item">
<h3>Item 2 (Optional)</h3>

<label>Item Name</label>
<input name="item2_name">

<label>Quantity</label>
<input name="item2_qty" type="number" min="1" value="1">

<label>Price per Item (Rs. )</label>
<input name="item2_price" type="number" min="0" step="0.01">
</div>

<div class="item">
<h3>Item 3 (Optional)</h3>

<label>Item Name</label>
<input name="item3_name">

<label>Quantity</label>
<input name="item3_qty" type="number" min="1" value="1">

<label>Price per Item (Rs. )</label>
<input name="item3_price" type="number" min="0" step="0.01">
</div>

<h2>Adjustments</h2>

<label>Tax (%)</label>
<input name="tax_rate" type="number" min="0" step="0.01" value="18">

<label>Discount (Rs. )</label>
<input name="discount" type="number" min="0" step="0.01" value="0">

<button type="submit">GENERATE INVOICE PDF</button>

</form>
</div>
</body>
</html>
"""


def safe(value):
    return html.escape(value.strip())


def get_float(data, key, default=0):
    try:
        return float(data.get(key, [default])[0] or default)
    except ValueError:
        return default


def generate_invoice(data):
    invoice_id = uuid.uuid4().hex[:10].upper()
    output = OUTPUT_DIR / f"invoice_{invoice_id}.pdf"

    business_name = safe(data.get("business_name", [""])[0])
    business_address = safe(data.get("business_address", [""])[0])
    business_phone = safe(data.get("business_phone", [""])[0])
    business_email = safe(data.get("business_email", [""])[0])

    customer_name = safe(data.get("customer_name", [""])[0])
    customer_address = safe(data.get("customer_address", [""])[0])
    customer_phone = safe(data.get("customer_phone", [""])[0])

    invoice_number = safe(data.get("invoice_number", ["INV-0001"])[0])
    invoice_date = safe(data.get("invoice_date", [str(date.today())])[0])

    tax_rate = get_float(data, "tax_rate")
    discount = get_float(data, "discount")

    items = []

    for i in range(1, 4):
        name = data.get(f"item{i}_name", [""])[0].strip()

        if not name:
            continue

        qty = get_float(data, f"item{i}_qty", 1)
        price = get_float(data, f"item{i}_price", 0)

        if qty < 0:
            qty = 0

        if price < 0:
            price = 0

        items.append((name, qty, price))

    if not items:
        raise ValueError("At least one item is required.")

    subtotal = sum(qty * price for _, qty, price in items)

    taxable = max(subtotal - discount, 0)
    tax = taxable * tax_rate / 100
    total = taxable + tax

    c = canvas.Canvas(str(output), pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 24)
    c.drawString(25 * mm, height - 30 * mm, "INVOICE")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(25 * mm, height - 48 * mm, business_name)

    c.setFont("Helvetica", 9)

    y = height - 55 * mm

    for text in [business_address, business_phone, business_email]:
        if text:
            c.drawString(25 * mm, y, text)
            y -= 6 * mm

    c.drawRightString(
        width - 25 * mm,
        height - 48 * mm,
        f"Invoice #: {invoice_number}"
    )

    c.drawRightString(
        width - 25 * mm,
        height - 55 * mm,
        f"Date: {invoice_date}"
    )

    c.setFont("Helvetica-Bold", 11)
    c.drawString(25 * mm, height - 88 * mm, "Bill To")

    c.setFont("Helvetica", 9)

    y = height - 96 * mm

    for text in [customer_name, customer_address, customer_phone]:
        if text:
            c.drawString(25 * mm, y, text)
            y -= 6 * mm

    table_top = height - 125 * mm

    c.setFont("Helvetica-Bold", 9)

    c.drawString(25 * mm, table_top, "Item")
    c.drawRightString(120 * mm, table_top, "Qty")
    c.drawRightString(150 * mm, table_top, "Price")
    c.drawRightString(185 * mm, table_top, "Total")

    c.line(
        25 * mm,
        table_top - 3 * mm,
        width - 15 * mm,
        table_top - 3 * mm
    )

    y = table_top - 13 * mm

    c.setFont("Helvetica", 9)

    for name, qty, price in items:
        line_total = qty * price

        c.drawString(25 * mm, y, name[:45])
        c.drawRightString(120 * mm, y, f"{qty:g}")
        c.drawRightString(150 * mm, y, f"Rs. {price:,.2f}")
        c.drawRightString(185 * mm, y, f"Rs. {line_total:,.2f}")

        y -= 10 * mm

    y -= 5 * mm

    c.line(
        120 * mm,
        y,
        width - 15 * mm,
        y
    )

    c.setFont("Helvetica", 9)

    y -= 9 * mm
    c.drawRightString(150 * mm, y, "Subtotal:")
    c.drawRightString(185 * mm, y, f"Rs. {subtotal:,.2f}")

    y -= 8 * mm
    c.drawRightString(150 * mm, y, "Discount:")
    c.drawRightString(185 * mm, y, f"-Rs. {discount:,.2f}")

    y -= 8 * mm
    c.drawRightString(150 * mm, y, f"Tax ({tax_rate:g}%):")
    c.drawRightString(185 * mm, y, f"Rs. {tax:,.2f}")

    y -= 10 * mm

    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(150 * mm, y, "Grand Total:")
    c.drawRightString(185 * mm, y, f"Rs. {total:,.2f}")

    c.setFont("Helvetica", 8)
    c.drawCentredString(
        width / 2,
        20 * mm,
        "Thank you for your business!"
    )

    c.save()

    return output, subtotal, tax, discount, total


class InvoiceHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/" or path == "/invoice":
            page = HTML_FORM.replace(
                "__TODAY__",
                str(date.today())
            ).encode()

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(page)))
            self.end_headers()
            self.wfile.write(page)
            return

        if path.startswith("/download/"):
            filename = path.split("/download/", 1)[1]
            file = OUTPUT_DIR / Path(filename).name

            if not file.is_file():
                self.send_response(404)
                self.end_headers()
                return

            data = file.read_bytes()

            self.send_response(200)
            self.send_header("Content-Type", "application/pdf")
            self.send_header(
                "Content-Disposition",
                f'attachment; filename="{file.name}"'
            )
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        if self.path == "/webhook":
            length = int(self.headers.get("Content-Length", "0"))
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

                print("WEBHOOK RECEIVED:", event)

                if event == "payment_link.paid":
                    print("PAYMENT LINK PAID")

                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"OK")

            except Exception as e:
                print("WEBHOOK ERROR:", e)
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())

            return

        if self.path != "/generate":
            self.send_response(404)
            self.end_headers()
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length)

            data = parse_qs(
                raw.decode("utf-8"),
                keep_blank_values=True
            )

            output, subtotal, tax, discount, total = generate_invoice(data)

            filename = output.name

            page = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Invoice Ready</title>
</head>
<body style="font-family:Arial;max-width:700px;margin:50px auto;padding:20px;">
<h1>Invoice Generated ✅</h1>
<p>Your invoice has been created successfully.</p>

<p>Subtotal: Rs. {subtotal:,.2f}</p>
<p>Discount: Rs. {discount:,.2f}</p>
<p>Tax: Rs. {tax:,.2f}</p>
<h2>Grand Total: Rs. {total:,.2f}</h2>

<a href="/download/{filename}">
<button style="padding:12px 20px;">DOWNLOAD PDF</button>
</a>

<br><br>
<a href="/">Create another invoice</a>
</body>
</html>
""".encode()

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(page)))
            self.end_headers()
            self.wfile.write(page)

        except Exception as e:
            message = html.escape(str(e))

            page = f"""<html>
<body style="font-family:Arial;padding:30px;">
<h1>Invoice Error</h1>
<p>{message}</p>
<a href="/">Go back</a>
</body>
</html>
""".encode()

            self.send_response(400)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(page)))
            self.end_headers()
            self.wfile.write(page)

    def log_message(self, format, *args):
        print(format % args)


if __name__ == "__main__":
    server = HTTPServer((HOST, PORT), InvoiceHandler)

    print("AI Invoice Generator")
    print("=====================")
    print(f"Open: http://{HOST}:{PORT}")

    server.serve_forever()
