class OpportunityValidator:

    def validate(self, opportunity, balance):
        idea = opportunity["idea"]
        cost = opportunity["cost_estimate"]

        score = 0
        reasons = []

        # Budget check
        if cost <= balance * 0.10:
            score += 25
            reasons.append("Low cost compared with available budget.")
        elif cost <= balance * 0.25:
            score += 15
            reasons.append("Affordable but uses more budget.")
        else:
            score += 5
            reasons.append("High cost for current budget.")

        # Simple demand heuristic
        demand_keywords = [
            "business",
            "invoice",
            "planner",
            "content",
            "calculator",
            "utility",
            "tool"
        ]

        if any(word in idea.lower() for word in demand_keywords):
            score += 30
            reasons.append("Potentially useful to a specific user group.")
        else:
            score += 10

        # Simplicity
        if any(word in idea.lower() for word in ["simple", "small", "printable"]):
            score += 25
            reasons.append("Relatively simple to prototype.")

        # Remaining score
        score += 20

        if score >= 70:
            decision = "BUILD"
        elif score >= 50:
            decision = "RESEARCH_MORE"
        else:
            decision = "REJECT"

        return {
            "idea": idea,
            "score": min(score, 100),
            "decision": decision,
            "reasons": reasons
        }
