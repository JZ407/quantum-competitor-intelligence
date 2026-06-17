"""Profile generation utilities — structured research → DB.

The actual web research is done interactively by Claude (WebSearch tool).
This module handles: storing research output, synthesizing from existing DB articles,
and incremental updates.
"""
import json, os, sys, sqlite3
from datetime import datetime
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from competitor_profiles.schema import (
    init_profile_db, upsert_profile, add_source, get_profile
)

# Profile schema as a template — defines all fields we want to fill
PROFILE_TEMPLATE = {
    "company_name": "",           # Official English name
    "name_cn": "",                # Chinese name
    "founded_year": None,         # Year founded
    "hq": "",                     # Headquarters city/country
    "website": "",                # Official website
    "employee_count": None,       # Approximate employee count
    "qubit_modality": "",         # e.g. superconducting, trapped ion, neutral atom, photonic, cat qubit, spin, topological
    "tech_stage": "",             # e.g. R&D, early commercial, commercial
    "business_model": "",         # e.g. hardware + cloud, software-only, full-stack
    "ceo": "",                    # CEO name
    "founders": [],               # [{name, role, background}]
    "key_people": [],             # [{name, role, background, notable_for}]
    "total_funding_usd": None,    # Total funding in USD
    "funding_history": [],        # [{date, round, amount_usd, investors[], note}]
    "valuation_usd": None,        # Latest valuation in USD
    "products": [],               # [{name, type, description, status, launch_date}]
    "partnerships": [],           # [{partner, date, type, description}]
    "tech_milestones": [],        # [{date, description, significance}]
    "swot": {                     # SWOT analysis
        "strengths": [],
        "weaknesses": [],
        "opportunities": [],
        "threats": [],
    },
    "competitive_positioning": "",  # Paragraph on market position vs peers
    "latest_summary": "",           # 2-3 sentence summary of latest developments
    "profile_status": "draft",
}


def load_news_for_company(company_name: str, limit: int = 100) -> list:
    """Load existing news articles for a company from the institutions DB."""
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           'institution_news', 'institutions.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''SELECT title, title_cn, publish_date, summary, summary_cn, url, source
                 FROM articles
                 WHERE source LIKE ? OR source LIKE ?
                 ORDER BY publish_date DESC LIMIT ?''',
              (f'{company_name}%', f'%{company_name}%', limit))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def synthesize_news_summary(company_name: str, client=None) -> str:
    """Generate a chronological summary from existing DB articles.
    Returns a markdown timeline string."""
    articles = load_news_for_company(company_name, limit=50)
    if not articles:
        return f"_No articles found in DB for {company_name}_"

    lines = [f"## {company_name} 新闻时间线\n"]
    for art in articles:
        date = art.get('publish_date', '??') or '??'
        title = art.get('title_cn') or art.get('title', '') or '(无标题)'
        summary = art.get('summary_cn') or art.get('summary', '') or ''
        if summary:
            summary = summary[:200]
        url = art.get('url', '')
        lines.append(f"- **{date}** — {title[:120]}")
        if summary:
            lines.append(f"  > {summary[:150]}")
    return '\n'.join(lines)


def fill_profile_from_research(company_name: str, research_data: dict,
                                sources: list = None) -> int:
    """Store a profile from structured research data.

    Args:
        company_name: e.g. "Algorithmiq"
        research_data: dict with fields matching PROFILE_TEMPLATE
        sources: list of {field_name, source_url, source_title}

    Returns profile_id.
    """
    conn = init_profile_db()

    # Merge with template
    profile = dict(PROFILE_TEMPLATE)
    profile.update(research_data)
    profile['company_name'] = company_name
    profile['last_researched'] = datetime.now().isoformat()
    profile['profile_status'] = research_data.get('profile_status', 'complete')

    pid = upsert_profile(conn, profile)

    # Store sources
    if sources:
        for s in sources:
            add_source(conn, pid, s.get('field_name', ''),
                       s.get('source_url', ''), s.get('source_title', ''))

    conn.close()
    return pid


def mark_outdated(company_name: str) -> bool:
    """Mark a profile as outdated (needs re-research)."""
    conn = init_profile_db()
    c = conn.cursor()
    c.execute('''UPDATE competitor_profiles SET profile_status = 'outdated',
                 updated_at = ? WHERE company_name LIKE ?''',
              (datetime.now().isoformat(), f'%{company_name}%'))
    conn.commit()
    affected = c.rowcount
    conn.close()
    return affected > 0
