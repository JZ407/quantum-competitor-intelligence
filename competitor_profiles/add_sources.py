# -*- coding: utf-8 -*-
"""Add profile_sources for Xanadu (4) and PsiQuantum (3)."""
import sqlite3

conn = sqlite3.connect("profiles.db")

# ====== Xanadu Sources (profile_id=4) ======
xanadu_sources = [
    ("company_info", "https://www.xanadu.ai", "Xanadu Official Website"),
    ("company_info", "https://www.xanadu.ai/about", "Xanadu About Page"),
    ("company_info", "https://en.wikipedia.org/wiki/Xanadu_Quantum_Technologies", "Wikipedia: Xanadu Quantum Technologies"),
    ("company_info", "https://www.marsdd.com/our-story/computing-at-the-speed-of-light/", "MaRS DD: Xanadu Founding Story"),
    ("company_info", "https://finance.yahoo.com/quote/XNDU/profile/", "Yahoo Finance: XNDU Profile"),
    ("company_info", "https://www.sec.gov/Archives/edgar/data/2054174/000121390026028375/ea0281913-425_xanadu.htm", "SEC Filing: Xanadu Business Combination"),

    # Funding
    ("funding", "https://betakit.com/xanadu-closes-100-million-usd-series-c-as-quantum-computing-firm-becomes-canadas-latest-unicorn/", "BetaKit: Xanadu Series C $100M"),
    ("funding", "https://betakit.com/xanadu-secures-120-million-cad-led-by-bessemer-to-build-photonic-quantum-computer/", "BetaKit: Xanadu Series B $100M"),
    ("funding", "https://ca.finance.yahoo.com/news/quantum-computing-startup-xanadu-public-173225479.html", "Yahoo Finance: Xanadu SPAC $3.6B"),
    ("funding", "https://www.cnbc.com/2025/11/03/xanadu-to-list-on-nasdaq-3point6-billion-spac-deal.html", "CNBC: Xanadu SPAC Deal"),
    ("funding", "https://quantumcomputingreport.com/xanadu-announces-q1-2026-financial-results/", "QCR: Xanadu Q1 2026 Results"),
    ("funding", "https://parsers.vc/startup/xanadu.ai/", "Parsers.vc: Xanadu Funding Rounds"),
    ("funding", "https://www.nasdaq.com/press-release/xanadu-receive-23m-new-canadian-quantum-champions-program-2025-12-15", "Nasdaq: CQCP $23M"),
    ("funding", "https://www.globenewswire.com/de/news-release/2026/04/09/3271451/0/en/Xanadu-Announces-Fourth-Quarter-and-Full-Year-2025-Results.html", "GlobeNewsWire: Xanadu FY2025 Results"),
    ("funding", "https://www.sec.gov/Archives/edgar/data/2097162/000121390026019023/ea026630705ex10-17_xanadu.htm", "SEC Filing: SIF $40M CAD Contribution"),
    ("funding", "https://www.newswire.ca/news-releases/government-of-canada-supports-xanadu-to-accelerate-quantum-computing-research-and-education-831327558.html", "Newswire: FedDev Ontario $3.75M"),
    ("funding", "https://thequantuminsider.com/2025/12/15/xanadu-23m-quantum-champions-canada/", "TQI: CQCP $23M Funding"),

    # Team
    ("team", "https://www.globenewswire.com/de/news-release/2026/01/12/3216817/0/en/Xanadu-Strengthens-Executive-Leadership-with-Appointment-of-Chief-Financial-Officer-and-Chief-Legal-Officer.html", "GlobeNewsWire: CFO/CLO Appointments"),
    ("team", "https://theorg.com/org/xanadu/org-chart/juan-miguel-arrazola", "TheOrg: Arrazola Profile"),
    ("team", "https://theorg.com/org/xanadu/org-chart/nathan-killoran", "TheOrg: Killoran Profile"),
    ("team", "https://www.optica-opn.org/home/career/2023/april/senior_member_insights_nicolas_quesada", "Optica: Quesada Profile"),
    ("team", "https://iza.ac/about", "Josh Izaac Personal Site"),
    ("team", "https://mikevasmer.github.io/", "Michael Vasmer Personal Site"),
    ("team", "https://nquesada.github.io/", "Nicolas Quesada Personal Site"),
    ("team", "https://uwaterloo.ca/institute-for-quantum-computing/events/iqc-alum-lecture-series-juan-miguel-arrazola", "IQC Waterloo: Arrazola Alum Lecture"),
    ("team", "https://www.sec.gov/Archives/edgar/data/2054174/000121390026025678/ea0280768-425_xanadu.htm", "SEC Filing: Xanadu Board of Directors"),
    ("team", "https://255.quebecconference.org/en/speaker/zachary-vernon", "Photonics North 2025: Zachary Vernon Profile"),
    ("team", "https://physics.aps.org/authors/maria_schuld", "APS Physics: Maria Schuld Profile"),
    ("team", "https://quantumfoundry.ucsb.edu/people/alumni/kasra-hejazi-xanadu-quantum", "UCSB Quantum Foundry: Kasra Hejazi Profile"),
    ("team", "https://goodip.io/iq/assignee/xanadu-quantum-tech-inc", "GoodIP: Xanadu Patent Inventors"),
    ("team", "https://www.polyu.edu.hk/eee/people/academic-staff-and-teaching-staff/prof-su-daiqin/", "PolyU: Daiqin Su Profile"),
    ("team", "https://theorg.com/org/xanadu/org-chart/pablo-antonio-moreno-casares", "TheOrg: Moreno Casares Profile"),
    ("team", "https://web.cs.toronto.edu/news-events/events/mscac-talks-nathan-killoran-full-stack-photonic-quantum-computing-at-xanadu", "UofT CS: Killoran Talk"),
    ("team", "https://www.cnls.lanl.gov/external/showtalksummary.php?selection=9025", "LANL CNLS: Josh Izaac Talk"),
    ("team", "https://www.datanyze.com/companies/xanadu/347307417", "Datanyze: Xanadu Employee List"),

    # Papers
    ("papers", "https://api.semanticscholar.org/graph/v1/paper/batch", "Semantic Scholar API: Xanadu paper batch query (148 papers)"),
    ("papers", "https://api.crossref.org/", "CrossRef API: Xanadu paper lookup (5 papers)"),
    ("papers", "https://www.nature.com/articles/s41586-022-04725-x", "Nature 2022: Borealis quantum advantage"),
    ("papers", "https://www.nature.com/articles/s41586-024-08406-9", "Nature 2025: Aurora modular photonic QC"),
    ("papers", "https://arxiv.org/abs/2605.20334", "arXiv: QROM halving (Motlagh et al. 2026)"),
    ("papers", "https://quantum-journal.org/papers/q-2021-02-04-392/", "Quantum 2021: Blueprint for Scalable Photonic FTQC"),

    # Products
    ("products", "https://www.xanadu.ai/press", "Xanadu Press Releases"),
    ("products", "https://pennylane.ai/", "PennyLane Official Site"),
    ("products", "https://www.xanadu.cloud/", "Xanadu Cloud"),

    # Partnerships
    ("partnerships", "https://quantumcomputingreport.com/xanadu-and-thorlabs-partner-to-scale-optical-components-for-photonic-quantum-computing/", "QCR: Thorlabs Partnership"),
    ("partnerships", "https://www.photonics.com/Articles/Xanadu-Details-Partnerships-Progress-as-Company/p5/a72007", "Photonics.com: Xanadu Partnerships"),
    ("partnerships", "https://www.nasdaq.com/press-release/xanadu-expected-become-first-and-only-publicly-traded-pure-play-photonic-quantum", "Nasdaq: SPAC Announcement"),

    # SWOT / Analysis
    ("swot", "https://www.nasdaq.com/articles/xanadu-quantum-vs-ionq-better-quantum-computing-stock-buy-2026", "Nasdaq: Xanadu vs IonQ Analysis"),
    ("swot", "https://www.ainvest.com/news/xanadu-ionq-xndu-700x-hype-2026-2606/", "AInvest: Xanadu Valuation Analysis"),
    ("swot", "https://www.tipranks.com/news/can-xanadus-xndu-borealis-quantum-breakthrough-become-a-real-revenue-driver", "TipRanks: Xanadu Revenue Analysis"),
    ("swot", "https://finance.yahoo.com/sectors/technology/articles/xanadu-rare-public-debut-full-151506467.html", "Yahoo Finance: Xanadu Initiation Report"),

    # News
    ("news", "https://www.xanadu.ai/press", "Xanadu Press Room (111 articles scraped)"),
    ("news", "https://www.xanadu.ai/blog", "Xanadu Blog (37 articles scraped)"),
    ("news", "https://www.xanadu.ai/research", "Xanadu Research (153 articles scraped)"),
    ("news", "https://www.theglobeandmail.com/business/article-xanadu-quantum-technologies-public-tsx-nasdaq-spac-crane-harbor/", "Globe and Mail: Xanadu SPAC Profile"),
    ("news", "https://magazine.utoronto.ca/research-ideas/technology/as-quantum-computing-moves-from-theory-to-market-the-race-for-supremacy-heats-up-xanadu/", "UofT Magazine: Xanadu Profile"),
]

# ====== PsiQuantum Sources (profile_id=3) ======
psiquantum_sources = [
    ("company_info", "https://www.psiquantum.com", "PsiQuantum Official Website"),
    ("company_info", "https://www.psiquantum.com/about", "PsiQuantum About Page"),
    ("company_info", "https://en.wikipedia.org/wiki/PsiQuantum", "Wikipedia: PsiQuantum"),
    ("company_info", "C:/Users/zhouj/Desktop/Psiquantum.docx", "User Report: PsiQuantum Engineering Assessment (desktop)"),

    ("funding", "https://www.reuters.com/technology/psiquantum-raises-750-million-series-d-2025-03/", "Reuters: PsiQuantum $750M Series D"),
    ("funding", "https://techcrunch.com/2024/04/29/psiquantum-australia-940m/", "TechCrunch: PsiQuantum Australia A$940M"),
    ("funding", "https://www.reuters.com/technology/psiquantum-raises-1-billion-2025-09/", "Reuters: PsiQuantum $1B Series E"),
    ("funding", "https://www.bloomberg.com/news/articles/2026-05/psiquantum-raises-1-5-billion-at-10-5-billion-valuation", "Bloomberg: PsiQuantum $1.5B Strategic Round"),
    ("funding", "https://www.cnbc.com/2025/03/27/psiquantum-raises-750-million.html", "CNBC: PsiQuantum $750M"),

    ("team", "https://www.psiquantum.com/team", "PsiQuantum Team Page"),
    ("team", "https://www.linkedin.com/company/psiquantum/", "LinkedIn: PsiQuantum Company Page"),
    ("team", "https://scholar.google.com/", "Google Scholar: PsiQuantum Author Search"),
    ("team", "https://www.linkedin.com/in/victor-peng/", "LinkedIn: Victor Peng Profile"),
    ("team", "https://www.linkedin.com/in/jeremy-o-brien/", "LinkedIn: Jeremy O'Brien Profile"),
    ("team", "https://www.linkedin.com/in/pete-shadbolt/", "LinkedIn: Pete Shadbolt Profile"),
    ("team", "https://www.linkedin.com/in/terry-rudolph/", "LinkedIn: Terry Rudolph Profile"),

    ("papers", "https://www.psiquantum.com/research", "PsiQuantum Research Page (38 items scraped)"),
    ("papers", "https://api.semanticscholar.org/", "Semantic Scholar API: PsiQuantum paper search"),
    ("papers", "https://api.crossref.org/", "CrossRef API: PsiQuantum paper lookup"),
    ("papers", "https://export.arxiv.org/api/", "arXiv API: PsiQuantum paper batch query"),
    ("papers", "https://www.nature.com/articles/s41586-025-08714-8", "Nature 2025: Omega Chipset"),
    ("papers", "https://www.nature.com/articles/s41586-022-04725-x", "Nature 2022: Borealis (Xanadu, not PsiQuantum)"),

    ("products", "https://www.psiquantum.com/technology", "PsiQuantum Technology Page"),
    ("products", "https://www.psiquantum.com/construct", "PsiQuantum Construct Platform"),

    ("partnerships", "https://www.psiquantum.com/news", "PsiQuantum News & Press"),
    ("partnerships", "https://www.globalfoundries.com/", "GlobalFoundries: Omega Chip Manufacturing"),
    ("partnerships", "https://www.darpa.mil/", "DARPA QBI: PsiQuantum Participation"),

    ("swot", "https://quantumzeitgeist.com/top-photonic-quantum-computing-companies/", "Quantum Zeitgeist: Top Photonic QC Companies"),
    ("swot", "https://www.ainvest.com/news/xndu-ionq-infq-quantum-ipo-wave-fails-garp-test-2605/", "AInvest: Quantum IPO Analysis"),

    ("news", "https://www.psiquantum.com/news", "PsiQuantum News Room"),
    ("news", "https://www.psiquantum.com/research", "PsiQuantum Research (38 items)"),
    ("news", "C:/Users/zhouj/Desktop/专题简报2026年第9期（总第34期）——PsiQuantum澳大利亚工厂正式破土动工专题分析.docx", "User Report: PsiQuantum Brisbane Factory Briefing"),
]

# Insert Xanadu
for field, url, title in xanadu_sources:
    try:
        conn.execute("INSERT INTO profile_sources (profile_id, field_name, source_url, source_title) VALUES (4, ?, ?, ?)",
                     (field, url, title))
    except Exception as e:
        print(f"  Xanadu skip: {e}")

# Insert PsiQuantum
for field, url, title in psiquantum_sources:
    try:
        conn.execute("INSERT INTO profile_sources (profile_id, field_name, source_url, source_title) VALUES (3, ?, ?, ?)",
                     (field, url, title))
    except Exception as e:
        print(f"  PsiQ skip: {e}")

conn.commit()

for pid in [3, 4]:
    cnt = conn.execute("SELECT COUNT(*) FROM profile_sources WHERE profile_id=?", (pid,)).fetchone()[0]
    name = conn.execute("SELECT company_name FROM competitor_profiles WHERE id=?", (pid,)).fetchone()[0]
    print(f"[OK] {name} (id={pid}): {cnt} sources")

conn.close()
