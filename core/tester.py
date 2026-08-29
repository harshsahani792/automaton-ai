import os


class ProductTester:

    def test(self, build_result):
        if build_result.get("status") != "BUILT":
            return {
                "status": "FAIL",
                "reason": "Product was not built successfully."
            }

        product_path = build_result.get("path")

        if not product_path or not os.path.isdir(product_path):
            return {
                "status": "FAIL",
                "reason": "Product directory does not exist."
            }

        files = build_result.get("files", [])

        missing = []

        for filename in files:
            path = os.path.join(product_path, filename)

            if not os.path.isfile(path):
                missing.append(filename)

        if missing:
            return {
                "status": "FAIL",
                "reason": f"Missing files: {', '.join(missing)}"
            }

        return {
            "status": "PASS",
            "reason": "Prototype files exist and basic structure is valid.",
            "files_checked": files
        }
