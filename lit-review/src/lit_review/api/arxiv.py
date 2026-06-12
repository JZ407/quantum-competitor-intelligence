"""arXiv API client with Atom XML parsing and caching."""

import json
import time
import xml.etree.ElementTree as ET
import httpx

from ._client import RateLimiter, params_hash


ARXIV_BASE = "https://export.arxiv.org/api/query"
ARXIV_NS = "{http://www.w3.org/2005/Atom}"
OPENSEARCH_NS = "{http://a9.com/-/spec/opensearch/1.1/}"
ARXIV_NS_SHORT = "{http://arxiv.org/schemas/atom}"


class ArxivClient:
    def __init__(self, cache_repo, rate: float = 1 / 3.0):
        self._client = httpx.Client(timeout=30.0)
        self._rate_limiter = RateLimiter(rate)
        self._cache = cache_repo

    def _request_with_retry(self, params: dict, max_retries: int = 5) -> httpx.Response:
        """GET arXiv API with rate-limit retry and exponential backoff."""
        for attempt in range(max_retries):
            self._rate_limiter.wait()
            resp = self._client.get(ARXIV_BASE, params=params)
            if resp.status_code in (429, 503):
                wait = (2 ** attempt) * 10  # 10s, 20s, 40s, 80s, 160s
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp
        resp.raise_for_status()
        return resp

    def search(
        self,
        query: str,
        max_results: int = 100,
        sort_by: str = "relevance",
    ) -> list[dict]:
        max_results = min(max_results, 200)
        cache_key = params_hash("arxiv_search", query, max_results, sort_by)

        cached = self._cache.get("arxiv_search", cache_key)
        if cached:
            return json.loads(cached)

        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results,
            "sortBy": sort_by,
        }
        if sort_by in ("submittedDate", "lastUpdatedDate"):
            params["sortOrder"] = "descending"
        resp = self._request_with_retry(params)

        results = self._parse_atom(resp.text)
        self._cache.set("arxiv_search", cache_key, json.dumps(results), ttl=86400)
        return results

    def fetch_by_id(self, arxiv_id: str) -> dict | None:
        clean_id = arxiv_id.strip()
        cache_key = params_hash("arxiv_by_id", clean_id)

        cached = self._cache.get("arxiv_by_id", cache_key)
        if cached:
            data = json.loads(cached)
            return data[0] if data else None

        self._rate_limiter.wait()
        params = {"id_list": clean_id, "max_results": 1}
        resp = self._client.get(ARXIV_BASE, params=params)
        resp.raise_for_status()

        results = self._parse_atom(resp.text)
        self._cache.set("arxiv_by_id", cache_key, json.dumps(results), ttl=86400)
        return results[0] if results else None

    def _parse_atom(self, xml: str) -> list[dict]:
        root = ET.fromstring(xml)
        papers = []

        for entry in root.findall(f"{ARXIV_NS}entry"):
            title_el = entry.find(f"{ARXIV_NS}title")
            title = title_el.text.strip() if title_el is not None and title_el.text else ""

            abstract_el = entry.find(f"{ARXIV_NS}summary")
            abstract = abstract_el.text.strip() if abstract_el is not None and abstract_el.text else ""

            # Authors
            authors = []
            for author_el in entry.findall(f"{ARXIV_NS}author"):
                name_el = author_el.find(f"{ARXIV_NS}name")
                if name_el is not None and name_el.text:
                    authors.append(name_el.text.strip())

            # arXiv ID
            arxiv_id = ""
            id_el = entry.find(f"{ARXIV_NS}id")
            if id_el is not None and id_el.text:
                raw_id = id_el.text.strip()
                arxiv_id = raw_id.replace("http://arxiv.org/abs/", "").replace("https://arxiv.org/abs/", "")

            # DOI
            doi = ""
            for link in entry.findall(f"{ARXIV_NS}link"):
                if link.get("title") == "doi":
                    doi = link.get("href", "").replace("http://dx.doi.org/", "").replace("https://doi.org/", "")
                    break

            # Categories (primary + secondary)
            categories = []
            primary_cat = entry.find(f"{ARXIV_NS_SHORT}primary_category")
            if primary_cat is not None:
                cat_term = primary_cat.get("term")
                if cat_term:
                    categories.append(cat_term)
            for cat_el in entry.findall(f"{ARXIV_NS}category"):
                cat_term = cat_el.get("term")
                if cat_term and cat_term not in categories:
                    categories.append(cat_term)

            # Year from published date
            year = None
            published_el = entry.find(f"{ARXIV_NS}published")
            if published_el is not None and published_el.text:
                try:
                    year = int(published_el.text.strip()[:4])
                except (ValueError, IndexError):
                    pass

            # Journal ref
            journal = ""
            journal_el = entry.find(f"{ARXIV_NS_SHORT}journal_ref")
            if journal_el is not None and journal_el.text:
                journal = journal_el.text.strip()

            papers.append({
                "title": title,
                "abstract": abstract,
                "authors": authors,
                "arxiv_id": arxiv_id,
                "doi": doi,
                "year": year,
                "journal": journal,
                "categories": categories,
                "source": "arxiv",
            })

        return papers
