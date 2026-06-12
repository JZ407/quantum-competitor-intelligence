from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy import func

from .models import Paper, Author, Tag, Citation, ApiCache
from . import get_db


class PaperRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_paper(self, paper_data: dict) -> tuple:
        """Add a paper, handling dedup. Returns (paper, is_new, was_merged)."""

        # Normalize: empty strings become None for unique fields
        doi = paper_data.get("doi") or None
        arxiv_id = paper_data.get("arxiv_id") or None
        paper_data["doi"] = doi
        paper_data["arxiv_id"] = arxiv_id

        existing = self._find_duplicate(paper_data)
        if existing:
            self._merge_paper(existing, paper_data)
            return existing, False, True

        paper = Paper(
            title=paper_data["title"],
            abstract=paper_data.get("abstract") or None,
            year=paper_data.get("year"),
            journal=paper_data.get("journal") or None,
            doi=doi,
            arxiv_id=arxiv_id,
            citation_count=paper_data.get("citation_count", 0),
            notes=paper_data.get("notes"),
            pdf_path=paper_data.get("pdf_path") or None,
            source=paper_data.get("source") or None,
        )
        self.session.add(paper)
        self.session.flush()

        if paper_data.get("authors"):
            for i, author_name in enumerate(paper_data["authors"], 1):
                author = self._get_or_create_author(author_name)
                self.session.execute(
                    paper_authors_table().insert().values(
                        paper_id=paper.id, author_id=author.id, position=i
                    )
                )

        if paper_data.get("tags"):
            for tag_name in paper_data["tags"]:
                tag = self._get_or_create_tag(tag_name)
                self.session.execute(
                    paper_tags_table().insert().values(
                        paper_id=paper.id, tag_id=tag.id
                    )
                )

        self.session.commit()
        return paper, True, False

    def get_paper(self, paper_id: int) -> Paper | None:
        return self.session.get(Paper, paper_id)

    def get_paper_by_doi(self, doi: str) -> Paper | None:
        return self.session.query(Paper).filter(Paper.doi == doi).first()

    def get_paper_by_arxiv(self, arxiv_id: str) -> Paper | None:
        return self.session.query(Paper).filter(Paper.arxiv_id == arxiv_id).first()

    def search_papers(
        self,
        query: str | None = None,
        tags: list[str] | None = None,
        status: str | None = None,
        year_from: int | None = None,
        year_to: int | None = None,
    ) -> list[Paper]:
        q = self.session.query(Paper)
        if query:
            like = f"%{query}%"
            q = q.filter(
                (Paper.title.ilike(like)) | (Paper.abstract.ilike(like))
            )
        if tags:
            q = q.filter(Paper.tags.any(Tag.name.in_(tags)))
        if status:
            q = q.filter(Paper.reading_status == status)
        if year_from is not None:
            q = q.filter(Paper.year >= year_from)
        if year_to is not None:
            q = q.filter(Paper.year <= year_to)
        return q.order_by(Paper.year.desc().nulls_last()).all()

    def list_papers(
        self,
        tag: str | None = None,
        status: str | None = None,
    ) -> list[Paper]:
        return self.search_papers(tags=[tag] if tag else None, status=status)

    def update_status(self, paper_id: int, status: str) -> None:
        paper = self.get_paper(paper_id)
        if paper:
            paper.reading_status = status
            paper.updated_at = datetime.now(timezone.utc)
            self.session.commit()

    def add_notes(self, paper_id: int, notes: str) -> None:
        paper = self.get_paper(paper_id)
        if paper:
            paper.notes = notes
            paper.updated_at = datetime.now(timezone.utc)
            self.session.commit()

    def add_tag(self, paper_id: int, tag_name: str) -> None:
        paper = self.get_paper(paper_id)
        if not paper:
            return
        tag = self._get_or_create_tag(tag_name)
        existing = self.session.execute(
            paper_tags_table().select().where(
                (paper_tags_table().c.paper_id == paper_id)
                & (paper_tags_table().c.tag_id == tag.id)
            )
        ).first()
        if not existing:
            self.session.execute(
                paper_tags_table().insert().values(paper_id=paper_id, tag_id=tag.id)
            )
            self.session.commit()

    def remove_tag(self, paper_id: int, tag_name: str) -> None:
        tag = self.session.query(Tag).filter(Tag.name == tag_name).first()
        if not tag:
            return
        self.session.execute(
            paper_tags_table().delete().where(
                (paper_tags_table().c.paper_id == paper_id)
                & (paper_tags_table().c.tag_id == tag.id)
            )
        )
        self.session.commit()

    def get_all_tags(self) -> list[tuple]:
        return (
            self.session.query(Tag.name, func.count(paper_tags_table().c.paper_id))
            .outerjoin(paper_tags_table())
            .group_by(Tag.id)
            .order_by(Tag.name)
            .all()
        )

    def get_stats(self) -> dict:
        total = self.session.query(func.count(Paper.id)).scalar()
        by_status = (
            self.session.query(Paper.reading_status, func.count(Paper.id))
            .group_by(Paper.reading_status)
            .all()
        )
        by_year = (
            self.session.query(Paper.year, func.count(Paper.id))
            .filter(Paper.year.isnot(None))
            .group_by(Paper.year)
            .order_by(Paper.year.desc())
            .all()
        )
        return {
            "total": total,
            "by_status": dict(by_status),
            "by_year": dict(by_year),
        }

    def merge_duplicates(self, keep_id: int, merge_id: int) -> None:
        keep = self.get_paper(keep_id)
        merge = self.get_paper(merge_id)
        if not keep or not merge:
            return

        # Merge tags
        for tag in merge.tags:
            if tag not in keep.tags:
                keep.tags.append(tag)

        # Merge notes
        if merge.notes and not keep.notes:
            keep.notes = merge.notes
        elif merge.notes and keep.notes:
            keep.notes = f"{keep.notes}\n\n--- Merged from paper #{merge_id} ---\n{merge.notes}"

        # Keep richer metadata
        if not keep.abstract and merge.abstract:
            keep.abstract = merge.abstract
        if not keep.doi and merge.doi:
            keep.doi = merge.doi
        if not keep.arxiv_id and merge.arxiv_id:
            keep.arxiv_id = merge.arxiv_id
        if not keep.journal and merge.journal:
            keep.journal = merge.journal
        if not keep.year and merge.year:
            keep.year = merge.year
        if merge.citation_count > keep.citation_count:
            keep.citation_count = merge.citation_count

        # Reassign citations
        self.session.query(Citation).filter(
            Citation.cited_paper_id == merge_id
        ).update({"cited_paper_id": keep_id})
        self.session.query(Citation).filter(
            Citation.paper_id == merge_id
        ).update({"paper_id": keep_id})

        keep.updated_at = datetime.now(timezone.utc)
        self.session.delete(merge)
        self.session.commit()

    def find_all_duplicates(self, threshold: float = 0.85) -> list[tuple]:
        """Find duplicate pairs across the entire database using title similarity."""
        from rapidfuzz import fuzz

        papers = self.session.query(Paper).all()
        duplicates = []
        seen = set()
        for i, p1 in enumerate(papers):
            for p2 in papers[i + 1 :]:
                pair_key = (min(p1.id, p2.id), max(p1.id, p2.id))
                if pair_key in seen:
                    continue
                seen.add(pair_key)
                # Exact match on DOI or arXiv ID
                if p1.doi and p2.doi and p1.doi == p2.doi:
                    duplicates.append((p1, p2, 1.0, "doi"))
                elif p1.arxiv_id and p2.arxiv_id and p1.arxiv_id == p2.arxiv_id:
                    duplicates.append((p1, p2, 1.0, "arxiv_id"))
                else:
                    ratio = fuzz.ratio(
                        p1.title.lower().strip(), p2.title.lower().strip()
                    ) / 100.0
                    if ratio >= threshold:
                        duplicates.append((p1, p2, ratio, "title"))
        return duplicates

    def update_citation_count(self, paper_id: int, count: int) -> None:
        paper = self.get_paper(paper_id)
        if paper:
            paper.citation_count = count
            paper.updated_at = datetime.now(timezone.utc)
            self.session.commit()

    def add_citation(self, paper_id: int, cited_paper_id: int, context: str | None = None) -> None:
        existing = self.session.query(Citation).filter(
            Citation.paper_id == paper_id,
            Citation.cited_paper_id == cited_paper_id,
        ).first()
        if not existing:
            self.session.add(
                Citation(
                    paper_id=paper_id,
                    cited_paper_id=cited_paper_id,
                    context_snippet=context,
                )
            )
            self.session.commit()

    def get_citation_graph(self, paper_id: int) -> dict:
        paper = self.get_paper(paper_id)
        if not paper:
            return {"citing": [], "cited_by": []}
        citing = (
            self.session.query(Paper)
            .join(Citation, Citation.cited_paper_id == Paper.id)
            .filter(Citation.paper_id == paper_id)
            .all()
        )
        cited_by = (
            self.session.query(Paper)
            .join(Citation, Citation.paper_id == Paper.id)
            .filter(Citation.cited_paper_id == paper_id)
            .all()
        )
        return {"citing": citing, "cited_by": cited_by}

    def _find_duplicate(self, data: dict) -> Paper | None:
        if data.get("doi"):
            found = self.get_paper_by_doi(data["doi"])
            if found:
                return found
        if data.get("arxiv_id"):
            found = self.get_paper_by_arxiv(data["arxiv_id"])
            if found:
                return found
        return None

    def _merge_paper(self, existing: Paper, data: dict) -> None:
        changed = False
        if not existing.abstract and data.get("abstract"):
            existing.abstract = data["abstract"]
            changed = True
        if not existing.doi and data.get("doi"):
            existing.doi = data["doi"]
            changed = True
        if not existing.journal and data.get("journal"):
            existing.journal = data["journal"]
            changed = True
        if not existing.year and data.get("year"):
            existing.year = data["year"]
            changed = True
        if data.get("citation_count", 0) > (existing.citation_count or 0):
            existing.citation_count = data["citation_count"]
            changed = True
        if data.get("authors"):
            for i, author_name in enumerate(data["authors"], 1):
                author = self._get_or_create_author(author_name)
                exists = self.session.execute(
                    paper_authors_table().select().where(
                        (paper_authors_table().c.paper_id == existing.id)
                        & (paper_authors_table().c.author_id == author.id)
                    )
                ).first()
                if not exists:
                    self.session.execute(
                        paper_authors_table().insert().values(
                            paper_id=existing.id, author_id=author.id, position=i
                        )
                    )
                    changed = True
        if data.get("tags"):
            for tag_name in data["tags"]:
                tag = self._get_or_create_tag(tag_name)
                exists = self.session.execute(
                    paper_tags_table().select().where(
                        (paper_tags_table().c.paper_id == existing.id)
                        & (paper_tags_table().c.tag_id == tag.id)
                    )
                ).first()
                if not exists:
                    self.session.execute(
                        paper_tags_table().insert().values(
                            paper_id=existing.id, tag_id=tag.id
                        )
                    )
                    changed = True
        if changed:
            existing.updated_at = datetime.now(timezone.utc)
            self.session.commit()

    def _get_or_create_author(self, name: str) -> Author:
        author = self.session.query(Author).filter(Author.full_name == name).first()
        if not author:
            author = Author(full_name=name)
            self.session.add(author)
            self.session.flush()
        return author

    def _get_or_create_tag(self, name: str) -> Tag:
        tag = self.session.query(Tag).filter(Tag.name == name).first()
        if not tag:
            tag = Tag(name=name)
            self.session.add(tag)
            self.session.flush()
        return tag


class CacheRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, endpoint: str, params_hash: str) -> str | None:
        entry = (
            self.session.query(ApiCache)
            .filter(
                ApiCache.endpoint == endpoint,
                ApiCache.params_hash == params_hash,
            )
            .first()
        )
        if entry:
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            age = (now - entry.cached_at).total_seconds()
            if age < entry.ttl_seconds:
                return entry.response_json
            self.session.delete(entry)
            self.session.commit()
        return None

    def set(self, endpoint: str, params_hash: str, response: str, ttl: int = 86400) -> None:
        self.session.merge(
            ApiCache(
                endpoint=endpoint,
                params_hash=params_hash,
                response_json=response,
                ttl_seconds=ttl,
            )
        )
        self.session.commit()

    def clear(self, endpoint: str | None = None) -> int:
        q = self.session.query(ApiCache)
        if endpoint:
            q = q.filter(ApiCache.endpoint == endpoint)
        count = q.count()
        q.delete()
        self.session.commit()
        return count

    def stats(self) -> dict:
        total = self.session.query(func.count(ApiCache.id)).scalar()
        endpoints = (
            self.session.query(ApiCache.endpoint, func.count(ApiCache.id))
            .group_by(ApiCache.endpoint)
            .all()
        )
        return {"total_entries": total, "by_endpoint": dict(endpoints)}


def paper_authors_table():
    from .models import paper_authors

    return paper_authors


def paper_tags_table():
    from .models import paper_tags

    return paper_tags
