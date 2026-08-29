from datetime import datetime


class MarketResearcher:

    def research(self, idea):
        """
        V1 demo market research.
        Real web/API research will be connected later.
        """

        idea_lower = idea.lower()

        demand_signals = [
            "business",
            "invoice",
            "planner",
            "content",
            "calculator",
            "utility",
            "tool",
            "ai"
        ]

        matching_signals = [
            word for word in demand_signals
            if word in idea_lower
        ]

        if matching_signals:
            demand_score = min(80, 40 + len(matching_signals) * 10)
        else:
            demand_score = 30

        competition_score = 50
        buildability_score = 80

        market_score = round(
            (demand_score + competition_score + buildability_score) / 3
        )

        if market_score >= 70:
            recommendation = "PROMISING"
        elif market_score >= 50:
            recommendation = "UNCERTAIN"
        else:
            recommendation = "WEAK"

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "idea": idea,
            "demand_score": demand_score,
            "competition_score": competition_score,
            "buildability_score": buildability_score,
            "market_score": market_score,
            "recommendation": recommendation,
            "signals": matching_signals,
            "source": "V1_HEURISTIC"
        }
