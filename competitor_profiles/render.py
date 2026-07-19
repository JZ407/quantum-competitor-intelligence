"""Profile rendering for Streamlit UI."""
import json
import sqlite3
import os
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'profiles.db')


def render_profile_card(profile: dict) -> str:
    """Render a single competitor profile as an HTML card for Streamlit."""
    name = profile.get('company_name', 'Unknown')
    name_cn = profile.get('name_cn', '')
    display_name = f"{name} ({name_cn})" if name_cn else name

    html = f"""<div style="background:#1e1e2e; border-radius:8px; padding:16px; margin:8px 0; border-left:4px solid #e94560;">
    <h4 style="margin:0 0 8px 0; color:#e94560;">{display_name}</h4>
    <table style="width:100%; font-size:0.85em; color:#ccc;">
    """
    rows = []
    if profile.get('founded_year'):
        rows.append(f'<tr><td style="color:#888; width:80px;">成立</td><td>{profile["founded_year"]}</td></tr>')
    if profile.get('hq'):
        rows.append(f'<tr><td style="color:#888;">总部</td><td>{profile["hq"]}</td></tr>')
    if profile.get('qubit_modality'):
        rows.append(f'<tr><td style="color:#888;">技术路线</td><td>{profile["qubit_modality"]}</td></tr>')
    if profile.get('ceo'):
        rows.append(f'<tr><td style="color:#888;">CEO</td><td>{profile["ceo"]}</td></tr>')
    if profile.get('total_funding_usd'):
        funding = f'${profile["total_funding_usd"]/1e6:.0f}M' if profile['total_funding_usd'] < 1e9 else f'${profile["total_funding_usd"]/1e9:.1f}B'
        rows.append(f'<tr><td style="color:#888;">融资总额</td><td>{funding}</td></tr>')
    if profile.get('valuation_usd'):
        val = f'${profile["valuation_usd"]/1e6:.0f}M' if profile['valuation_usd'] < 1e9 else f'${profile["valuation_usd"]/1e9:.1f}B'
        rows.append(f'<tr><td style="color:#888;">估值</td><td>{val}</td></tr>')
    if profile.get('tech_stage'):
        rows.append(f'<tr><td style="color:#888;">阶段</td><td>{profile["tech_stage"]}</td></tr>')

    html += '\n'.join(rows)
    html += '</table></div>'
    return html


def render_detailed_profile(profile: dict, lang: str = 'zh') -> str:
    """Render a full detailed profile as Markdown. lang='zh' uses Chinese labels/content."""
    name = profile.get('company_name', 'Unknown')
    name_cn = profile.get('name_cn', '')
    display_name = f"{name} ({name_cn})" if name_cn else name

    # Load Chinese translations if available
    cn = {}
    tc = profile.get('translations_cn')
    if tc:
        if isinstance(tc, str):
            try:
                cn = json.loads(tc)
            except (json.JSONDecodeError, TypeError):
                pass

    is_zh = lang == 'zh'
    L = lambda zh, en: zh if is_zh else en

    md = f"# 🏢 {display_name}\n\n"

    # ── Basic Info ──
    md += f"## 📋 {L('基本信息', 'Basic Info')}\n\n"
    md += f"| {L('项目', 'Field')} | {L('内容', 'Value')} |\n|------|------|\n"
    for label_zh, label_en, key in [
        ('成立年份', 'Founded', 'founded_year'),
        ('总部', 'HQ', 'hq'),
        ('网站', 'Website', 'website'),
        ('员工数', 'Employees', 'employee_count'),
        ('CEO', 'CEO', 'ceo'),
        ('商业模式', 'Business Model', 'business_model'),
    ]:
        val = profile.get(key)
        if val:
            if key == 'website' and isinstance(val, str):
                val = f'[{val}]({val})'
            md += f"| {L(label_zh, label_en)} | {val} |\n"

    # ── Technology ──
    md += f"\n## 🔬 {L('技术', 'Technology')}\n\n"
    for label_zh, label_en, key in [
        ('量子比特类型', 'Qubit Modality', 'qubit_modality'),
        ('发展阶段', 'Stage', 'tech_stage'),
    ]:
        val = profile.get(key)
        if val:
            md += f"- **{L(label_zh, label_en)}**: {val}\n"

    # ── Funding ──
    history = profile.get('funding_history')
    total = profile.get('total_funding_usd')
    valn = profile.get('valuation_usd')
    if total or history:
        md += f"\n## 💰 {L('融资', 'Funding')}\n\n"
        if total:
            md += f"**{L('融资总额', 'Total Funding')}**: ${total/1e6:.0f}M\n"
        if valn:
            md += f"**{L('估值', 'Valuation')}**: ${valn/1e6:.0f}M\n"
        if history and isinstance(history, list):
            md += f"\n| {L('日期', 'Date')} | {L('轮次', 'Round')} | {L('金额', 'Amount')} | {L('投资方', 'Investors')} |\n|------|------|------|--------|\n"
            for r in history:
                date = r.get('date', '?')
                rd = r.get('round', '?')
                amt = r.get('amount_usd', '')
                if amt:
                    amt = f'${amt/1e6:.0f}M' if amt < 1e9 else f'${amt/1e9:.1f}B'
                invs = ', '.join(r.get('investors', [])[:4])
                md += f"| {date} | {rd} | {amt} | {invs} |\n"

    # ── Founders (brief) ──
    founders = profile.get('founders')
    if founders:
        if isinstance(founders, str):
            try: founders = json.loads(founders)
            except: founders = []
        if isinstance(founders, list) and founders:
            md += f"\n## 👥 {L('创始人', 'Founders')}\n\n"
            for f in founders:
                if isinstance(f, dict):
                    md += f"- **{f.get('name', '?')}** — {f.get('role', '')} ({f.get('background', '')})\n"

    # ── Products ──
    products = cn.get('products') or profile.get('products')
    if isinstance(products, str):
        try: products = json.loads(products)
        except: products = []
    if products and isinstance(products, list):
        md += f"\n## 🛠️ {L('产品', 'Products')}\n\n"
        for p in products:
            if isinstance(p, dict):
                name = p.get('name', '?')
                ptype = p.get('type', '')
                desc = p.get('description', '')
                status = p.get('status', '')
                md += f"- **{name}** ({ptype}) — {desc} _{status}_\n"

    # ── Partnerships ──
    partnerships = cn.get('partnerships') or profile.get('partnerships')
    if isinstance(partnerships, str):
        try: partnerships = json.loads(partnerships)
        except: partnerships = []
    if partnerships and isinstance(partnerships, list):
        md += f"\n## 🤝 {L('合作伙伴', 'Partnerships')}\n\n"
        for p in partnerships:
            if isinstance(p, dict):
                ptype = p.get('type', '')
                desc = p.get('description', '')
                md += f"- **{p.get('partner', '?')}** ({p.get('date', '?')}/{ptype}): {desc}\n"

    # ── Milestones ──
    milestones = cn.get('tech_milestones') or profile.get('tech_milestones')
    if isinstance(milestones, str):
        try: milestones = json.loads(milestones)
        except: milestones = []
    if milestones and isinstance(milestones, list):
        md += f"\n## 🎯 {L('技术里程碑', 'Milestones')}\n\n"
        for m in milestones:
            if isinstance(m, dict):
                md += f"- **{m.get('date', '?')}**: {m.get('description', '')}\n"

    # ── SWOT ──
    swot = cn.get('swot') or profile.get('swot')
    if isinstance(swot, str):
        try: swot = json.loads(swot)
        except: swot = {}
    if swot and isinstance(swot, dict):
        md += f"\n## 📊 {L('SWOT 分析', 'SWOT Analysis')}\n\n"
        quad_map = [
            ('strengths', '💪', L('优势', 'Strengths')),
            ('weaknesses', '⚠️', L('劣势', 'Weaknesses')),
            ('opportunities', '🌱', L('机会', 'Opportunities')),
            ('threats', '🚧', L('威胁', 'Threats')),
        ]
        for quad, emoji, qlabel in quad_map:
            items = swot.get(quad, [])
            if items:
                md += f"**{emoji} {qlabel}**:\n"
                for item in items:
                    md += f"- {item}\n"
                md += "\n"

    # ── Positioning ──
    pos = profile.get('competitive_positioning')
    if pos:
        md += f"\n## 🎯 {L('竞争定位', 'Competitive Positioning')}\n\n{pos}\n"

    # ── Latest ──
    latest = profile.get('latest_summary')
    if latest:
        md += f"\n## 📡 {L('最新动态', 'Latest')}\n\n{latest}\n"

    # ── Meta ──
    md += f"\n---\n*{L('最后更新', 'Last updated')}: {profile.get('last_researched', '?')}* | *{L('状态', 'Status')}: {profile.get('profile_status', 'draft')}*\n"

    return md


def render_profile_list(profiles: list) -> str:
    """Render a table of all profiles as HTML."""
    if not profiles:
        return '<p style="color:#888;">暂无档案。运行研究生成第一个竞争对手档案。</p>'

    rows = []
    for p in profiles:
        name = p.get('company_name', '?')
        cn = p.get('name_cn', '')
        disp = f"{name} ({cn})" if cn else name
        modality = p.get('qubit_modality', '-')
        funding = ''
        if p.get('total_funding_usd'):
            f = p['total_funding_usd']
            funding = f'${f/1e6:.0f}M' if f < 1e9 else f'${f/1e9:.1f}B'
        status = p.get('profile_status', 'draft')
        status_color = {'complete': '#4caf50', 'draft': '#ff9800', 'outdated': '#f44336'}.get(status, '#888')
        updated = str(p.get('last_researched', '') or p.get('updated_at', ''))[:10]

        rows.append(f"""<tr>
            <td style="padding:8px; border-bottom:1px solid #333;">
                <strong style="color:#e94560;">{disp}</strong>
            </td>
            <td style="padding:8px; border-bottom:1px solid #333;">{modality}</td>
            <td style="padding:8px; border-bottom:1px solid #333;">{funding}</td>
            <td style="padding:8px; border-bottom:1px solid #333;">
                <span style="color:{status_color};">●</span> {status}
            </td>
            <td style="padding:8px; border-bottom:1px solid #333; color:#888;">{updated}</td>
        </tr>""")

    return f"""<table style="width:100%; border-collapse:collapse; color:#ccc;">
    <thead><tr style="text-align:left; border-bottom:2px solid #555; color:#888;">
        <th style="padding:8px;">公司</th>
        <th style="padding:8px;">技术路线</th>
        <th style="padding:8px;">融资</th>
        <th style="padding:8px;">状态</th>
        <th style="padding:8px;">更新</th>
    </tr></thead>
    <tbody>{''.join(rows)}</tbody></table>"""


def render_team_section(key_people: list, team_analytics: dict = None) -> str:
    """Render the team section with L3 deep profiles."""
    if not key_people:
        return '<p>暂无团队数据</p>'

    html = '''<html><head><meta charset="utf-8"><style>
    body { background:#0e1117; color:#e0e0e0; font-family:-apple-system,BlinkMacSystemFont,sans-serif; font-size:14px; padding:16px; margin:0; }
    h2 { color:#e94560; border-bottom:1px solid #333; padding-bottom:8px; }
    h3 { color:#ff6b81; margin-top:20px; }
    details { margin:6px 0; padding:8px 12px; background:#1a1a2e; border-radius:6px; border-left:3px solid #e94560; }
    summary { cursor:pointer; padding:4px 0; font-size:1.02em; }
    summary strong { color:#fff; }
    table { border-collapse:collapse; margin:8px 0; width:100%%; }
    td { padding:4px 12px 4px 0; vertical-align:top; font-size:0.92em; }
    td:first-child { color:#888; white-space:nowrap; font-weight:500; width:70px; }
    a { color:#e94560; text-decoration:none; }
    a:hover { text-decoration:underline; }
    ul { margin:4px 0; padding-left:20px; }
    li { margin:2px 0; font-size:0.9em; color:#bbb; }
    p, .section-label { font-weight:600; color:#999; font-size:0.85em; text-transform:uppercase; letter-spacing:0.5px; margin:10px 0 4px 0; }
    </style></head><body>
    <h2>👥 团队深度分析</h2>
    '''

    # Team analytics overview
    if team_analytics:
        html += '<h3>📊 团队总览</h3><table>'
        html += f'<tr><td>已研究</td><td>{team_analytics.get("total_researched", len(key_people))} 人</td></tr>'
        degrees = team_analytics.get('degree_distribution', {})
        if degrees:
            phd_count = sum(v for k, v in degrees.items() if 'PhD' in k or 'Doctor' in k)
            html += f'<tr><td>博士</td><td>{phd_count} 人</td></tr>'
        h_range = team_analytics.get('h_index_range', [0, 0])
        avg_h = team_analytics.get('avg_h_index', 0)
        if h_range[1] > 0:
            html += f'<tr><td>h-index</td><td>{h_range[0]}–{h_range[1]} (均 {avg_h})</td></tr>'
        institutions = team_analytics.get('top_institutions', {})
        if institutions:
            html += f'<tr><td>学术来源</td><td>{", ".join(list(institutions.keys())[:8])}</td></tr>'
        html += '</table>'

    # Group by role category
    leadership = []
    researchers = []
    engineers = []
    commercial = []
    board = []

    for p in key_people:
        title = (p.get('title', '') or '').lower()
        name = p.get('name', '')
        # Skip duplicates
        if any(name == x.get('name') for x in leadership + researchers + engineers + commercial + board):
            continue
        if any(k in title for k in ['ceo', 'cso', 'cto', 'coo', 'cfo', 'co-founder', 'chief']):
            leadership.append(p)
        elif any(k in title for k in ['engineer', 'developer', 'head of product']):
            engineers.append(p)
        elif any(k in title for k in ['counsel', 'chief of staff', 'country manager', 'operations', 'people', 'it ', 'board']):
            commercial.append(p)
        else:
            researchers.append(p)

    # Render each group as a collapsible section
    groups = [
        ('领导团队', leadership, '🎯'),
        ('研发团队', researchers, '🔬'),
        ('工程团队', engineers, '⚙️'),
        ('商业与运营', commercial, '💼'),
    ]

    for group_name, members, emoji in groups:
        if not members:
            continue
        html += f'<h3>{emoji} {group_name} ({len(members)}人)</h3>'

        for p in members:
            name = p.get('name', '?')
            title = p.get('title', '')
            linkedin = p.get('linkedin', '')
            bg = p.get('academic_background', {}) or {}
            prev_exp = p.get('previous_experience', []) or []
            research = p.get('research_focus', []) or []
            pubs = p.get('publications_highlights', []) or []
            scholar = p.get('google_scholar', '')
            h_idx = p.get('h_index_estimate', '')
            achievements = p.get('notable_achievements', []) or []
            role = p.get('role_at_algorithmiq', '')

            links = []
            if linkedin:
                links.append(f'<a href="{linkedin}" target="_blank">LinkedIn</a>')
            if scholar:
                links.append(f'<a href="{scholar}" target="_blank">Scholar</a>')
            link_str = ' · '.join(links) if links else ''

            html += f'<details><summary><strong>{name}</strong> <span style="color:#888;">— {title}</span></summary>'

            # Info table
            html += '<table>'
            if bg:
                degree = bg.get('highest_degree', '')
                field = bg.get('field', '')
                insts = bg.get('institutions', [])
                year = bg.get('graduation_year', '')
                if degree:
                    html += f'<tr><td>学历</td><td>{degree} · {field} ({year})</td></tr>'
                if insts:
                    html += f'<tr><td>院校</td><td>{", ".join(insts[:4])}</td></tr>'
            if h_idx:
                html += f'<tr><td>h-index</td><td>{h_idx}</td></tr>'
            if link_str:
                html += f'<tr><td>链接</td><td>{link_str}</td></tr>'
            html += '</table>'

            if prev_exp:
                html += '<p class="section-label">经历</p><ul>'
                for exp in prev_exp[:3]:
                    company = exp.get('company', '')
                    role_exp = exp.get('role', '')
                    years = exp.get('years', '')
                    html += f'<li>{company}: {role_exp} ({years})</li>'
                html += '</ul>'

            if research:
                html += f'<p class="section-label">方向</p><p style="color:#bbb;margin:2px 0;">{", ".join(research[:6])}</p>'

            if role:
                html += f'<p class="section-label">角色</p><p style="color:#bbb;margin:2px 0;">{role}</p>'

            if pubs:
                html += '<p class="section-label">代表论文</p><ul>'
                for pub in pubs[:2]:
                    html += f'<li>{pub[:150]}</li>'
                html += '</ul>'

            if achievements:
                html += '<p class="section-label">成就</p><ul>'
                for ach in achievements[:3]:
                    html += f'<li>{ach}</li>'
                html += '</ul>'

            html += '</details>'

    html += '</body></html>'
    return html


def load_publications(profile_id: int, limit: int = 200, themes: list = None, search: str = '') -> list:
    """Load publications for a profile from DB, with optional filters."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    query = 'SELECT * FROM profile_publications WHERE profile_id = ?'
    params = [profile_id]

    if themes:
        theme_clauses = ' OR '.join(['research_themes LIKE ?' for _ in themes])
        query += f' AND ({theme_clauses})'
        params.extend([f'%{t}%' for t in themes])

    if search:
        query += ' AND (title LIKE ? OR authors LIKE ?)'
        params.extend([f'%{search}%', f'%{search}%'])

    query += ' ORDER BY COALESCE(pub_date, "0000") DESC LIMIT ?'
    params.append(limit)

    c.execute(query, params)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def render_research_output(profile: dict) -> str:
    """Render research output section for a profile."""
    analytics = profile.get('research_analytics')
    if isinstance(analytics, str):
        try:
            analytics = json.loads(analytics)
        except (json.JSONDecodeError, TypeError):
            analytics = {}

    if not analytics:
        return ''

    md = '\n## 📄 研究产出\n\n'

    # Quick stats
    total = analytics.get('total_publications', 0)
    journal_n = analytics.get('journal_count', 0)
    arxiv_n = analytics.get('arxiv_count', 0)
    date_range = f"{analytics.get('date_range_start', '?')} ~ {analytics.get('date_range_end', '?')}"
    avg = analytics.get('avg_papers_per_month', 0)

    md += f'**{total}** 篇论文 ({journal_n} 期刊 + {arxiv_n} 预印本) | '
    md += f'覆盖: {date_range} | 月均: {avg} 篇\n\n'

    # Research themes
    themes = analytics.get('research_themes', {})
    if themes:
        md += '### 🔬 研究方向分布\n\n'
        theme_labels = {
            'quantum_algorithms': '量子算法', 'quantum_chemistry': '量子化学',
            'quantum_simulation': '量子模拟', 'quantum_information': '量子信息',
            'error_mitigation': '误差缓解', 'tensor_networks': '张量网络',
            'machine_learning': '机器学习', 'quantum_biology': '量子生物学',
            'error_correction': '纠错与容错', 'neutral_atoms': '中性原子',
            'hardware_platform': '硬件平台',
        }
        max_t = max(themes.values()) if themes else 1
        for theme, count in sorted(themes.items(), key=lambda x: -x[1]):
            label = theme_labels.get(theme, theme)
            bar = '█' * int(count / max_t * 20)
            md += f'- **{label}**: {bar} {count}篇\n'
        md += '\n'

    # Top journals
    journals = analytics.get('top_journals', {})
    if journals:
        md += '### 📰 期刊分布\n\n| 期刊 | 数量 |\n|------|------|\n'
        for j, c in list(journals.items())[:8]:
            md += f'| {j} | {c} |\n'
        md += '\n'

    # Top authors
    authors_with_titles = analytics.get('top_authors_with_titles', {})
    if authors_with_titles:
        md += '### ✍️ 高产作者 (Top 15)\n\n'
        sorted_authors = sorted(authors_with_titles.items(), key=lambda x: -x[1]['papers'])[:15]
        max_a = sorted_authors[0][1]['papers'] if sorted_authors else 1
        for author, info in sorted_authors:
            pct = info['papers'] / max_a
            bar_w = int(pct * 200)
            color = '#e94560' if pct > 0.7 else ('#ff9800' if pct > 0.4 else '#53d8fb')
            title_str = f' — *{info["title"]}*' if info.get('title') else ''
            role_str = f' `{info["role"]}`' if info.get('role') else ''
            md += (
                f'<div style="display:flex;align-items:center;margin:2px 0;font-size:0.92em;">'
                f'<span style="min-width:280px;max-width:320px;text-align:right;padding-right:8px;">'
                f'<strong>{author}</strong>{role_str}</span>'
                f'<span style="width:120px;background:#1a1a2e;border-radius:3px;height:10px;margin:0 8px;">'
                f'<span style="display:block;background:{color};height:100%;width:{int(bar_w*0.6)}px;border-radius:3px;"></span>'
                f'</span>'
                f'<span style="color:#888;width:30px;text-align:right;font-size:0.85em;">{info["papers"]}篇</span>'
                f'</div>\n'
            )
        md += '\n'

    # Monthly trend
    monthly = analytics.get('monthly_trend', {})
    if monthly:
        md += '### 📈 发表趋势\n\n'
        sorted_months = sorted(monthly.keys())
        if sorted_months:
            md += '| 月份 | 数量 | 趋势 |\n|------|------|------|\n'
            for m in sorted_months[-12:]:  # last 12 months
                n = monthly[m]
                bar = '█' * n
                md += f'| {m} | {n} | {bar} |\n'
        md += '\n'

    return md


def render_author_contribution(profile_id: int, top_n: int = 25) -> str:
    """Render author contribution bar chart from profile_publications.
    Color-coded: Xanadu employees (blue), external/advisor (orange), former (gray)."""
    from collections import Counter
    import sqlite3, os

    db = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'profiles.db')
    conn = sqlite3.connect(db)
    rows = conn.execute(
        'SELECT authors FROM profile_publications WHERE profile_id=?', (profile_id,)
    ).fetchall()
    conn.close()

    if not rows:
        return ''

    c = Counter()
    for r in rows:
        for a in (r[0] or '').split(', '):
            a = a.strip()
            if a and len(a) > 2:
                c[a] += 1

    top = c.most_common(top_n)
    max_n = top[0][1] if top else 1

    # Known affiliation mapping (from verification above)
    xanadu_people = {
        'J. Arrazola', 'N. Killoran', 'M. Schuld', 'N. Quesada', 'J. Izaac',
        'T. Bromley', 'S. Jahangiri', 'D. Su', 'Pablo Antonio Moreno Casares',
        'Stepan Fomichev', 'C. Weedbrook', 'H. Qi', 'K. Sabapathy', 'Danial Motlagh',
        'Modjtaba Shokrian Zini', 'K. Br\'adler', 'B. Morrison', 'Z. Vernon',
        'Ignacio Loaiza', 'David Wierichs', 'Alain Delgado', 'A. Delgado',
        'G. Dauphinais', 'M. Menotti', 'Joseph Bowles', 'I. Tzitrin', 'J. Bourassa',
        'Utkarsh Azad', 'M. Vasmer', 'L. Helt', 'K. Tan', 'Kasra Hejazi',
        'R. N. Alexander', 'Robert A. Lang',
    }
    external_people = {
        'P. Rebentrost', 'S. Lloyd', 'Jonathan E. Mueller', 'Arne-Christian Voigt',
        'Nathan Wiebe', 'M. Liscidini',
    }
    former_people = {
        'Ish Dhand', 'O. D. Matteo',
    }
    known_titles = {
        'J. Arrazola': 'Head of Algorithms',
        'N. Killoran': 'Head of Software',
        'C. Weedbrook': 'Founder & CEO',
        'Z. Vernon': 'CTO / Head of Hardware',
        'M. Schuld': 'Quantum ML Lead',
        'N. Quesada': 'Photonic QC Researcher',
        'J. Izaac': 'Strawberry Fields Lead',
        'Ish Dhand': 'Former Head of Architecture',
        'G. Dauphinais': 'Lead Quantum Architecture',
        'M. Vasmer': 'Sr. Quantum Architecture',
        'J. Bourassa': 'Blueprint Lead Author',
        'B. Morrison': '#2 Patent Inventor (Hardware)',
        'S. Lloyd': 'Chief Scientific Advisor (MIT)',
        'O. D. Matteo': 'Former PennyLane Dev → UBC Prof',
        'P. Rebentrost': 'NUS CQT (External)',
    }

    html = '<h3>✍️ 论文贡献 Top 25</h3>'
    html += '<div style="font-size:0.85em;color:#888;margin-bottom:8px;">'
    html += '<span style="color:#53d8fb;">■ Xanadu 现员工</span> '
    html += '<span style="color:#ff9800;">■ 外部合作/顾问</span> '
    html += '<span style="color:#888;">■ 前员工</span></div>'

    for i, (name, cnt) in enumerate(top, 1):
        pct = cnt / max_n
        bar_w = int(pct * 280)

        if name in former_people:
            color = '#888888'
        elif name in external_people:
            color = '#ff9800'
        elif name in xanadu_people:
            color = '#53d8fb'
        else:
            color = '#53d8fb'  # default: assume Xanadu

        title = known_titles.get(name, '')
        title_html = f' <span style="color:#666;font-size:0.8em;">— {title}</span>' if title else ''

        html += (
            f'<div style="display:flex;align-items:center;margin:1px 0;font-size:0.85em;">'
            f'<span style="min-width:30px;text-align:right;color:#666;padding-right:6px;">{i}</span>'
            f'<span style="min-width:260px;max-width:300px;text-align:right;padding-right:8px;'
            f'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">'
            f'<strong>{name}</strong>{title_html}</span>'
            f'<span style="width:160px;background:#1a1a2e;border-radius:3px;height:10px;margin:0 6px;">'
            f'<span style="display:block;background:{color};height:100%;width:{bar_w}px;border-radius:3px;"></span>'
            f'</span>'
            f'<span style="color:#aaa;min-width:35px;text-align:right;font-size:0.85em;">{cnt}</span>'
            f'</div>\n'
        )

    return html


def render_publication_list(profile_id: int, search: str = '', limit: int = 50, themes: list = None) -> str:
    """Render a searchable/filterable publication list."""
    pubs = load_publications(profile_id, limit, themes=themes, search=search)

    if not pubs:
        return '<p style="color:#888;">暂无论文数据</p>'

    # Theme filter buttons (handled in Streamlit, here just render list)
    rows = []
    for pub in pubs:
        title = pub.get('title') or ''
        authors = pub.get('authors') or ''
        pub_type = pub.get('pub_type', '')
        journal = pub.get('journal', '')
        pub_date = pub.get('pub_date', '') or ''
        url = pub.get('url', '')
        themes = pub.get('research_themes', '') or ''
        arxiv_id = pub.get('arxiv_id', '') or ''

        # Badge
        badge_color = '#ff9800' if pub_type == 'preprint' else '#4caf50'
        badge_text = '预印本' if pub_type == 'preprint' else '期刊'

        # Theme badges
        theme_badges = ''
        theme_label_map = {
            'quantum_algorithms': '算法', 'quantum_chemistry': '化学',
            'quantum_simulation': '模拟', 'error_mitigation': '误差缓解',
            'tensor_networks': '张量网络', 'quantum_information': '量子信息',
            'machine_learning': 'ML', 'quantum_biology': '生物'
        }
        if themes:
            for t in themes.split(','):
                label = theme_label_map.get(t, t)
                theme_badges += f'<span style="background:#333; border-radius:3px; padding:1px 6px; margin:0 2px; font-size:0.7em; color:#aaa;">{label}</span>'

        title_display = title[:120] + ('...' if len(title) > 120 else '')
        authors_short = authors[:100] + ('...' if len(authors) > 100 else '')

        rows.append(f"""<tr style="border-bottom:1px solid #2a2a3a;">
            <td style="padding:6px 8px; vertical-align:top;">
                <span style="background:{badge_color}; color:#000; border-radius:3px; padding:1px 6px; font-size:0.7em; font-weight:bold;">{badge_text}</span>
            </td>
            <td style="padding:6px 8px;">
                <a href="{url}" target="_blank" style="color:#e94560; text-decoration:none; font-size:0.9em;">
                    {title_display}
                </a>
                <div style="font-size:0.75em; color:#888; margin-top:2px;">{authors_short}</div>
                <div style="margin-top:2px;">{theme_badges}</div>
            </td>
            <td style="padding:6px 8px; color:#888; font-size:0.8em; white-space:nowrap;">{journal or 'arXiv'}</td>
            <td style="padding:6px 8px; color:#888; font-size:0.8em; white-space:nowrap;">{pub_date}</td>
        </tr>""")

    return f"""<table style="width:100%; border-collapse:collapse; color:#ccc; font-family:monospace;">
    <thead><tr style="text-align:left; border-bottom:2px solid #555; color:#888; font-size:0.85em;">
        <th style="padding:6px 8px; width:50px;">类型</th>
        <th style="padding:6px 8px;">标题 / 作者</th>
        <th style="padding:6px 8px; width:100px;">期刊</th>
        <th style="padding:6px 8px; width:80px;">日期</th>
    </tr></thead>
    <tbody>{''.join(rows)}</tbody></table>"""


def render_cross_analysis(profile: dict) -> str:
    """Render funding x products x publications cross-analysis."""
    import re
    from collections import Counter, defaultdict

    funding = profile.get('funding_history')
    if isinstance(funding, str):
        try: funding = json.loads(funding)
        except: funding = []
    products = profile.get('products')
    if isinstance(products, str):
        try: products = json.loads(products)
        except: products = []

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM profile_publications WHERE profile_id=?', (profile['id'],))
    pubs = [dict(r) for r in c.fetchall()]
    conn.close()

    dated = []
    for p in pubs:
        d = p.get('pub_date') or ''
        m = re.match(r'(\d{4})-(\d{2})', d)
        if m:
            p['_year'] = int(m.group(1))
            p['_month'] = d
            dated.append(p)

    html = '<html><head><meta charset="utf-8"><style>'
    html += 'body{background:#0e1117;color:#e0e0e0;font-family:sans-serif;font-size:14px;padding:16px;margin:0;}'
    html += 'h2{color:#e94560;border-bottom:1px solid #333;padding-bottom:8px;}'
    html += 'h3{color:#ff6b81;margin:16px 0 8px 0;}'
    html += '.finding{background:#1a1a2e;border-left:3px solid #e94560;padding:12px 16px;margin:12px 0;border-radius:0 6px 6px 0;}'
    html += '.finding h4{color:#fff;margin:0 0 6px 0;}'
    html += '.finding p{color:#bbb;margin:2px 0;font-size:0.92em;}'
    html += '.timeline{display:flex;align-items:flex-start;gap:6px;margin:12px 0;flex-wrap:wrap;}'
    html += '.tl-item{background:#1a1a2e;border-radius:6px;padding:10px 14px;text-align:center;min-width:80px;}'
    html += '.tl-item .year{color:#e94560;font-weight:bold;font-size:1.1em;}'
    html += '.tl-item .event{color:#ccc;font-size:0.82em;margin-top:4px;}'
    html += '.tl-item .detail{color:#888;font-size:0.75em;}'
    html += '.bar-row{display:flex;align-items:center;gap:8px;margin:4px 0;}'
    html += '.bar-label{min-width:140px;font-size:0.9em;color:#ccc;text-align:right;}'
    html += '.bar-fill{background:#e94560;height:18px;border-radius:3px;min-width:3px;}'
    html += '.bar-num{font-size:0.8em;color:#888;margin-left:6px;}'
    html += '</style></head><body>'
    html += '<h2>📊 交叉分析：融资 × 产品 × 论文</h2>'

    # Timeline — built dynamically from funding + products
    html += '<h3>📅 关键时间线</h3><div class="timeline">'
    tl_events = []
    for f in (funding or []):
        d = str(f.get('date', ''))[:4]
        r = f.get('round', '') or ''
        amt = f.get('amount_usd', 0) or 0
        if amt >= 1e6: amt_str = f'${amt/1e6:.0f}M'
        elif amt > 0: amt_str = f'${amt/1e3:.0f}K'
        else: amt_str = ''
        tl_events.append((d, r[:10], amt_str))
    for prod in (products or []):
        d = str(prod.get('launch_date', ''))[:4]
        name = prod.get('name', '')[:10]
        if d and d.isdigit():
            tl_events.append((d, name, prod.get('status', '')[:4]))
    tl_events.sort()
    seen = set()
    for d, evt, detail in tl_events:
        key = (d, evt)
        if key in seen: continue
        seen.add(key)
        html += f'<div class="tl-item"><div class="year">{d}</div><div class="event">{evt}</div><div class="detail">{detail}</div></div>'
    html += '</div>'

    # Annual output — data-driven from actual publications
    html += '<h3>📈 年度论文产出</h3>'
    yearly = defaultdict(int)
    for p in dated:
        yearly[p['_year']] += 1
    if yearly:
        max_y = max(yearly.values())
        for y in sorted(yearly):
            n = yearly[y]
            bar_w = max(int(n / max_y * 250), 3)
            html += f'<div class="bar-row"><span class="bar-label">{y}年</span><div class="bar-fill" style="width:{bar_w}px;"></div><span class="bar-num">{n}篇</span></div>'
    else:
        html += '<p style="color:#888;">暂无论文数据</p>'

    # Product-paper theme mapping — use actual product names from profile
    if products and dated:
        html += '<h3>🔗 产品 ↔ 论文主题</h3>'
        # Use research_themes from actual publications for the bar
        theme_counts = Counter()
        for p in dated:
            for t in (p.get('research_themes') or '').split(','):
                t = t.strip()
                if t: theme_counts[t] += 1
        if theme_counts:
            max_t = max(theme_counts.values())
            theme_labels = {
                'neutral_atoms': '中性原子硬件', 'quantum_simulation': '量子模拟',
                'quantum_algorithms': '量子算法', 'error_correction': '纠错与容错',
                'hardware_platform': '硬件平台', 'quantum_information': '量子信息',
                'quantum_chemistry': '量子化学', 'error_mitigation': '误差缓解',
                'tensor_networks': '张量网络', 'machine_learning': '机器学习',
                'quantum_biology': '量子生物学',
            }
            for theme, cnt in theme_counts.most_common(8):
                label = theme_labels.get(theme, theme)
                bar_w = max(int(cnt / max_t * 250), 3)
                html += f'<div class="bar-row"><span class="bar-label">{label}</span><div class="bar-fill" style="width:{bar_w}px;"></div><span class="bar-num">{cnt}篇</span></div>'

    # Findings — read from profile's cross_analysis field
    html += '<h3>💡 关键发现</h3>'
    ca = profile.get('cross_analysis')
    if isinstance(ca, str):
        try: ca = json.loads(ca)
        except: ca = None
    if ca and isinstance(ca, dict):
        for item in ca.get('findings', []):
            html += f'<div class="finding"><h4>{item.get("title","")}</h4><p>{item.get("desc","")}</p></div>'
    else:
        html += '<p style="color:#888;">暂无分析数据</p>'

    html += '</body></html>'
    return html
