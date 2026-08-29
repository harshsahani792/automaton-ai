from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


class PrintablePlanner:

    def __init__(self, output_dir="workspace/create_printable_digital_planners"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def build(self, pages=30):
        output = self.output_dir / "printable_planner.pdf"

        c = canvas.Canvas(str(output), pagesize=A4)
        width, height = A4

        for page in range(1, pages + 1):
            c.setFont("Helvetica-Bold", 22)
            c.drawString(25 * mm, height - 30 * mm, "Daily Productivity Planner")

            c.setFont("Helvetica", 10)
            c.drawString(
                25 * mm,
                height - 40 * mm,
                f"Page {page} / {pages}"
            )

            # Date
            c.setFont("Helvetica-Bold", 12)
            c.drawString(25 * mm, height - 58 * mm, "Date:")

            c.line(
                40 * mm,
                height - 59 * mm,
                90 * mm,
                height - 59 * mm
            )

            # Top priorities
            c.drawString(
                25 * mm,
                height - 78 * mm,
                "TOP 3 PRIORITIES"
            )

            y = height - 90 * mm

            for i in range(1, 4):
                c.rect(25 * mm, y, 6 * mm, 6 * mm)
                c.line(
                    35 * mm,
                    y + 2 * mm,
                    175 * mm,
                    y + 2 * mm
                )
                y -= 13 * mm

            # Tasks
            c.drawString(
                25 * mm,
                y - 5 * mm,
                "TASKS"
            )

            y -= 18 * mm

            for i in range(1, 9):
                c.rect(25 * mm, y, 5 * mm, 5 * mm)
                c.line(
                    34 * mm,
                    y + 1.5 * mm,
                    175 * mm,
                    y + 1.5 * mm
                )
                y -= 11 * mm

            # Notes
            c.drawString(
                25 * mm,
                y - 3 * mm,
                "NOTES"
            )

            y -= 15 * mm

            for i in range(5):
                c.line(
                    25 * mm,
                    y,
                    175 * mm,
                    y
                )
                y -= 9 * mm

            # Footer
            c.setFont("Helvetica", 8)
            c.drawCentredString(
                width / 2,
                12 * mm,
                "Printable Productivity Planner"
            )

            c.showPage()

        c.save()

        return {
            "status": "BUILT",
            "product": "printable_productivity_planner",
            "pages": pages,
            "file": str(output),
            "size_bytes": output.stat().st_size
        }


if __name__ == "__main__":
    result = PrintablePlanner().build(30)

    print("PDF PRODUCT")
    print("================")
    print("Status:", result["status"])
    print("Pages:", result["pages"])
    print("File:", result["file"])
    print("Size:", result["size_bytes"], "bytes")
