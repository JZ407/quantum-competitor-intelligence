"""Literature review CLI for superconducting quantum computing."""

import sys
import typer
from rich.console import Console
from rich.table import Table

# Force UTF-8 encoding on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

console = Console()
app = typer.Typer(
    name="lit-review",
    help="Literature review tool for superconducting quantum computing",
)

search_app = typer.Typer(help="Search literature databases")
import_app = typer.Typer(help="Import papers from various sources")
tag_app = typer.Typer(help="Manage paper tags")
export_app = typer.Typer(help="Export review documents")
cache_app = typer.Typer(help="Manage API cache")
config_app = typer.Typer(help="View and set configuration")

app.add_typer(search_app, name="search")
app.add_typer(import_app, name="import")
app.add_typer(tag_app, name="tag")
app.add_typer(export_app, name="export")
app.add_typer(cache_app, name="cache")
app.add_typer(config_app, name="config")

# ── Path to DB ──────────────────────────────────────────────
import os
from lit_review.db import get_db
from lit_review.db.repository import PaperRepository, CacheRepository
from lit_review.api import ArxivClient, SemanticScholarClient, APIManager
from lit_review.importers.bibtex import BibtexImporter
from lit_review.export.markdown import ReviewExporter
from lit_review import config as cfg

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "literature.db")
_engine = None
_SessionLocal = None


def get_session():
    global _engine, _SessionLocal
    if _engine is None:
        _engine, _SessionLocal = get_db(DB_PATH)
    return _SessionLocal()


def _paper_data(r: dict) -> dict:
    """Convert search result dict to paper data for repository."""
    return {
        "title": r.get("title", ""),
        "abstract": r.get("abstract", ""),
        "authors": r.get("authors", []),
        "year": r.get("year"),
        "journal": r.get("journal", ""),
        "doi": r.get("doi", ""),
        "arxiv_id": r.get("arxiv_id", ""),
        "citation_count": r.get("citation_count", 0),
        "source": r.get("source", ""),
        "tags": r.get("categories", []) + [t for t in r.get("tags", []) if isinstance(t, str)],
    }


def _import_results(repo: PaperRepository, results: list[dict], indices: list[int] | None = None) -> tuple[int, int]:
    """Import selected search results into DB. Returns (new, merged)."""
    new, merged = 0, 0
    for i, r in enumerate(results, 1):
        if indices is not None and i not in indices:
            continue
        _, is_new, was_merged = repo.add_paper(_paper_data(r))
        if is_new:
            new += 1
        elif was_merged:
            merged += 1
    return new, merged


def _prompt_save(results: list[dict]) -> list[int] | None:
    """Ask user which results to save. Returns list of 1-based indices, or None to skip."""
    console.print("\n[bold]Save to database?[/bold]")
    console.print("  [a]ll   — save all results")
    console.print("  [1,3,5] — save specific papers by number (e.g. 1,3,5-8)")
    console.print("  [n]one  — don't save anything")

    choice = typer.prompt("Choice", default="n").strip().lower()

    if choice in ("n", "none", ""):
        return None

    if choice in ("a", "all"):
        return list(range(1, len(results) + 1))

    # Parse individual numbers and ranges: "1,3,5-8"
    indices = []
    for part in choice.split(","):
        part = part.strip()
        if "-" in part:
            try:
                lo, hi = part.split("-", 1)
                indices.extend(range(int(lo), int(hi) + 1))
            except ValueError:
                console.print(f"[red]Invalid range: {part}[/red]")
                return None
        else:
            try:
                indices.append(int(part))
            except ValueError:
                console.print(f"[red]Invalid number: {part}[/red]")
                return None

    indices = [i for i in indices if 1 <= i <= len(results)]
    return indices if indices else None


# ── search ───────────────────────────────────────────────────

@search_app.command("arxiv")
def search_arxiv(
    query: str = typer.Argument(..., help="Search query string"),
    max_results: int = typer.Option(100, "--max-results", "-n", help="Max results (1-200)"),
):
    """Search arXiv for papers."""
    session = get_session()
    cache_repo = CacheRepository(session)
    client = ArxivClient(cache_repo)

    with console.status(f"[bold]Searching arXiv for: {query}[/bold]"):
        results = client.search(query, max_results=max_results)

    if not results:
        console.print("[dim]No results found.[/dim]")
        session.close()
        return

    console.print(f"[bold]arXiv: {len(results)} results for '{query}'[/bold]\n")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("#", width=4)
    table.add_column("Title", width=65)
    table.add_column("Year", width=6)
    table.add_column("Authors", width=35)

    for i, r in enumerate(results, 1):
        authors_str = ", ".join(r.get("authors", [])[:3])
        if len(r.get("authors", [])) > 3:
            authors_str += " et al."
        table.add_row(
            str(i),
            r["title"][:62] + "..." if len(r["title"]) > 65 else r["title"],
            str(r.get("year", "-")),
            authors_str,
        )
    console.print(table)

    indices = _prompt_save(results)
    if indices:
        repo = PaperRepository(session)
        new, merged = _import_results(repo, results, indices)
        console.print(f"[green]Saved: {new} new, {merged} merged[/green]")
    else:
        console.print("[dim]Nothing saved.[/dim]")

    session.close()


@search_app.command("semantic")
def search_semantic(
    query: str = typer.Argument(..., help="Search query string"),
    max_results: int = typer.Option(100, "--max-results", "-n", help="Max results"),
):
    """Search Semantic Scholar for papers."""
    session = get_session()
    cache_repo = CacheRepository(session)
    client = SemanticScholarClient(cache_repo)

    with console.status(f"[bold]Searching Semantic Scholar for: {query}[/bold]"):
        results = client.search(query, limit=min(max_results, 100))

    if not results:
        console.print("[dim]No results found.[/dim]")
        session.close()
        return

    console.print(f"[bold]Semantic Scholar: {len(results)} results for '{query}'[/bold]\n")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("#", width=4)
    table.add_column("Title", width=65)
    table.add_column("Year", width=6)
    table.add_column("Citations", width=10)
    table.add_column("Authors", width=35)

    for i, r in enumerate(results, 1):
        authors_str = ", ".join(r.get("authors", [])[:3])
        if len(r.get("authors", [])) > 3:
            authors_str += " et al."
        table.add_row(
            str(i),
            r["title"][:62] + "..." if len(r["title"]) > 65 else r["title"],
            str(r.get("year", "-")),
            str(r.get("citation_count", 0)),
            authors_str,
        )
    console.print(table)

    indices = _prompt_save(results)
    if indices:
        repo = PaperRepository(session)
        new, merged = _import_results(repo, results, indices)
        console.print(f"[green]Saved: {new} new, {merged} merged[/green]")
    else:
        console.print("[dim]Nothing saved.[/dim]")

    session.close()


@search_app.command("all")
def search_all(
    query: str = typer.Argument(..., help="Search query string"),
    max_results: int = typer.Option(100, "--max-results", "-n", help="Max results per source"),
):
    """Search both arXiv and Semantic Scholar (deduplicated)."""
    session = get_session()
    cache_repo = CacheRepository(session)
    api = APIManager(session, cache_repo)

    with console.status(f"[bold]Searching for: {query}[/bold]"):
        results = api.search_all(query, max_results=max_results)

    if not results:
        console.print("[dim]No results found.[/dim]")
        session.close()
        return

    console.print(f"[bold]Unified search: {len(results)} results for '{query}'[/bold]\n")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("#", width=4)
    table.add_column("Title", width=60)
    table.add_column("Year", width=6)
    table.add_column("Source", width=15)
    table.add_column("Authors", width=35)

    for i, r in enumerate(results, 1):
        authors_str = ", ".join(r.get("authors", [])[:3])
        if len(r.get("authors", [])) > 3:
            authors_str += " et al."
        table.add_row(
            str(i),
            r["title"][:57] + "..." if len(r["title"]) > 60 else r["title"],
            str(r.get("year", "-")),
            r.get("source", ""),
            authors_str,
        )
    console.print(table)

    indices = _prompt_save(results)
    if indices:
        repo = PaperRepository(session)
        new, merged = _import_results(repo, results, indices)
        console.print(f"[green]Saved: {new} new, {merged} merged[/green]")
    else:
        console.print("[dim]Nothing saved.[/dim]")

    session.close()


# ── import ───────────────────────────────────────────────────

@import_app.command("bibtex")
def import_bibtex(
    file: str = typer.Argument(..., help="Path to .bib file"),
):
    """Import papers from a BibTeX file."""
    if not os.path.exists(file):
        console.print(f"[red]File not found: {file}[/red]")
        raise typer.Exit(1)

    session = get_session()
    repo = PaperRepository(session)
    importer = BibtexImporter(repo)

    # Parse first, show results
    entries = importer.parse_file(file)
    if not entries:
        console.print("[dim]No valid entries found.[/dim]")
        session.close()
        return

    console.print(f"[bold]{file}: {len(entries)} entries[/bold]\n")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("#", width=4)
    table.add_column("Title", width=65)
    table.add_column("Year", width=6)
    table.add_column("Authors", width=35)

    for i, e in enumerate(entries, 1):
        authors_str = ", ".join(e.get("authors", [])[:3])
        if len(e.get("authors", [])) > 3:
            authors_str += " et al."
        table.add_row(
            str(i),
            e["title"][:62] + "..." if len(e["title"]) > 65 else e["title"],
            str(e.get("year", "-")),
            authors_str,
        )
    console.print(table)

    indices = _prompt_save(entries)
    if indices:
        new, merged = importer.import_file(file, indices)
        console.print(f"[green]Saved: {new} new, {merged} merged[/green]")
    else:
        console.print("[dim]Nothing saved.[/dim]")

    session.close()


# ── list ─────────────────────────────────────────────────────

@app.command("list")
def list_papers(
    tag: str = typer.Option(None, "--tag", "-t", help="Filter by tag"),
    status: str = typer.Option(None, "--status", "-s", help="Filter by reading status"),
    year: int = typer.Option(None, "--year", "-y", help="Filter by year"),
    query: str = typer.Option(None, "--query", "-q", help="Search in title/abstract"),
    stats: bool = typer.Option(False, "--stats", help="Show aggregate statistics"),
):
    """List papers in the local database."""
    session = get_session()
    repo = PaperRepository(session)

    if stats:
        st = repo.get_stats()
        console.print(f"[bold]Total papers:[/bold] {st['total']}")
        if st["by_status"]:
            console.print("[bold]By status:[/bold]")
            for s, c in st["by_status"].items():
                console.print(f"  {s}: {c}")
        if st["by_year"]:
            console.print("[bold]By year (top 10):[/bold]")
            for yr, c in list(st["by_year"].items())[:10]:
                console.print(f"  {yr}: {c}")
        session.close()
        return

    papers = repo.search_papers(query=query, tags=[tag] if tag else None, status=status)
    if year:
        papers = [p for p in papers if p.year == year]

    if not papers:
        console.print("[dim]No papers found.[/dim]")
    else:
        table = Table(title="Papers", show_header=True, header_style="bold cyan")
        table.add_column("ID", style="dim", width=5)
        table.add_column("Title", width=60)
        table.add_column("Year", width=6)
        table.add_column("Citations", width=10)
        table.add_column("Status", width=10)
        table.add_column("Tags", width=30)

        for p in papers:
            tags_str = ", ".join(t.name for t in p.tags) if p.tags else ""
            table.add_row(
                str(p.id),
                p.title[:57] + "..." if len(p.title) > 60 else p.title,
                str(p.year) if p.year else "-",
                str(p.citation_count),
                p.reading_status,
                tags_str,
            )

        console.print(table)
        console.print(f"[dim]{len(papers)} paper(s)[/dim]")

    session.close()


# ── show ─────────────────────────────────────────────────────

@app.command("show")
def show_paper(
    paper_id: int = typer.Argument(..., help="Paper ID to display"),
):
    """Show full details of a paper."""
    session = get_session()
    repo = PaperRepository(session)
    paper = repo.get_paper(paper_id)

    if not paper:
        console.print(f"[red]Paper #{paper_id} not found.[/red]")
        session.close()
        return

    console.print(f"[bold cyan]{paper.title}[/bold cyan]")
    console.print(f"[dim]ID: {paper.id} | Status: {paper.reading_status} | Citations: {paper.citation_count}[/dim]")
    if paper.authors:
        console.print(f"Authors: {', '.join(a.full_name for a in paper.authors)}")
    if paper.year:
        console.print(f"Year: {paper.year}")
    if paper.journal:
        console.print(f"Journal: {paper.journal}")
    if paper.doi:
        console.print(f"DOI: {paper.doi}")
    if paper.arxiv_id:
        console.print(f"arXiv: {paper.arxiv_id}")
    if paper.tags:
        console.print(f"Tags: {', '.join(t.name for t in paper.tags)}")
    if paper.abstract:
        console.print(f"\n[bold]Abstract:[/bold]\n{paper.abstract}")
    if paper.notes:
        console.print(f"\n[bold]Notes:[/bold]\n{paper.notes}")
    if paper.pdf_path:
        console.print(f"\nPDF: {paper.pdf_path}")

    # Citation graph
    citation_graph = repo.get_citation_graph(paper_id)
    if citation_graph["citing"]:
        console.print(f"\n[bold]Cites ({len(citation_graph['citing'])}):[/bold]")
        for cp in citation_graph["citing"]:
            console.print(f"  [{cp.id}] {cp.title[:80]}")
    if citation_graph["cited_by"]:
        console.print(f"\n[bold]Cited by ({len(citation_graph['cited_by'])}):[/bold]")
        for cp in citation_graph["cited_by"]:
            console.print(f"  [{cp.id}] {cp.title[:80]}")

    session.close()


# ── tag ──────────────────────────────────────────────────────

@tag_app.command("add")
def tag_add(
    paper_id: int = typer.Argument(..., help="Paper ID"),
    tag_name: str = typer.Argument(..., help="Tag to add"),
):
    """Add a tag to a paper."""
    session = get_session()
    repo = PaperRepository(session)
    repo.add_tag(paper_id, tag_name)
    console.print(f"[green]Added tag '{tag_name}' to paper #{paper_id}[/green]")
    session.close()


@tag_app.command("remove")
def tag_remove(
    paper_id: int = typer.Argument(..., help="Paper ID"),
    tag_name: str = typer.Argument(..., help="Tag to remove"),
):
    """Remove a tag from a paper."""
    session = get_session()
    repo = PaperRepository(session)
    repo.remove_tag(paper_id, tag_name)
    console.print(f"[green]Removed tag '{tag_name}' from paper #{paper_id}[/green]")
    session.close()


@tag_app.command("list")
def tag_list(
    tag_name: str = typer.Argument(None, help="Tag to list papers for (omit for all tags)"),
):
    """List all tags or papers for a specific tag."""
    session = get_session()
    repo = PaperRepository(session)

    if tag_name:
        papers = repo.list_papers(tag=tag_name)
        console.print(f"[bold]Papers tagged '{tag_name}' ({len(papers)}):[/bold]")
        for p in papers:
            authors_str = ", ".join(a.full_name for a in p.authors[:3])
            if len(p.authors) > 3:
                authors_str += " et al."
            console.print(f"  [{p.id}] {p.title[:70]} ({p.year}) - {authors_str}")
    else:
        tags = repo.get_all_tags()
        if not tags:
            console.print("[dim]No tags defined.[/dim]")
        else:
            table = Table(title="All Tags")
            table.add_column("Tag", style="cyan")
            table.add_column("Papers", justify="right")
            for name, count in tags:
                table.add_row(name, str(count or 0))
            console.print(table)

    session.close()


# ── status ───────────────────────────────────────────────────

@app.command("status")
def set_status(
    paper_id: int = typer.Argument(..., help="Paper ID"),
    new_status: str = typer.Argument(..., help="New status: unread, reading, or done"),
):
    """Update the reading status of a paper."""
    if new_status not in ("unread", "reading", "done"):
        console.print(f"[red]Invalid status '{new_status}'. Use: unread, reading, done[/red]")
        raise typer.Exit(1)
    session = get_session()
    repo = PaperRepository(session)
    repo.update_status(paper_id, new_status)
    console.print(f"[green]Paper #{paper_id} status set to '{new_status}'[/green]")
    session.close()


# ── notes ────────────────────────────────────────────────────

@app.command("notes")
def manage_notes(
    paper_id: int = typer.Argument(..., help="Paper ID"),
    set_text: str = typer.Option(None, "--set", help="Set notes (if omitted, displays current notes)"),
):
    """View or set notes for a paper."""
    session = get_session()
    repo = PaperRepository(session)
    paper = repo.get_paper(paper_id)
    if not paper:
        console.print(f"[red]Paper #{paper_id} not found.[/red]")
        session.close()
        return

    if set_text:
        repo.add_notes(paper_id, set_text)
        console.print(f"[green]Notes updated for paper #{paper_id}[/green]")
    else:
        if paper.notes:
            console.print(f"[bold]Notes for [{paper.id}] {paper.title[:60]}:[/bold]")
            console.print(paper.notes)
        else:
            console.print("[dim]No notes yet. Use --set to add notes.[/dim]")
    session.close()


# ── pdf ──────────────────────────────────────────────────────

@app.command("pdf")
def set_pdf(
    paper_id: int = typer.Argument(..., help="Paper ID"),
    path: str = typer.Argument(..., help="Path to PDF file (relative to project root)"),
):
    """Link a PDF file to a paper."""
    session = get_session()
    repo = PaperRepository(session)
    paper = repo.get_paper(paper_id)
    if not paper:
        console.print(f"[red]Paper #{paper_id} not found.[/red]")
        session.close()
        return

    paper.pdf_path = path
    session.commit()
    console.print(f"[green]PDF linked to paper #{paper_id}: {path}[/green]")
    session.close()


# ── annotate ─────────────────────────────────────────────────

@app.command("annotate")
def annotate(
    paper_id: int = typer.Argument(..., help="Paper ID to annotate"),
):
    """Interactively edit paper notes via $EDITOR."""
    import subprocess
    import tempfile

    editor = os.environ.get("EDITOR", os.environ.get("VISUAL", "notepad" if os.name == "nt" else "vi"))

    session = get_session()
    repo = PaperRepository(session)
    paper = repo.get_paper(paper_id)
    if not paper:
        console.print(f"[red]Paper #{paper_id} not found.[/red]")
        session.close()
        return

    template = f"""# Paper #{paper.id}: {paper.title}
# Authors: {', '.join(a.full_name for a in paper.authors) if paper.authors else 'N/A'}
# Status: {paper.reading_status} (change to: unread | reading | done)
#
# Edit notes below. Lines starting with # are comments and will be removed.
# Save and close the editor when done.

Status: {paper.reading_status}

{paper.notes or ''}
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(template)
        tmp_path = f.name

    try:
        subprocess.call([editor, tmp_path])

        with open(tmp_path, "r", encoding="utf-8") as f:
            content = f.read()

        notes_lines = []
        new_status = paper.reading_status
        for line in content.split("\n"):
            if line.startswith("#"):
                continue
            if line.startswith("Status:"):
                s = line.replace("Status:", "").strip()
                if s in ("unread", "reading", "done"):
                    new_status = s
                continue
            notes_lines.append(line)

        new_notes = "\n".join(notes_lines).strip()
        repo.add_notes(paper_id, new_notes)
        repo.update_status(paper_id, new_status)
        console.print(f"[green]Paper #{paper_id} updated.[/green]")
    finally:
        os.unlink(tmp_path)

    session.close()


# ── dedup ────────────────────────────────────────────────────

@app.command("dedup")
def deduplicate(
    dry_run: bool = typer.Option(False, "--dry-run", help="Show duplicates without merging"),
    threshold: float = typer.Option(0.85, "--threshold", help="Title similarity threshold (0-1)"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Auto-merge without confirmation"),
):
    """Find and merge duplicate papers."""
    session = get_session()
    repo = PaperRepository(session)

    with console.status("[bold]Scanning for duplicates...[/bold]"):
        duplicates = repo.find_all_duplicates(threshold=threshold)

    if not duplicates:
        console.print("[green]No duplicates found.[/green]")
        session.close()
        return

    console.print(f"[bold]Found {len(duplicates)} potential duplicate pair(s):[/bold]\n")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("#", width=4)
    table.add_column("Paper 1", width=40)
    table.add_column("Paper 2", width=40)
    table.add_column("Match", width=15)

    for i, (p1, p2, ratio, method) in enumerate(duplicates, 1):
        table.add_row(
            str(i),
            f"[{p1.id}] {p1.title[:35]}...",
            f"[{p2.id}] {p2.title[:35]}...",
            f"{method} ({ratio:.0%})",
        )
    console.print(table)

    if dry_run:
        console.print("[dim]Dry-run: no changes made. Remove --dry-run to merge.[/dim]")
        session.close()
        return

    if not yes:
        confirm = typer.confirm(f"\nMerge {len(duplicates)} duplicate pairs?")
        if not confirm:
            console.print("[dim]Aborted.[/dim]")
            session.close()
            return

    merged_count = 0
    for p1, p2, _, _ in duplicates:
        try:
            repo.merge_duplicates(p1.id, p2.id)
            merged_count += 1
            console.print(f"  Merged [{p2.id}] into [{p1.id}]: {p1.title[:50]}")
        except Exception as e:
            console.print(f"[red]Failed to merge [{p1.id}] & [{p2.id}]: {e}[/red]")

    console.print(f"\n[green]Merged {merged_count} duplicate pair(s)[/green]")
    session.close()


# ── export ───────────────────────────────────────────────────

@export_app.command("review")
def export_review(
    output: str = typer.Option("output/review.md", "--output", "-o", help="Output file path"),
    tag: str = typer.Option(None, "--tag", "-t", help="Filter by tags (comma-separated)"),
    title: str = typer.Option("Literature Review", "--title", help="Document title"),
    description: str = typer.Option(None, "--description", "-d", help="Review description"),
    status: str = typer.Option(None, "--status", "-s", help="Filter by reading status"),
    no_bibtex: bool = typer.Option(False, "--no-bibtex", help="Exclude BibTeX bibliography"),
):
    """Export a structured markdown literature review."""
    session = get_session()
    repo = PaperRepository(session)
    exporter = ReviewExporter(repo)

    tag_list = [t.strip() for t in tag.split(",")] if tag else None

    with console.status(f"[bold]Generating review...[/bold]"):
        output_path = exporter.export(
            output_path=output,
            title=title,
            description=description,
            tags=tag_list,
            status=status,
            include_bibtex=not no_bibtex,
        )

    console.print(f"[green]Review exported to: {output_path}[/green]")
    session.close()


# ── cache ────────────────────────────────────────────────────

@cache_app.command("stats")
def cache_stats():
    """Show API cache statistics."""
    session = get_session()
    cache_repo = CacheRepository(session)
    st = cache_repo.stats()
    console.print(f"[bold]Cache entries:[/bold] {st['total_entries']}")
    if st["by_endpoint"]:
        console.print("[bold]By endpoint:[/bold]")
        for ep, count in st["by_endpoint"].items():
            console.print(f"  {ep}: {count}")
    session.close()


@cache_app.command("clear")
def cache_clear(
    endpoint: str = typer.Option(None, "--endpoint", help="Clear only this endpoint"),
):
    """Clear the API cache."""
    session = get_session()
    cache_repo = CacheRepository(session)
    count = cache_repo.clear(endpoint=endpoint)
    if endpoint:
        console.print(f"[green]Cleared {count} cache entries for '{endpoint}'[/green]")
    else:
        console.print(f"[green]Cleared all {count} cache entries[/green]")
    session.close()


# ── config ───────────────────────────────────────────────────

@config_app.command("show")
def config_show():
    """Show current configuration."""
    config = cfg.load_config()
    table = Table(title="Configuration")
    table.add_column("Key", style="cyan")
    table.add_column("Value")
    for k, v in config.items():
        display = v if "api_key" not in k.lower() else ("***" + v[-4:] if v else "")
        table.add_row(k, display)
    console.print(table)


@config_app.command("set")
def config_set(
    key: str = typer.Argument(..., help="Config key"),
    value: str = typer.Argument(..., help="Config value"),
):
    """Set a configuration value."""
    cfg.set_(key, value)
    console.print(f"[green]Config '{key}' updated[/green]")


def main():
    app()


if __name__ == "__main__":
    main()
