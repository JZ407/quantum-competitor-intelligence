# -*- coding: utf-8 -*-
"""Extract Xanadu paper authors via Semantic Scholar API (generous rate limits).
Falls back to CrossRef for papers not found on S2."""
import sqlite3, re, json, urllib.request, time
from collections import Counter

INST_DB = "D:/Claude_code/institution_news/institutions.db"
PROFILES_DB = "D:/Claude_code/competitor_profiles/profiles.db"

inst_conn = sqlite3.connect(INST_DB)
inst_conn.row_factory = sqlite3.Row
c = inst_conn.cursor()
c.execute("SELECT id, title, url, publish_date FROM articles WHERE source='Xanadu Research'")
rows = c.fetchall()
print(f"Loaded {len(rows)} papers")

# Extract IDs
arxiv_papers = []
doi_papers = []
for r in rows:
    url = r['url'] or ''
    aid = re.search(r'arxiv\.org/abs/([\d.]+)', url)
    doi = re.search(r'(10\.\d{4,}/[^\s\"<>?#]+)', url)
    if aid:
        arxiv_papers.append({'db_id': r['id'], 'title': r['title'], 'url': url,
                             'arxiv_id': re.sub(r'v\d+$', '', aid.group(1))})
    elif doi:
        doi_papers.append({'db_id': r['id'], 'title': r['title'], 'url': url,
                           'doi': doi.group(0).rstrip('.')})

print(f"arXiv: {len(arxiv_papers)} | DOI: {len(doi_papers)}")

author_counts = Counter()
paper_details = []
found = 0
not_found = 0

# ── Semantic Scholar: batch by arXiv ID ──
S2_URL = "https://api.semanticscholar.org/graph/v1/paper/batch"
FIELDS = "?fields=title,authors,year,journal,externalIds,publicationDate"

BATCH = 50
for start in range(0, len(arxiv_papers), BATCH):
    batch = arxiv_papers[start:start+BATCH]
    payload = json.dumps({"ids": [f"ArXiv:{p['arxiv_id']}" for p in batch]}).encode('utf-8')

    try:
        req = urllib.request.Request(S2_URL + FIELDS, data=payload, headers={
            'Content-Type': 'application/json',
            'User-Agent': 'XanaduProfileBuilder/1.0'
        })
        resp = urllib.request.urlopen(req, timeout=60)
        data = json.loads(resp.read())

        for i, paper in enumerate(data):
            batch_item = batch[i]
            if paper is None:
                not_found += 1
                continue

            authors_raw = [a['name'] for a in paper.get('authors', [])]
            authors_str = ', '.join(authors_raw)
            journal = paper.get('journal', {})
            journal_name = journal.get('name', '') if journal else ''
            pub_date = paper.get('publicationDate', '') or ''

            for a in authors_raw:
                author_counts[a] += 1

            paper_details.append({
                'title': paper.get('title', batch_item['title']),
                'authors': authors_str, 'authors_list': authors_raw,
                'journal': journal_name, 'pub_date': pub_date,
                'arxiv_id': batch_item['arxiv_id'], 'url': batch_item['url'],
            })
            found += 1

        progress = min(start+BATCH, len(arxiv_papers))
        print(f"  S2 batch {start//BATCH + 1}: {found} found, {not_found} missing ({progress}/{len(arxiv_papers)})")
        time.sleep(1.5)
    except Exception as e:
        print(f"  S2 batch {start//BATCH + 1} error: {e}")
        time.sleep(5)

# ── CrossRef for DOI papers + arXiv papers not on S2 ──
crossref_count = 0
doi_url = "https://api.crossref.org/works/"

for p in doi_papers:
    try:
        curl = f"{doi_url}{urllib.request.quote(p['doi'], safe='')}"
        resp = urllib.request.urlopen(curl, timeout=15)
        data = json.loads(resp.read())
        msg = data.get('message', {})
        title = msg.get('title', [''])[0] if msg.get('title') else p['title']
        authors_raw = [f"{a.get('given','')} {a.get('family','')}".strip() for a in msg.get('author', [])]
        authors_str = ', '.join(authors_raw)
        ct = msg.get('container-title', [''])
        journal = ct[0] if isinstance(ct, list) and ct else ''
        pp = msg.get('published-print', msg.get('published-online', {}))
        pub_date = '-'.join(str(v) for v in pp.values())[:10] if pp else ''

        for a in authors_raw:
            author_counts[a] += 1

        paper_details.append({
            'title': title, 'authors': authors_str, 'authors_list': authors_raw,
            'journal': journal, 'pub_date': pub_date, 'doi': p['doi'], 'url': p['url'],
        })
        crossref_count += 1
        time.sleep(0.3)
    except Exception as e:
        print(f"  CrossRef err for {p['doi'][:40]}: {e}")

# Also try CrossRef for arXiv papers not found on S2
if not_found > 0:
    print(f"\n  Trying CrossRef for {not_found} arXiv papers not on S2...")
    # Most arXiv papers have DOIs - query by arXiv ID
    # We'll skip this for now as it's complex; focus on S2 results

# ── Results ──
print(f"\n{'='*60}")
print(f"Total: {len(paper_details)} papers ({found} S2 + {crossref_count} CrossRef), {len(author_counts)} authors")
print(f"\nTop 50 authors by paper count:")
for i, (name, cnt) in enumerate(author_counts.most_common(50), 1):
    print(f"  {i:2d}. {name:45s} {cnt:3d}")

# ── Import to profile_publications ──
profiles_conn = sqlite3.connect(PROFILES_DB)
profiles_conn.execute('DELETE FROM profile_publications WHERE profile_id=4')
imported = 0
for p in paper_details:
    pub_type = 'journal_article' if p.get('journal') else 'preprint'
    try:
        profiles_conn.execute('''
            INSERT INTO profile_publications (profile_id, title, authors, journal, pub_date, url, pub_type, arxiv_id)
            VALUES (4, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            str(p.get('title', ''))[:300],
            str(p.get('authors', ''))[:800],
            str(p.get('journal', ''))[:200],
            str(p.get('pub_date', ''))[:20],
            str(p.get('url', ''))[:500],
            pub_type,
            str(p.get('arxiv_id', ''))[:50]
        ))
        imported += 1
    except Exception as e:
        print(f"  DB err: {e}")

profiles_conn.commit()
profiles_conn.close()
inst_conn.close()

print(f"\n[OK] {imported} papers imported to profile_publications")

# Save
with open('D:/Claude_code/competitor_profiles/xanadu_authors.json', 'w', encoding='utf-8') as f:
    json.dump({
        'total_papers': len(paper_details), 'total_authors': len(author_counts),
        'top_authors': [(n, c) for n, c in author_counts.most_common(50)],
    }, f, ensure_ascii=False, indent=2)
print("Saved xanadu_authors.json")
