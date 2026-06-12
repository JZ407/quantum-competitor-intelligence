"""Tests for BibTeX importer."""

import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from lit_review.db.models import Base
from lit_review.db.repository import PaperRepository
from lit_review.importers.bibtex import BibtexImporter


@pytest.fixture
def repo():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine)
    s = Session()
    yield PaperRepository(s)
    s.close()


FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


class TestBibtexImporter:
    def test_import_sample(self, repo):
        importer = BibtexImporter(repo)
        path = os.path.join(FIXTURES_DIR, "sample.bib")
        new, merged = importer.import_file(path)
        assert new == 3
        assert merged == 0

    def test_import_sets_tags_from_keywords(self, repo):
        importer = BibtexImporter(repo)
        path = os.path.join(FIXTURES_DIR, "sample.bib")
        importer.import_file(path)

        papers = repo.search_papers(query="Charge-insensitive")
        assert len(papers) == 1
        tags = [t.name for t in papers[0].tags]
        assert "transmon" in tags

    def test_import_sets_doi(self, repo):
        importer = BibtexImporter(repo)
        path = os.path.join(FIXTURES_DIR, "sample.bib")
        importer.import_file(path)

        papers = repo.search_papers(query="Surface codes")
        assert len(papers) == 1
        assert papers[0].doi == "10.1103/PhysRevA.86.032324"
