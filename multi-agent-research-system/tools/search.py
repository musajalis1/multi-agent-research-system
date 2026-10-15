"""MediaWiki search: one discovery API, one summary API, no HTML scraping."""
import json
from urllib.parse import urlencode, quote
from urllib.request import Request, urlopen
from tools.models import Source


USER_AGENT = "MultiAgentResearchPortfolio/1.0 (educational example)"


def fetch_json(url: str) -> dict:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urlopen(request, timeout=15) as response:
        return json.load(response)


def search_wikipedia(query: str, limit: int = 5, fetcher=fetch_json) -> list[Source]:
    params = urlencode({"action": "query", "list": "search", "srsearch": query,
                        "srlimit": limit, "format": "json", "utf8": 1})
    data = fetcher("https://en.wikipedia.org/w/api.php?" + params)
    hits = data.get("query", {}).get("search", [])
    sources = []
    for hit in hits[:limit]:
        title = hit["title"]
        url = "https://en.wikipedia.org/wiki/" + quote(title.replace(" ", "_"), safe="()")
        try:
            summary = fetcher("https://en.wikipedia.org/api/rest_v1/page/summary/" + quote(title.replace(" ", "_"), safe="()"))
            excerpt = summary.get("extract", "")[:1600]
        except (OSError, ValueError, KeyError):
            continue
        if excerpt:
            sources.append(Source(f"S{len(sources)+1}", title, url, excerpt))
    return sources
