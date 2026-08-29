import os
import re

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


class ProductBuilder:
    def __init__(self, workspace="workspace"):
        self.workspace = workspace
        os.makedirs(self.workspace, exist_ok=True)

    def _safe_name(self, text):
        name = text.lower()
        name = re.sub(r"[^a-z0-9]+", "-", name)
        return name.strip("-")[:60] or "product"

    def _build_pdf(self, idea, product_dir):
        pdf_path = os.path.join(product_dir, "product.pdf")

        title = idea.strip().rstrip(".")

        sections = [
            "Getting Started",
            "Overview",
            "Step-by-Step Checklist",
            "Worksheet",
            "Planning Notes",
            "Tracking Sheet",
            "Review & Next Actions",
            "Resources",
        ]

        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4

        # Title page
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(
            width / 2,
            height - 60 * mm,
            title
        )

        c.setFont("Helvetica", 12)
        c.drawCentredString(
            width / 2,
            height - 75 * mm,
            "A practical digital guide and worksheet."
        )

        c.setFont("Helvetica", 9)
        c.drawCentredString(
            width / 2,
            30 * mm,
            "Created by Automaton V1"
        )

        c.showPage()

        # Content / worksheet pages
        for index, section in enumerate(sections, start=1):
            c.setFont("Helvetica-Bold", 18)
            c.drawString(
                25 * mm,
                height - 30 * mm,
                section
            )

            c.setFont("Helvetica", 9)
            c.drawString(
                25 * mm,
                height - 40 * mm,
                f"Page {index + 1} / {len(sections) + 1} - {title}"
            )

            c.setFont("Helvetica", 11)
            c.drawString(
                25 * mm,
                height - 55 * mm,
                f"Use this page to work through '{section.lower()}' for:"
            )

            c.setFont("Helvetica-Bold", 11)
            c.drawString(
                25 * mm,
                height - 63 * mm,
                title
            )

            y = height - 78 * mm

            for _ in range(8):
                c.rect(
                    25 * mm,
                    y,
                    5 * mm,
                    5 * mm
                )

                c.line(
                    34 * mm,
                    y + 1.5 * mm,
                    175 * mm,
                    y + 1.5 * mm
                )

                y -= 12 * mm

            c.setFont("Helvetica", 8)
            c.drawCentredString(
                width / 2,
                12 * mm,
                "Digital product. No physical shipping required."
            )

            c.showPage()

        c.save()

        return pdf_path

    def _write_product_info(self, idea, product_dir, pdf_path):
        info_path = os.path.join(product_dir, "PRODUCT_INFO.txt")

        title = idea.strip().rstrip(".")
        size_bytes = os.path.getsize(pdf_path)

        with open(info_path, "w") as f:
            f.write(
                f"{title}\n\n"
                f"Format: PDF\n"
                f"File: product.pdf\n"
                f"Size: {size_bytes} bytes\n\n"
                f"What you get:\n"
                f"- A ready-to-use digital guide and worksheet\n"
                f"- Instant digital delivery\n\n"
                f"Thank you for your purchase.\n"
            )

        return info_path

    def build(self, idea):
        product_name = self._safe_name(idea)

        product_dir = os.path.join(
            self.workspace,
            product_name
        )

        os.makedirs(product_dir, exist_ok=True)

        pdf_path = self._build_pdf(
            idea,
            product_dir
        )

        info_path = self._write_product_info(
            idea,
            product_dir,
            pdf_path
        )

        return {
            "status": "BUILT",
            "product": product_name,
            "path": product_dir,
            "files": [
                os.path.basename(pdf_path),
                os.path.basename(info_path)
            ],
            "slug": product_name,
            "folder": product_dir,
            "file": pdf_path,
            "type": "pdf"
        }
