"""Markdown review exporter using Jinja2 templates."""

import os
from datetime import datetime, timezone
from jinja2 import Environment, FileSystemLoader, select_autoescape

from lit_review.db.models import Paper


class ReviewExporter:
    def __init__(self, repo):
        self.repo = repo

        template_dir = os.path.dirname(os.path.abspath(__file__))
        self._env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(),
        )
        self._template = self._env.get_template("template.md.j2")

    def export(
        self,
        output_path: str,
        title: str = "Literature Review",
        description: str | None = None,
        tags: list[str] | None = None,
        status: str | None = None,
        include_bibtex: bool = True,
    ) -> str:
        """Generate the review document. Returns the output path."""

        # Fetch papers grouped by tag
        papers = self.repo.search_papers(tags=tags, status=status)

        # Group papers by tag; untagged go in "Uncategorized"
        by_tag: dict[str, list[Paper]] = {}
        if tags:
            for tag in tags:
                by_tag[tag] = []
        by_tag["Uncategorized"] = []

        seen = set()
        for p in papers:
            tagged = False
            for tag in p.tags:
                tag_name = tag.name
                if tags is None or tag_name in tags:
                    if tag_name not in by_tag:
                        by_tag[tag_name] = []
                    if p.id not in seen:
                        by_tag[tag_name].append(p)
                        seen.add(p.id)
                        tagged = True
            if not tagged and p.id not in seen:
                by_tag["Uncategorized"].append(p)
                seen.add(p.id)

        if not tags:
            by_tag.pop("Uncategorized", None)

        # Build sections, sort papers by year descending within each section
        sections = []
        for tag_name, tag_papers in sorted(by_tag.items()):
            if not tag_papers:
                continue
            tag_papers.sort(key=lambda p: (p.year or 0), reverse=True)
            sections.append({
                "heading": tag_name,
                "anchor": tag_name.lower().replace(" ", "-"),
                "papers": [
                    {
                        "title": p.title,
                        "authors": ", ".join(a.full_name for a in p.authors) if p.authors else "N/A",
                        "year": str(p.year) if p.year else "N/A",
                        "journal": p.journal or "N/A",
                        "doi": p.doi or "",
                        "arxiv_id": p.arxiv_id or "",
                        "citation_count": p.citation_count or 0,
                        "reading_status": p.reading_status,
                        "tags": ", ".join(t.name for t in p.tags) if p.tags else "",
                        "abstract": p.abstract or "*No abstract available.*",
                        "notes": p.notes or "",
                        "cite_key": self._cite_key(p),
                    }
                    for p in tag_papers
                ],
            })

        bibtex_entries = []
        if include_bibtex:
            all_papers = []
            for section in sections:
                for pd in section["papers"]:
                    all_papers.append(pd)
            for pd in all_papers:
                bibtex_entries.append(self._format_bibtex(pd))

        html = self._template.render(
            title=title,
            date=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            description=description,
            sections=sections,
            bibtex_entries=bibtex_entries,
        )

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

        return output_path

    def _cite_key(self, paper: Paper) -> str:
        """Generate a citation key: first author surname + year."""
        if paper.authors:
            surname = paper.authors[0].full_name.split()[-1]
        else:
            surname = "Unknown"
        year = paper.year or "0000"
        return f"{surname}{year}"

    def _format_bibtex(self, pd: dict) -> str:
        """Format a paper as a BibTeX entry."""
        cite_key = pd["cite_key"]
        authors = " and ".join(pd["authors"].split(", "))
        lines = [f"@article{{{cite_key},"]
        lines.append(f"  title = {{{{{pd['title']}}}}},")
        lines.append(f"  author = {{{{{authors}}}}},")
        if pd["year"] != "N/A":
            lines.append(f"  year = {{{{{pd['year']}}}}},")
        if pd["journal"] != "N/A":
            lines.append(f"  journal = {{{{{pd['journal']}}}}},")
        if pd["doi"]:
            lines.append(f"  doi = {{{{{pd['doi']}}}}},")
        if pd["arxiv_id"]:
            lines.append(f"  archiveprefix = {{arXiv}},")
            lines.append(f"  eprint = {{{{{pd['arxiv_id']}}}}},")
        lines.append("}")
        return "\n".join(lines)
