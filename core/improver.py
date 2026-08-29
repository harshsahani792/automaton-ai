import os
from datetime import datetime


class ProductImprover:

    def improve(self, build_result, test_result):
        if test_result.get("status") == "FAIL":
            action = "FIX"
            reason = test_result.get("reason", "Unknown test failure.")
        else:
            action = "IMPROVE"
            reason = "Prototype passed basic tests and can be improved."

        product_path = build_result.get("path")

        if not product_path or not os.path.isdir(product_path):
            return {
                "status": "FAIL",
                "action": "STOP",
                "reason": "Product directory does not exist."
            }

        improvement_file = os.path.join(
            product_path,
            "IMPROVEMENT_PLAN.md"
        )

        with open(improvement_file, "w") as f:
            f.write(
                "# Improvement Plan\n\n"
                f"Created by: Automaton V1\n\n"
                f"Created at: {datetime.utcnow().isoformat()}\n\n"
                f"## Current test\n"
                f"{test_result.get('status')}\n\n"
                f"## Action\n"
                f"{action}\n\n"
                f"## Reason\n"
                f"{reason}\n\n"
                f"## Next goals\n"
                f"- Improve usability\n"
                f"- Add a useful feature\n"
                f"- Make the prototype easier to test\n"
                f"- Run another test after changes\n"
            )

        return {
            "status": "IMPROVED",
            "action": action,
            "file": improvement_file,
            "reason": reason
        }
