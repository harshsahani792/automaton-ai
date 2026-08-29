from pathlib import Path
import re


class ProductFactory:

    def __init__(self, workspace="workspace"):
        self.workspace = Path(workspace)

    def _slugify(self, text):
        text = text.lower()
        text = re.sub(r"[^a-z0-9]+", "_", text)
        return text.strip("_")[:60]

    def build(self, idea):
        slug = self._slugify(idea)

        product_dir = self.workspace / slug
        product_dir.mkdir(parents=True, exist_ok=True)

        readme = product_dir / "README.md"

        readme.write_text(
            f"""# {idea}

## Product

This is an Automaton V1 prototype.

## Idea

{idea}

## Goal

Create a small digital product that solves a specific problem
for a specific user group.

## Status

PROTOTYPE

## Next Steps

1. Validate the target customer.
2. Improve the product.
3. Test demand.
4. Prepare a simple sales page.
5. Measure real interest.

## Safety

This prototype does not spend real money or place real orders.
""",
            encoding="utf-8"
        )

        return {
            "status": "BUILT",
            "product": slug,
            "path": str(product_dir),
            "files": [readme.name]
        }

    def test(self, build_result):
        path = Path(build_result["path"])

        if not path.exists():
            return {
                "status": "FAIL",
                "reason": "Product directory does not exist."
            }

        files = list(path.iterdir())

        if not files:
            return {
                "status": "FAIL",
                "reason": "Product directory is empty."
            }

        return {
            "status": "PASS",
            "reason": "Prototype exists and contains files.",
            "files_checked": [f.name for f in files]
        }
