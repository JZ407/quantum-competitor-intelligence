import sqlite3, json, os
from collections import Counter

conn = sqlite3.connect("profiles.db")
conn.row_factory = sqlite3.Row
profile = dict(conn.execute("SELECT * FROM competitor_profiles WHERE id=2").fetchone())
output_dir = "QuEra"

lines = []
def w(text=""): lines.append(text)

w("# QuEra Computing 竞争对手档案导出")
w(f"导出日期: 2026-06-26")
w()

# 1. Overview
w("## 公司概况")
w(f"- 公司名: {profile['company_name']}")
w(f"- 中文名: {profile['name_cn']}")
w(f"- 成立: {profile['founded_year']}")
w(f"- 总部: {profile['hq']}")
w(f"- 网站: {profile['website']}")
w(f"- 员工: ~{profile['employee_count']}人")
w(f"- 技术路线: {profile['qubit_modality']}")
w(f"- 发展阶段: {profile['tech_stage']}")
w(f"- 商业模式: {profile['business_model']}")
w(f"- CEO: {profile['ceo']}")
w(f"- 融资总额: ${profile['total_funding_usd']/1e6:.0f}M")
if profile.get('valuation_usd'): w(f"- 估值: ${profile['valuation_usd']/1e9:.1f}B")
w(f"- 状态: {profile['profile_status']}")
w(f"- 最后更新: {profile['last_researched']}")
w()

# 2. Funding
fh = json.loads(profile['funding_history']) if isinstance(profile['funding_history'], str) else (profile['funding_history'] or [])
w(f"## 融资历程 ({len(fh)}轮)")
for f in fh:
    amt = f.get('amount_usd', 0) or 0
    amt_str = f"${amt/1e6:.0f}M" if amt >= 1e6 else f"${amt/1e3:.0f}K"
    invs = ", ".join(f.get('investors', []))
    w(f"- {f.get('date','?')} | {f.get('round','?')} | {amt_str} | {invs}")
    if f.get('note'): w(f"  > {f['note']}")
w()

# 3. Products
prods = json.loads(profile['products']) if isinstance(profile['products'], str) else (profile['products'] or [])
w(f"## 产品 ({len(prods)}款)")
for p in prods:
    w(f"- **{p.get('name','?')}** ({p.get('type','?')}, {p.get('status','?')})")
    w(f"  {p.get('description','')}")
    if p.get('launch_date'): w(f"  发布: {p['launch_date']}")
w()

# 4. Partnerships
parts = json.loads(profile['partnerships']) if isinstance(profile['partnerships'], str) else (profile['partnerships'] or [])
w(f"## 合作伙伴 ({len(parts)}家)")
by_type = {}
for p in parts:
    t = p.get('type', '其他')
    by_type.setdefault(t, []).append(p)
for t in sorted(by_type):
    w(f"### {t}")
    for p in by_type[t]:
        w(f"- **{p.get('partner','?')}** ({p.get('date','?')}): {p.get('description','')}")
w()

# 5. Team
kp = json.loads(profile['key_people']) if isinstance(profile['key_people'], str) else (profile['key_people'] or [])
w(f"## 团队 ({len(kp)}人)")
for p in kp:
    name = p.get('name', '?')
    title = p.get('title', '')
    bg = p.get('academic_background', {}) or {}
    edu = (bg.get('highest_degree','') + ' ' + bg.get('field','')).strip()
    insts = ', '.join(bg.get('institutions', [])[:3])
    h = p.get('h_index_estimate', '')
    achievements = p.get('notable_achievements', [])
    prev = p.get('previous_experience', [])
    research = p.get('research_focus', [])
    pubs_high = p.get('publications_highlights', [])

    w(f"### {name} — {title}")
    if edu: w(f"- 学历: {edu}")
    if insts: w(f"- 院校: {insts}")
    if h: w(f"- h-index: {h}")
    if p.get('linkedin'): w(f"- LinkedIn: {p['linkedin']}")
    if p.get('google_scholar'): w(f"- Google Scholar: {p['google_scholar']}")
    if research: w(f"- 研究方向: {', '.join(research)}")
    if prev:
        w("- 经历:")
        for exp in prev:
            w(f"  - {exp.get('company','')} | {exp.get('role','')} | {exp.get('period','')}")
    if pubs_high:
        w("- 代表论文:")
        for pub in pubs_high: w(f"  - {pub}")
    if achievements:
        w("- 成就:")
        for a in achievements: w(f"  - {a}")
    w()

# 6. Publications
pubs = conn.execute("SELECT title, authors, journal, pub_date, pub_type, url, research_themes FROM profile_publications WHERE profile_id=2 ORDER BY pub_date DESC").fetchall()
w(f"## 论文 ({len(pubs)}篇)")
by_year = Counter(p['pub_date'][:4] for p in pubs if p['pub_date'])
for y in sorted(by_year, reverse=True):
    w(f"### {y}年 ({by_year[y]}篇)")
    for p in pubs:
        if p['pub_date'] and p['pub_date'][:4] == y:
            authors_short = (p['authors'] or '')[:100]
            themes = p['research_themes'] or ''
            w(f"- [{p['pub_type'] or '?'}] {p['pub_date']} | {p['journal'] or '?'} | {p['title'][:120]}")
            if authors_short: w(f"  Authors: {authors_short}")
            if themes: w(f"  Themes: {themes}")
w()

# 7. Sources
sources = conn.execute("SELECT * FROM profile_sources WHERE profile_id=2").fetchall()
w(f"## 信息来源 ({len(sources)}条)")
for s in sources:
    w(f"- [{s['field_name']}] {s['source_title'] or s['source_url']}")
    if s['source_url']: w(f"  {s['source_url']}")
w()

# 8. SWOT
swot_data = json.loads(profile['swot']) if isinstance(profile['swot'], str) else (profile['swot'] or {})
if swot_data:
    w("## SWOT 分析")
    for cat, label in [('strengths','优势'), ('weaknesses','劣势'), ('opportunities','机会'), ('threats','威胁')]:
        items = swot_data.get(cat, [])
        w(f"### {label} ({len(items)}项)")
        for i in items: w(f"- {i}")
        w()

# 9. Research Analytics
ra = json.loads(profile['research_analytics']) if isinstance(profile['research_analytics'], str) else (profile['research_analytics'] or {})
if ra:
    w("## 研究产出分析")
    w(f"- 论文总数: {ra.get('total_publications',0)}")
    w(f"- 期刊: {ra.get('journal_count',0)} | 预印本: {ra.get('arxiv_count',0)}")
    w(f"- 时间跨度: {ra.get('date_range_start','?')} ~ {ra.get('date_range_end','?')}")
    w(f"- 月均: {ra.get('avg_papers_per_month',0)}篇")
    if ra.get('research_themes'):
        w(f"- 研究方向: {json.dumps(ra['research_themes'], ensure_ascii=False)}")
    if ra.get('top_authors_with_titles'):
        w("- 高产作者:")
        for author, info in sorted(ra['top_authors_with_titles'].items(), key=lambda x: -x[1]['papers'])[:15]:
            role = info.get('role', '')
            role_str = f" ({role})" if role else ""
            w(f"  - {author}{role_str}: {info['papers']}篇")
w()

# 10. Cross Analysis
ca = json.loads(profile['cross_analysis']) if isinstance(profile['cross_analysis'], str) else (profile.get('cross_analysis') or {})
if ca and ca.get('findings'):
    w("## 交叉分析：融资 × 产品 × 论文")
    for f in ca['findings']:
        w(f"- **{f['title']}**: {f['desc']}")
w()

filepath = os.path.join(output_dir, "quera_profile_export.md")
with open(filepath, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
conn.close()

print(f"Exported: {filepath}")
print(f"Size: {os.path.getsize(filepath)/1024:.0f} KB")
