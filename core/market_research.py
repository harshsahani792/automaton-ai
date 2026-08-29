import requests
from bs4 import BeautifulSoup
from datetime import datetime


class MarketResearcher:

    def __init__(self):
        self.timeout = 15
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Android) AutomatonV1"
        }

    def search_web(self, query, max_results=8):
        url = "https://html.duckduckgo.com/html/"

        try:
            response = requests.get(
                url,
                params={"q": query},
                headers=self.headers,
                timeout=self.timeout
            )

            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            results = []

            for item in soup.select(".result"):
                title_tag = item.select_one(".result__a")
                snippet_tag = item.select_one(".result__snippet")

                if not title_tag:
                    continue

                results.append({
                    "title": title_tag.get_text(" ", strip=True),
                    "url": title_tag.get("href", ""),
                    "snippet": (
                        snippet_tag.get_text(" ", strip=True)
                        if snippet_tag else ""
                    )
                })

                if len(results) >= max_results:
                    break

            return results

        except Exception as e:
            return {"error": str(e)}

    def research(self, idea):

        query = f"{idea} alternatives pricing competitors"
        results = self.search_web(query)

        if isinstance(results, dict):
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "idea": idea,
                "market_score": 0,
                "recommendation": "RESEARCH_FAILED",
                "source": "DUCKDUCKGO",
                "results": [],
                "error": results.get("error")
            }

        if not results:
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "idea": idea,
                "market_score": 0,
                "recommendation": "RESEARCH_FAILED",
                "source": "DUCKDUCKGO",
                "results": []
            }

        combined = " ".join(
            item["title"] + " " + item["snippet"]
            for item in results
        ).lower()

        demand_words = [
            "buy", "price", "pricing", "tool",
            "software", "template", "solution", "business"
        ]

        competition_words = [
            "alternative", "competitor",
            "similar", "free", "pricing", "software"
        ]

        demand_hits = sum(
            word in combined for word in demand_words
        )

        competition_hits = sum(
            word in combined for word in competition_words
        )

        demand_score = min(100, 35 + demand_hits * 8)
        competition_score = min(100, 30 + competition_hits * 10)
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
            "demand_hits": demand_hits,
            "competition_hits": competition_hits,
            "source": "DUCKDUCKGO",
            "results": results
        }
