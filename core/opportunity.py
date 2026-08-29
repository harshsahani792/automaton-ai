import random


class OpportunityEngine:
    def __init__(self):
        self.opportunities = [
            "Create a simple invoice generator for small businesses.",
            "Create printable digital planners.",
            "Create a small AI-powered text utility.",
            "Create a simple social-media content tool.",
            "Create a niche calculator or business utility."
        ]

    def find_opportunity(self):
        idea = random.choice(self.opportunities)

        return {
            "idea": idea,
            "cost_estimate": 5.00,
            "potential": "UNKNOWN",
            "next_action": "VALIDATE"
        }
