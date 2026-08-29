from datetime import datetime


class MarketTester:

    def test(self, idea, research):

        market_score = research.get("market_score", 0)
        recommendation = research.get("recommendation", "UNKNOWN")

        if recommendation == "PROMISING" and market_score >= 70:
            decision = "TEST_MARKET"

        elif recommendation == "UNCERTAIN" and market_score >= 60:
            decision = "MORE_RESEARCH"

        else:
            decision = "REJECT"

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "idea": idea,
            "market_score": market_score,
            "research_recommendation": recommendation,
            "decision": decision,
            "real_money_spent": 0.00,
            "status": "SIMULATION"
        }
