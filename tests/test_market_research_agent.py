import unittest

from src.market_research_agent import MarketResearchAgent


class MarketResearchAgentTests(unittest.TestCase):
    def test_generate_report_structure(self):
        search_text = "Top links: https://example.com/ev-report https://example.org/ev-trends"

        def fake_fetch(url, _headers=None):
            if "s.jina.ai" in url:
                return search_text
            return "Electric vehicle demand is rising with policy support and charging expansion."

        agent = MarketResearchAgent(fetcher=fake_fetch)
        report = agent.generate_report("electric vehicles in India")

        self.assertEqual(report["topic"], "electric vehicles in India")
        self.assertIn("market_overview", report)
        self.assertIn("key_trends", report)
        self.assertIn("major_competitors", report)
        self.assertTrue(report["sources"])

    def test_context_memory_tracks_previous_topics(self):
        def fake_fetch(url, _headers=None):
            if "s.jina.ai" in url:
                return "https://example.com/report"
            return "Sample source content"

        agent = MarketResearchAgent(fetcher=fake_fetch)
        first = agent.generate_report("cloud kitchens")
        second = agent.generate_report("fintech lending")

        self.assertEqual(first["context"]["previous_topics"], [])
        self.assertEqual(second["context"]["previous_topics"], ["cloud kitchens"])


if __name__ == "__main__":
    unittest.main()
