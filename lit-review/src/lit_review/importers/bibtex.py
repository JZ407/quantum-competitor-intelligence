"""BibTeX file importer using bibtexparser v1."""

import bibtexparser


class BibtexImporter:
    def __init__(self, repo):
        self.repo = repo

    def parse_file(self, path: str) -> list[dict]:
        """Parse a .bib file and return paper data without importing."""
        with open(path, "r", encoding="utf-8") as f:
            bib_db = bibtexparser.load(f)

        results = []
        for entry in bib_db.entries:
            paper_data = self._parse_entry(entry)
            if paper_data.get("title"):
                results.append(paper_data)
        return results

    def import_file(self, path: str, indices: list[int] | None = None) -> tuple[int, int]:
        """Import papers from a .bib file. Returns (new, merged)."""
        with open(path, "r", encoding="utf-8") as f:
            bib_db = bibtexparser.load(f)

        new, merged = 0, 0
        for i, entry in enumerate(bib_db.entries, 1):
            if indices is not None and i not in indices:
                continue
            paper_data = self._parse_entry(entry)
            if not paper_data.get("title"):
                continue
            _, is_new, was_merged = self.repo.add_paper(paper_data)
            if is_new:
                new += 1
            elif was_merged:
                merged += 1

        return new, merged

    def _parse_entry(self, entry: dict) -> dict:
        title = entry.get("title", "").strip()
        abstract = entry.get("abstract", "") or ""
        year = self._parse_year(entry.get("year", ""))
        journal = entry.get("journal", "") or entry.get("booktitle", "") or ""
        doi = entry.get("doi", "") or ""
        arxiv_id = ""

        # Extract arXiv ID from various fields
        eprint = entry.get("eprint", "")
        archive_prefix = entry.get("archiveprefix", "").lower()
        if eprint and archive_prefix == "arxiv":
            arxiv_id = eprint

        # Authors (bibtexparser v1 stores author as a string)
        authors = self._parse_authors(entry.get("author", ""))

        # URL/DOI fallback
        url = entry.get("url", "")
        if not doi and "doi.org" in url:
            doi = url.split("doi.org/")[-1]

        # Tags from keywords
        tags = []
        keywords = entry.get("keywords", "") or entry.get("keyword", "")
        if keywords:
            tags = [k.strip() for k in keywords.replace(";", ",").split(",") if k.strip()]

        return {
            "title": title,
            "abstract": abstract,
            "authors": authors,
            "year": year,
            "journal": journal,
            "doi": doi,
            "arxiv_id": arxiv_id,
            "source": "bibtex",
            "tags": tags,
        }

    def _parse_authors(self, author_str: str) -> list[str]:
        """Parse BibTeX author field into a list of names."""
        if not author_str:
            return []
        names = []
        for author in author_str.split(" and "):
            author = author.strip()
            # Handle "Last, First" and "First Last" formats
            if "," in author:
                parts = author.split(",", 1)
                last = parts[0].strip()
                first = parts[1].strip() if len(parts) > 1 else ""
                names.append(f"{first} {last}".strip())
            else:
                names.append(author)
        return [n for n in names if n]

    def _parse_year(self, year_str: str) -> int | None:
        if not year_str:
            return None
        try:
            return int(year_str.strip()[:4])
        except (ValueError, IndexError):
            return None
