from pathlib import Path
import shutil


class ProductPackager:

    def package(self, product_dir):
        product_dir = Path(product_dir)

        pdf = product_dir / "printable_planner.pdf"

        if not pdf.exists():
            return {
                "status": "FAIL",
                "reason": "Printable PDF not found."
            }

        package_dir = product_dir / "product_package"
        package_dir.mkdir(parents=True, exist_ok=True)

        destination = package_dir / pdf.name
        shutil.copy2(pdf, destination)

        readme = package_dir / "PRODUCT_INFO.txt"

        readme.write_text(
            """PRINTABLE PRODUCT

Product: Daily Productivity Planner
Format: PDF
Pages: 30
Use: Personal productivity and planning

Thank you for your purchase.
""",
            encoding="utf-8"
        )

        return {
            "status": "PACKAGED",
            "package": str(package_dir),
            "files": [f.name for f in package_dir.iterdir()]
        }


if __name__ == "__main__":
    result = ProductPackager().package(
        "workspace/create_printable_digital_planners"
    )

    print("PRODUCT PACKAGE")
    print("================")
    print("Status:", result["status"])
    print("Package:", result.get("package"))
    print("Files:", result.get("files"))
