"""Tests for Markdown exporter."""

import os
import tempfile
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from lit_review.db.models import Base
from lit_review.db.repository import PaperRepository
from lit_review.export.markdown import ReviewExporter


@pytest.fixture
def repo():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine)
    s = Session()
    yield PaperRepository(s)
    s.close()


class TestReviewExporter:
    def test_export_basic(self, repo):
        repo.add_paper({
            "title": "Test Quantum Paper",
            "abstract": "Abstract text",
            "authors": ["Alice Author"],
            "year": 2024,
            "doi": "10.1234/test",
            "tags": ["quantum"],
            "source": "test",
        })

        exporter = ReviewExporter(repo)
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
            output_path = f.name

        try:
            result = exporter.export(
                output_path=output_path,
                title="Test Review",
                include_bibtex=True,
            )
            assert os.path.exists(result)
            with open(result, "r", encoding="utf-8") as f:
                content = f.read()

            assert "# Literature Review: Test Review" in content
            assert "Test Quantum Paper" in content
            assert "Alice Author" in content
            assert "10.1234/test" in content
            assert "## quantum" in content
            assert "## Bibliography" in content
            assert "@article{Author2024" in content
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_export_filter_by_tag(self, repo):
        repo.add_paper({
            "title": "Tagged Paper",
            "tags": ["include_me"],
            "source": "test",
        })
        repo.add_paper({
            "title": "Other Paper",
            "tags": ["exclude_me"],
            "source": "test",
        })

        exporter = ReviewExporter(repo)
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
            output_path = f.name

        try:
            exporter.export(
                output_path=output_path,
                title="Filtered Review",
                tags=["include_me"],
            )
            with open(output_path, "r", encoding="utf-8") as f:
                content = f.read()

            assert "Tagged Paper" in content
            assert "Other Paper" not in content
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_export_no_bibtex(self, repo):
        repo.add_paper({"title": "No BibTeX Paper", "source": "test"})

        exporter = ReviewExporter(repo)
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
            output_path = f.name

        try:
            exporter.export(
                output_path=output_path,
                title="Test",
                include_bibtex=False,
            )
            with open(output_path, "r", encoding="utf-8") as f:
                content = f.read()

            assert "*No BibTeX entries available.*" in content
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
