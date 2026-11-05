from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
import re
from typing import Callable, Iterable
from urllib import parse, request


@dataclass
class Source:
    query: str
    url: str
    snippet: str


class MarketResearchAgent:
    """Goal-based market research agent with tool-using and context memory behavior."""

    def __init__(
        self,
        jina_api_key: str | None = None,
        gemini_api_key: str | None = None,
        fetcher: Callable[[str, dict[str, str] | None], str] | None = None,
    ) -> None:
        self.jina_api_key = jina_api_key or os.getenv("JINA_API_KEY", "")
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY", "")
        self.fetcher = fetcher or self._fetch_url
        self.history: list[dict[str, str]] = []

    def generate_report(self, topic: str) -> dict:
        topic = topic.strip()
        if not topic:
            raise ValueError("Topic is required")

        queries = self._plan_queries(topic)
        sources = self._collect_sources(queries)
        summary = self._reason_about_market(topic, sources)

        report = {
            "topic": topic,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "market_overview": summary["market_overview"],
            "key_trends": summary["key_trends"],
            "major_competitors": summary["major_competitors"],
            "customer_needs": summary["customer_needs"],
            "challenges": summary["challenges"],
            "growth_opportunities": summary["growth_opportunities"],
            "sources": [source.__dict__ for source in sources],
            "context": {
                "previous_topics": [item["topic"] for item in self.history],
            },
        }
        self.history.append({"topic": topic, "generated_at": report["generated_at"]})
        return report

    def _plan_queries(self, topic: str) -> list[str]:
        return [
            f"{topic} market size",
            f"{topic} trends",
            f"{topic} competitors",
            f"{topic} customer needs",
        ]

    def _collect_sources(self, queries: Iterable[str], max_sources: int = 6) -> list[Source]:
        sources: list[Source] = []
        for query in queries:
            try:
                search_result = self._jina_search(query)
            except Exception:
                continue
            for url in self._extract_urls(search_result):
                try:
                    content = self._jina_reader(url)
                except Exception:
                    continue
                snippet = self._to_snippet(content)
                if snippet:
                    sources.append(Source(query=query, url=url, snippet=snippet))
                if len(sources) >= max_sources:
                    return sources
        return sources

    def _jina_search(self, query: str) -> str:
        encoded = parse.quote(query)
        return self.fetcher(
            f"https://s.jina.ai/{encoded}",
            self._auth_headers(self.jina_api_key),
        )

    def _jina_reader(self, url: str) -> str:
        encoded = parse.quote(url, safe=":/?&=%#")
        return self.fetcher(
            f"https://r.jina.ai/{encoded}",
            self._auth_headers(self.jina_api_key),
        )

    def _reason_about_market(self, topic: str, sources: list[Source]) -> dict[str, object]:
        if self.gemini_api_key and sources:
            response = self._gemini_summary(topic, sources)
            if response:
                return response

        unique_domains = sorted({parse.urlparse(source.url).netloc for source in sources if source.url})
        snippets = [source.snippet for source in sources][:3]

        return {
            "market_overview": (
                f"{topic} shows active market interest based on recent web coverage"
                if sources
                else f"Limited live web data retrieved for {topic}; this is a baseline summary"
            ),
            "key_trends": snippets or [f"Demand for {topic} appears to be evolving across segments"],
            "major_competitors": [
                "Identify from source reports and company rankings",
                "Track entrants and incumbent positioning",
            ],
            "customer_needs": [
                "Affordability and value",
                "Product quality, reliability and service",
            ],
            "challenges": [
                "Rapid market shifts and fragmented data sources",
                "Regulatory and cost uncertainty",
            ],
            "growth_opportunities": [
                "Differentiate with focused customer segments",
                "Expand via partnerships and digital channels",
            ],
            "source_domains": unique_domains,
        }

    def _gemini_summary(self, topic: str, sources: list[Source]) -> dict[str, object] | None:
        prompt = {
            "topic": topic,
            "sources": [source.__dict__ for source in sources],
            "output_format": {
                "market_overview": "string",
                "key_trends": ["string"],
                "major_competitors": ["string"],
                "customer_needs": ["string"],
                "challenges": ["string"],
                "growth_opportunities": ["string"],
            },
        }
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
        )
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": (
                                "You are a market research assistant. Return ONLY valid JSON matching "
                                f"the requested output format. Input: {json.dumps(prompt)}"
                            )
                        }
                    ]
                }
            ]
        }

        body = json.dumps(payload).encode("utf-8")
        req = request.Request(url=url, data=body, method="POST")
        req.add_header("Content-Type", "application/json")

        try:
            with request.urlopen(req, timeout=20) as response:
                data = json.loads(response.read().decode("utf-8"))
            text = (
                data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
                .strip()
            )
            return json.loads(text) if text else None
        except Exception:
            return None

    @staticmethod
    def _extract_urls(text: str) -> list[str]:
        urls = re.findall(r"https?://[^\s\]\)\">]+", text)
        deduped: list[str] = []
        for url in urls:
            cleaned = url.rstrip(".,")
            if cleaned not in deduped:
                deduped.append(cleaned)
        return deduped

    @staticmethod
    def _to_snippet(text: str, limit: int = 300) -> str:
        compact = " ".join(text.split())
        return compact[:limit]

    @staticmethod
    def _auth_headers(api_key: str) -> dict[str, str] | None:
        return {"Authorization": "Bearer " + api_key} if api_key else None

    @staticmethod
    def _fetch_url(url: str, headers: dict[str, str] | None = None) -> str:
        req = request.Request(url=url)
        for key, value in (headers or {}).items():
            req.add_header(key, value)
        with request.urlopen(req, timeout=15) as response:
            return response.read().decode("utf-8", errors="replace")


def generate_market_report(topic: str) -> dict:
    return MarketResearchAgent().generate_report(topic)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate a market research report")
    parser.add_argument("topic", help="Research topic, product, industry, or company")
    args = parser.parse_args()

    report = generate_market_report(args.topic)
    print(json.dumps(report, indent=2))
