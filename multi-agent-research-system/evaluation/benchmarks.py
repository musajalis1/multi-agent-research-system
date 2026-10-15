"""Tiny deterministic citation-validity check; not a factuality benchmark."""
import re


def citation_validity(report: str, source_ids: set[str]) -> float:
    markers = re.findall(r"\[(S\d+)\]", report.split("## References")[0])
    return sum(m in source_ids for m in markers) / len(markers) if markers else 0.0


if __name__ == "__main__":
    example = "A claim [S1]. Another [S9]."
    print(f"Citation ID validity (toy example): {citation_validity(example, {'S1'}):.1%}")
