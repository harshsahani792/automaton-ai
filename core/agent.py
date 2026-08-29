from datetime import datetime
import json

from core.opportunity import OpportunityEngine
from core.market_research import MarketResearcher
from core.validator import OpportunityValidator
from core.builder import ProductBuilder
from core.tester import ProductTester
from core.improver import ProductImprover
from core.market_tester import MarketTester
from core.sales_page import SalesPageGenerator


class AutomatonAgent:
    def __init__(self, goal, wallet_file="data/wallet.json"):
        self.goal = goal
        self.wallet_file = wallet_file

        self.opportunity_engine = OpportunityEngine()
        self.market_researcher = MarketResearcher()
        self.validator = OpportunityValidator()
        self.builder = ProductBuilder()
        self.tester = ProductTester()
        self.improver = ProductImprover()
        self.market_tester = MarketTester()
        self.sales_page = SalesPageGenerator()

    def read_wallet(self):
        with open(self.wallet_file, "r") as f:
            return json.load(f)

    def think(self):
        wallet = self.read_wallet()
        balance = wallet["balance"]

        if balance <= 0:
            wallet["status"] = "DEAD"

            return {
                "status": "DEAD",
                "decision": "STOP",
                "reason": "No budget remaining."
            }

        # 1. Find opportunity
        opportunity = self.opportunity_engine.find_opportunity()

        # 2. Market research
        research = self.market_researcher.research(
            opportunity["idea"]
        )

        # 3. Validate
        validation = self.validator.validate(
            opportunity,
            balance
        )

        result = {
            "status": "ALIVE",
            "timestamp": datetime.utcnow().isoformat(),
            "goal": self.goal,
            "balance": balance,
            "idea": validation["idea"],
            "market_research": research,
            "score": validation["score"],
            "estimated_cost": opportunity["cost_estimate"],
            "reasons": validation["reasons"]
        }

        # Weak market = don't build
        if research["recommendation"] == "WEAK":
            result["decision"] = "REJECT"
            result["next_step"] = "FIND_NEW_IDEA"
            return result

        # Uncertain market = research more
        if research["recommendation"] == "UNCERTAIN":
            result["decision"] = "RESEARCH_MORE"
            result["next_step"] = "MORE_RESEARCH"
            return result

        # Promising market
        result["decision"] = validation["decision"]

        # 4. Build
        if validation["decision"] == "BUILD":
            build_result = self.builder.build(
                validation["idea"]
            )
            result["build"] = build_result

            # 4B. Generate sales page
            sales_result = self.sales_page.generate(
                validation["idea"],
                price=9.99
            )
            result["sales_page"] = sales_result

            # 5. Test
            test_result = self.tester.test(
                build_result
            )
            result["test"] = test_result

            # 6. Improve
            improvement_result = self.improver.improve(
                build_result,
                test_result
            )
            result["improvement"] = improvement_result

            # 7. Market Test (simulation only)
            if test_result["status"] == "PASS":
                market_test = self.market_tester.test(
                    validation["idea"],
                    research
                )
                result["market_test"] = market_test

                if market_test["decision"] == "TEST_MARKET":
                    result["next_step"] = "READY_FOR_MARKET_TEST"
                elif market_test["decision"] == "MORE_RESEARCH":
                    result["next_step"] = "MORE_RESEARCH"
                else:
                    result["next_step"] = "FIND_NEW_IDEA"
            else:
                result["next_step"] = "FIX_AND_RETEST"

        return result
