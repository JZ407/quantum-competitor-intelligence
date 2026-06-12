"""API clients for literature databases."""

from .arxiv import ArxivClient
from .semantic_scholar import SemanticScholarClient


class APIManager:
    def __init__(self, session, cache_repo, ss_api_key: str | None = None):
        self.session = session
        self.cache = cache_repo
        self.arxiv = ArxivClient(cache_repo)
        self.semantic = SemanticScholarClient(cache_repo, api_key=ss_api_key)

    def search_all(self, query: str, max_results: int = 100) -> list[dict]:
        arxiv_results = self.arxiv.search(query, max_results=max_results)
        arxiv_dois = {r["doi"] for r in arxiv_results if r.get("doi")}
        arxiv_ids = {r["arxiv_id"] for r in arxiv_results if r.get("arxiv_id")}

        ss_results = self.semantic.search(query, limit=min(max_results, 100))
        for r in ss_results:
            if r.get("doi") in arxiv_dois or r.get("arxiv_id") in arxiv_ids:
                continue
            arxiv_results.append(r)

        return arxiv_results
