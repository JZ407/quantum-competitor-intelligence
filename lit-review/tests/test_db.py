"""Tests for database models and repository."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from lit_review.db.models import Base, Paper, Author, Tag, Citation
from lit_review.db.repository import PaperRepository, CacheRepository


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine)
    s = Session()
    yield s
    s.close()


@pytest.fixture
def repo(session):
    return PaperRepository(session)


@pytest.fixture
def cache_repo(session):
    return CacheRepository(session)


class TestPaperRepository:
    def test_add_paper_basic(self, repo):
        paper, is_new, was_merged = repo.add_paper({
            "title": "Test Paper",
            "abstract": "Test abstract",
            "authors": ["Alice Author", "Bob Coauthor"],
            "year": 2024,
            "doi": "10.1234/test.1",
            "source": "test",
        })

        assert is_new is True
        assert was_merged is False
        assert paper.title == "Test Paper"
        assert len(paper.authors) == 2
        assert paper.authors[0].full_name == "Alice Author"

    def test_add_paper_duplicate_doi(self, repo):
        data = {
            "title": "Original Title",
            "doi": "10.1234/test.dup",
            "source": "test",
        }
        repo.add_paper(data)

        data2 = {
            "title": "Updated Title",
            "doi": "10.1234/test.dup",
            "abstract": "New abstract",
            "source": "test",
        }
        paper, is_new, was_merged = repo.add_paper(data2)

        assert is_new is False
        assert was_merged is True
        assert paper.abstract == "New abstract"
        assert paper.title == "Original Title"

    def test_add_paper_duplicate_arxiv(self, repo):
        data = {"title": "ArXiv Paper", "arxiv_id": "2401.00001", "source": "test"}
        repo.add_paper(data)
        paper, is_new, was_merged = repo.add_paper({
            "title": "ArXiv Paper V2",
            "arxiv_id": "2401.00001",
            "source": "test",
        })
        assert was_merged is True

    def test_add_paper_empty_doi_becomes_none(self, repo):
        """Empty DOI strings should be normalized to None."""
        paper, is_new, _ = repo.add_paper({
            "title": "No DOI Paper",
            "doi": "",
            "source": "test",
        })
        assert paper.doi is None

    def test_search_by_query(self, repo):
        repo.add_paper({"title": "Quantum Computing", "source": "test"})
        repo.add_paper({"title": "Classical Computing", "source": "test"})

        results = repo.search_papers(query="quantum")
        assert len(results) == 1
        assert results[0].title == "Quantum Computing"

    def test_search_by_tag(self, repo):
        repo.add_paper({
            "title": "Tagged Paper",
            "tags": ["quantum"],
            "source": "test",
        })
        repo.add_paper({"title": "Untagged", "source": "test"})

        results = repo.search_papers(tags=["quantum"])
        assert len(results) == 1

    def test_search_by_status(self, repo):
        repo.add_paper({"title": "Unread Paper", "source": "test"})
        repo.add_paper({"title": "Reading Paper", "source": "test"})
        repo.search_papers()
        # Update one to 'done'
        papers = repo.session.query(Paper).all()
        repo.update_status(papers[0].id, "done")

        results = repo.search_papers(status="done")
        assert len(results) == 1

    def test_update_status(self, repo):
        paper, _, _ = repo.add_paper({"title": "Status Test", "source": "test"})
        repo.update_status(paper.id, "reading")
        p = repo.get_paper(paper.id)
        assert p.reading_status == "reading"

    def test_add_notes(self, repo):
        paper, _, _ = repo.add_paper({"title": "Notes Test", "source": "test"})
        repo.add_notes(paper.id, "Important findings")
        p = repo.get_paper(paper.id)
        assert p.notes == "Important findings"

    def test_add_tag(self, repo):
        paper, _, _ = repo.add_paper({"title": "Tag Test", "source": "test"})
        repo.add_tag(paper.id, "important")
        assert len(paper.tags) == 1
        assert paper.tags[0].name == "important"

    def test_remove_tag(self, repo):
        paper, _, _ = repo.add_paper({
            "title": "Tag Remove Test",
            "tags": ["temp"],
            "source": "test",
        })
        assert len(paper.tags) == 1
        repo.remove_tag(paper.id, "temp")
        session = repo.session
        session.refresh(paper)
        assert len(paper.tags) == 0

    def test_get_all_tags(self, repo):
        repo.add_paper({
            "title": "P1",
            "tags": ["tag1", "tag2"],
            "source": "test",
        })
        repo.add_paper({
            "title": "P2",
            "tags": ["tag1"],
            "source": "test",
        })
        tags = repo.get_all_tags()
        tag_names = [t[0] for t in tags]
        assert "tag1" in tag_names
        assert "tag2" in tag_names

    def test_get_stats(self, repo):
        repo.add_paper({"title": "P1", "year": 2023, "source": "test"})
        repo.add_paper({"title": "P2", "year": 2023, "source": "test"})
        repo.add_paper({"title": "P3", "year": 2024, "source": "test"})

        st = repo.get_stats()
        assert st["total"] == 3
        assert st["by_year"][2023] == 2
        assert st["by_year"][2024] == 1

    def test_merge_duplicates(self, repo):
        p1, _, _ = repo.add_paper({
            "title": "Keep Me",
            "doi": "10.1234/keep",
            "tags": ["tagA"],
            "source": "test",
        })
        p2, _, _ = repo.add_paper({
            "title": "Merge Me",
            "tags": ["tagB"],
            "notes": "Merged notes",
            "source": "test",
        })

        repo.merge_duplicates(p1.id, p2.id)
        keep = repo.get_paper(p1.id)
        assert keep is not None
        assert repo.get_paper(p2.id) is None
        tag_names = [t.name for t in keep.tags]
        assert "tagB" in tag_names
        assert "Merged notes" in (keep.notes or "")

    def test_citation_graph(self, repo):
        p1, _, _ = repo.add_paper({"title": "Citing", "source": "test"})
        p2, _, _ = repo.add_paper({"title": "Cited", "source": "test"})

        repo.add_citation(p1.id, p2.id)
        graph = repo.get_citation_graph(p1.id)
        assert len(graph["citing"]) == 1
        assert graph["citing"][0].id == p2.id
        assert len(graph["cited_by"]) == 0

        graph2 = repo.get_citation_graph(p2.id)
        assert len(graph2["citing"]) == 0
        assert len(graph2["cited_by"]) == 1


class TestCacheRepository:
    def test_set_and_get(self, cache_repo):
        cache_repo.set("test", "abc123", '{"data": "hello"}')
        result = cache_repo.get("test", "abc123")
        assert result == '{"data": "hello"}'

    def test_miss(self, cache_repo):
        result = cache_repo.get("nonexistent", "hash")
        assert result is None

    def test_clear(self, cache_repo):
        cache_repo.set("ep1", "h1", "data1")
        cache_repo.set("ep2", "h2", "data2")
        assert cache_repo.clear(endpoint="ep1") == 1
        assert cache_repo.stats()["total_entries"] == 1
        assert cache_repo.clear() == 1
        assert cache_repo.stats()["total_entries"] == 0
