"""CLI entrypoint for the multi-agent research pipeline."""
import argparse
import json
from pathlib import Path

from agents.analyst import Analyst
from agents.fact_checker import FactChecker
from agents.report_writer import ReportWriter
from agents.researcher import Researcher
from configs.settings import Settings
from tools.llm import ChatLLM
from tools.models import Source


def run_pipeline(question, researcher, analyst, checker, writer):
    sources = researcher.run(question)
    if not sources:
        raise RuntimeError("No sources found; try a broader question")
    draft = analyst.run(question, sources)
    audit = checker.run(draft, sources)
    report = writer.run(question, draft, audit, sources)
    return {"question": question, "sources": [s.to_dict() for s in sources],
            "draft": draft, "audit": audit, "report": report}


def demo():
    source = Source("S1", "Example source (synthetic)", "https://example.org/demo", "RAG combines retrieval with generation.")
    return {"question": "What is RAG?", "sources": [source.to_dict()],
            "draft": "RAG combines retrieval with generation [S1].",
            "audit": "SUPPORTED: This is directly stated in the synthetic excerpt [S1].",
            "report": "# What is RAG?\n\n## Executive summary\n\nRetrieval-augmented generation combines retrieval with generation [S1].\n\n## Limitations\n\nThis is an offline synthetic example, not live research.\n\n## References\n\n- [S1] [Example source (synthetic)](https://example.org/demo)\n"}


def main():
    parser = argparse.ArgumentParser(description="Multi-agent research CLI")
    parser.add_argument("question", nargs="?", help="Research question")
    parser.add_argument("--output", default="report.md", help="Markdown report path")
    parser.add_argument("--demo", action="store_true", help="Offline synthetic example")
    args = parser.parse_args()
    if not args.demo and not args.question:
        parser.error("provide a question or --demo")
    if args.demo:
        result = demo()
    else:
        settings = Settings.from_env()
        llm = ChatLLM(settings.api_key, settings.model, settings.base_url)
        result = run_pipeline(args.question, Researcher(max_sources=settings.max_sources),
                              Analyst(llm), FactChecker(llm), ReportWriter(llm))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(result["report"], encoding="utf-8")
    trace = output.with_suffix(output.suffix + ".json")
    trace.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Report: {output}\nTrace: {trace}")


if __name__ == "__main__":
    main()
