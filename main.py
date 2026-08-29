import time

from core.agent import AutomatonAgent
from core.memory import Memory
from core.budget import Budget
from core.heartbeat import Heartbeat


GOAL = "Find and build a small digital product that can eventually generate revenue."

agent = AutomatonAgent(GOAL)
memory = Memory()
budget = Budget()
heartbeat = Heartbeat(interval=60)


def run_cycle():
    wallet = budget.load()

    print("=" * 50)
    print("AUTOMATON V1")
    print("=" * 50)
    print(f"Status : {wallet['status']}")
    print(f"Balance: ${wallet['balance']:.2f}")
    print(f"Goal   : {GOAL}")
    print("-" * 50)

    decision = agent.think()

    print(f"Decision: {decision['decision']}")
    print(f"Idea: {decision.get('idea', 'N/A')}")
    print(f"Score: {decision.get('score', 'N/A')}")
    print(f"Estimated cost: ${decision.get('estimated_cost', 0):.2f}")

    research = decision.get("market_research")

    if research:
        print("Market Research:")
        print(f"  Demand Score      : {research.get('demand_score')}")
        print(f"  Competition Score : {research.get('competition_score')}")
        print(f"  Buildability      : {research.get('buildability_score')}")
        print(f"  Market Score      : {research.get('market_score')}")
        print(f"  Recommendation    : {research.get('recommendation')}")
        print(f"  Source             : {research.get('source')}")

    if decision.get("reasons"):
        print("Reasons:")
        for reason in decision["reasons"]:
            print(f"  - {reason}")

    memory.remember(
        "agent_cycle",
        {
            "decision": decision.get("decision"),
            "idea": decision.get("idea"),
            "score": decision.get("score"),
            "estimated_cost": decision.get("estimated_cost"),
            "balance": decision.get("balance", wallet["balance"]),
            "market_research": decision.get("market_research"),
            "reasons": decision.get("reasons", []),
            "build": decision.get("build"),
            "test": decision.get("test"),
            "next_step": decision.get("next_step"),
            "sales_page": decision.get("sales_page")
        }
    )

    print("Memory : SAVED")
    print("Heartbeat: OK")
    print("=" * 50)


def main():
    print("Starting Automaton V1...")

    while heartbeat.running:
        try:
            wallet = budget.load()

            if wallet["balance"] <= 0:
                print("AUTOMATON DEAD: No budget remaining.")
                break

            run_cycle()
            heartbeat.wait()

        except KeyboardInterrupt:
            print("\nAutomaton stopped by user.")
            heartbeat.stop()

        except Exception as e:
            print(f"ERROR: {e}")
            time.sleep(10)


if __name__ == "__main__":
    main()
