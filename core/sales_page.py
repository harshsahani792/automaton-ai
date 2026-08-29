from pathlib import Path
import re


class SalesPageGenerator:

    def __init__(self, workspace="workspace"):
        self.workspace = Path(workspace)

    def _slugify(self, text):
        text = text.lower()
        text = re.sub(r"[^a-z0-9]+", "-", text)
        return text.strip("-")[:60]

    def generate(self, idea, price=9.99):
        slug = self._slugify(idea)
        product_dir = self.workspace / slug
        product_dir.mkdir(parents=True, exist_ok=True)

        page = product_dir / "sales.html"

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{idea}</title>
</head>
<body>
    <main>
        <h1>{idea}</h1>

        <p>
            A simple digital product designed to solve a specific
            problem quickly and easily.
        </p>

        <h2>What you get</h2>

        <ul>
            <li>Ready-to-use digital product</li>
            <li>Simple and easy to use</li>
            <li>Instant digital delivery</li>
        </ul>

        <h2>Price</h2>
        <p><strong>${price:.2f}</strong></p>

        <button id="buyButton">BUY NOW</button>

        <p id="message"></p>

        <p>
            Digital product. No physical shipping required.
        </p>
    </main>

    <script>
        document.getElementById("buyButton").addEventListener("click", async function () {{
            const button = document.getElementById("buyButton");
            const message = document.getElementById("message");

            button.disabled = true;
            message.textContent = "Creating secure payment link...";

            try {{
                const response = await fetch("http://127.0.0.1:8090/create-payment");
                const result = await response.json();

                if (result.status === "PAYMENT_CREATED" && result.payment_url) {{
                    window.location.href = result.payment_url;
                }} else {{
                    throw new Error(result.reason || result.error || "Payment link creation failed.");
                }}
            }} catch (error) {{
                button.disabled = false;
                message.textContent = "Unable to create payment link: " + error.message;
            }}
        }});
    </script>
</body>
</html>
"""

        page.write_text(html, encoding="utf-8")

        return {
            "status": "CREATED",
            "product": slug,
            "price": price,
            "sales_page": str(page),
            "payment_connected": True,
            "delivery_connected": False
        }
