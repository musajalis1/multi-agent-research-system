import unittest
from unittest.mock import Mock

from agents.analyst import Analyst
from agents.fact_checker import FactChecker
from agents.report_writer import ReportWriter
from agents.researcher import Researcher
from evaluation.benchmarks import citation_validity
from main import demo, run_pipeline
from tools.models import Source
from tools.search import search_wikipedia


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.sources = [Source("S1", "Test", "https://example.org/test", "The test claim is true.")]

    def test_pipeline_flow(self):
        llm = Mock()
        llm.complete.side_effect = ["Claim [S1]", "SUPPORTED [S1]", "# Report\nClaim [S1]."]
        result = run_pipeline("Question?", Researcher(search=lambda q, n: self.sources),
                              Analyst(llm), FactChecker(llm), ReportWriter(llm))
        self.assertEqual(len(result["sources"]), 1)
        self.assertIn("https://example.org/test", result["report"])
        self.assertEqual(llm.complete.call_count, 3)

    def test_invalid_citation_replaced(self):
        llm = Mock()
        llm.complete.return_value = "Claim [S99] and claim [S1]."
        result = ReportWriter(llm).run("Q", "draft", "audit", self.sources)
        self.assertIn("[citation unavailable]", result)
        self.assertNotIn("[S99]", result)

    def test_empty_sources_rejected(self):
        with self.assertRaises(RuntimeError):
            run_pipeline("Q", Researcher(search=lambda q, n: []), None, None, None)

    def test_citation_metric(self):
        self.assertEqual(citation_validity("A [S1]. B [S2].", {"S1"}), 0.5)

    def test_demo(self):
        self.assertIn("synthetic", demo()["report"].lower())

    def test_search_with_mock_fetcher(self):
        def fake(url):
            if "action=query" in url:
                return {"query": {"search": [{"title": "Machine learning"}]}}
            return {"extract": "ML summary"}
        results = search_wikipedia("machine learning", fetcher=fake)
        self.assertEqual(results[0].id, "S1")
        self.assertEqual(results[0].excerpt, "ML summary")


if __name__ == "__main__":
    unittest.main()
