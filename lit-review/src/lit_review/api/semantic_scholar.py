"""Semantic Scholar API client."""

import json
import time
import httpx

from ._client import RateLimiter, params_hash


SS_BASE = "https://api.semanticscholar.org/graph/v1"

SEARCH_FIELDS = "title,authors,year,journal,externalIds,citationCount,abstract"


class SemanticScholarClient:
    def __init__(self, cache_repo, api_key: str | None = None):
        self._client = httpx.Client(timeout=30.0)
        headers = {}
        if api_key:
            headers["x-api-key"] = api_key
        self._headers = headers
        self._rate_limiter = RateLimiter(10.0 if api_key else 1.0)
        self._cache = cache_repo

    def _request_with_retry(self, url: str, params: dict, max_retries: int = 5) -> httpx.Response:
        for attempt in range(max_retries):
            self._rate_limiter.wait()
            resp = self._client.get(url, params=params, headers=self._headers)
            if resp.status_code == 429:
                wait = (2 ** attempt) * 10  # 10s, 20s, 40s, 80s, 160s
                time.sleep(wait)
                continue
            if resp.status_code >= 500:
                time.sleep((2 ** attempt) * 3)
                continue
            resp.raise_for_status()
            return resp
        resp.raise_for_status()
        return resp

    def search(self, query: str, limit: int = 100) -> list[dict]:
        limit = min(limit, 100)
        cache_key = params_hash("semantic_search", query, limit)

        cached = self._cache.get("semantic_search", cache_key)
        if cached:
            return json.loads(cached)

        params = {
            "query": query,
            "limit": limit,
            "fields": SEARCH_FIELDS,
        }
        resp = self._request_with_retry(f"{SS_BASE}/paper/search", params)
        data = resp.json()

        results = []
        for item in data.get("data", []):
            results.append(self._normalize(item))

        self._cache.set("semantic_search", cache_key, json.dumps(results), ttl=86400)
        return results

    def get_citation_count(self, paper_id: str) -> int | None:
        self._rate_limiter.wait()
        params = {"fields": "citationCount"}
        resp = self._client.get(
            f"{SS_BASE}/paper/{paper_id}",
            params=params,
            headers=self._headers,
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json().get("citationCount", 0)

    def get_references(self, paper_id: str, limit: int = 100) -> list[dict]:
        cache_key = params_hash("semantic_references", paper_id, limit)
        cached = self._cache.get("semantic_references", cache_key)
        if cached:
            return json.loads(cached)

        self._rate_limiter.wait()
        params = {"limit": limit, "fields": SEARCH_FIELDS}
        resp = self._client.get(
            f"{SS_BASE}/paper/{paper_id}/references",
            params=params,
            headers=self._headers,
        )
        resp.raise_for_status()
        data = resp.json()

        results = []
        for item in data.get("data", []):
            paper_data = item.get("citedPaper", {})
            if paper_data:
                results.append(self._normalize(paper_data))

        self._cache.set("semantic_references", cache_key, json.dumps(results), ttl=86400)
        return results

    def get_citations(self, paper_id: str, limit: int = 100) -> list[dict]:
        cache_key = params_hash("semantic_citations", paper_id, limit)
        cached = self._cache.get("semantic_citations", cache_key)
        if cached:
            return json.loads(cached)

        self._rate_limiter.wait()
        params = {"limit": limit, "fields": SEARCH_FIELDS}
        resp = self._client.get(
            f"{SS_BASE}/paper/{paper_id}/citations",
            params=params,
            headers=self._headers,
        )
        resp.raise_for_status()
        data = resp.json()

        results = []
        for item in data.get("data", []):
            paper_data = item.get("citingPaper", {})
            if paper_data:
                results.append(self._normalize(paper_data))

        self._cache.set("semantic_citations", cache_key, json.dumps(results), ttl=86400)
        return results

    def _normalize(self, item: dict) -> dict:
        ext_ids = item.get("externalIds", {}) or {}
        return {
            "title": item.get("title", ""),
            "abstract": item.get("abstract", ""),
            "authors": [a.get("name", "") for a in item.get("authors", [])],
            "year": item.get("year"),
            "journal": (item.get("journal", {}) or {}).get("name", ""),
            "doi": ext_ids.get("DOI", ""),
            "arxiv_id": ext_ids.get("ArXiv", ""),
            "citation_count": item.get("citationCount", 0),
            "source": "semantic_scholar",
            "tags": item.get("s2FieldsOfStudy", []),
        }
