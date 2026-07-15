# -*- coding: utf-8 -*-
"""Cross-analysis for Xanadu vs peers."""
import json, sqlite3

conn = sqlite3.connect("profiles.db")

# Get all profiles for comparison
profiles = {}
for row in conn.execute("SELECT id, company_name, total_funding_usd, valuation_usd, employee_count FROM competitor_profiles"):
    profiles[row[0]] = {
        'name': row[1], 'funding': row[2] or 0, 'valuation': row[3] or 0,
        'employees': row[4] or 0
    }

xanadu = profiles.get(4, {})
psiquantum = profiles.get(3, {})

findings = [
    {
        "title": "Photonics Dual-Track: CV vs DV - Two Different Scaling Paths",
        "desc": (
            "Xanadu and PsiQuantum both focus on photonic quantum computing but pursue completely "
            "different technical approaches. Xanadu uses continuous-variable (CV) photonics + time-domain "
            "multiplexing + GKP encoding for error correction, demonstrating 12 logical qubits "
            "(Nature 2025). PsiQuantum uses discrete-variable (DV) silicon photonics + semiconductor "
            "fab manufacturing, demonstrating the Omega chipset (Nature 2025). "
            "The fundamental difference: Xanadu's photons are squeezed states - quantum information "
            "encoded in continuous amplitude/phase of light; PsiQuantum's photons are single photons - "
            "quantum information encoded in discrete presence/absence states. "
            "CV offers theoretical advantages in error correction overhead (up to 10x more efficient "
            "with GKP encoding), but experimental realization is more complex. DV benefits from "
            "standardized fab manufacturing, but single-photon source/detector efficiency remains a bottleneck."
        ),
    },
    {
        "title": "PennyLane: Xanadu's Real Moat - But Monetization Path Unclear",
        "desc": (
            "PennyLane's 47% quantum developer share (35,000+ active users, 200K monthly downloads, "
            "150+ university partners) is the closest thing to a de facto standard in quantum computing. "
            "Compare: IBM Qiskit ~35%, Google Cirq ~10%, Amazon Braket SDK ~5%. "
            "But the key question: how do you monetize a quantum developer ecosystem? The history of "
            "open-source SDK monetization (Red Hat $34B acquisition by IBM in 2019 with ~$5B revenue) "
            "shows that even industry-standard open-source software takes 10+ years to monetize meaningfully. "
            "Xanadu's FY2025 $4.6M revenue includes minimal software contribution - primarily DARPA "
            "and ARPA-E government contracts. If PennyLane were valued independently, referencing "
            "GitLab ($10B, 30M users), but with only ~100K quantum developers globally, the implied "
            "$1.5B+ software valuation embedded in Xanadu's $3.1B market cap means each quantum "
            "developer is valued at ~$15,000 regardless of willingness to pay."
        ),
    },
    {
        "title": "Founder Structure: Solo Founder vs Founding Teams",
        "desc": (
            "Xanadu is the only top-tier quantum computing company founded by a single individual. "
            "Christian Weedbrook founded Xanadu alone, with a theoretical physics background and no "
            "co-founders. Compare: PsiQuantum has 4 complementary co-founders (Jeremy O'Brien - "
            "experimental photonics + Bristol school, Terry Rudolph - theory + FBQC architecture, "
            "Pete Shadbolt - engineering + photonic processors, Mark Thompson - industry + integrated "
            "photonics). IonQ was co-founded by Chris Monroe (trapped-ion experimental master) and "
            "Jungsang Kim (engineering expert). Quantinuum emerged from Honeywell Quantum Solutions "
            "(30+ years of industrial R&D). In a field that requires physics + engineering + business "
            "compound expertise, being a solo founder increases CEO decision-making burden and "
            "single-point-of-failure risk. Weedbrook admitted at 2026 Analyst Day: 'I didn't even "
            "know how to do payroll at the beginning.'"
        ),
    },
    {
        "title": "IPO Timing as Double-Edged Sword: First-Mover Advantage vs Valuation Fragility",
        "desc": (
            "Xanadu became the world's first publicly traded pure-play photonic quantum company in "
            "March 2026, pre-empting PsiQuantum's expected IPO. This first-mover advantage has "
            "strategic value in brand visibility and financing window access. But the cost: as a "
            "public company, Xanadu faces relentless quarterly scrutiny - and its Q1 2026 numbers "
            "($2.83M revenue, $20.6M net loss) are difficult to justify to any rational public-market "
            "investor. PsiQuantum, staying private, can continue raising capital on long-term vision "
            "without quarterly performance pressure. September 2026 brings the lock-up expiry of "
            "250M+ legacy shares - if no major commercialization milestone materializes by then, "
            "Xanadu faces potential mass selling and value destruction."
        ),
    },
    {
        "title": "Quantum Data Center vs Quantum Computer Factory: A Paradigm Divide",
        "desc": (
            "Xanadu's 2029-2030 quantum data center vision (500 logical qubits, ~$1B Toronto "
            "facility) and PsiQuantum's quantum computer factory vision (Brisbane, Chicago) "
            "represent fundamentally different things. Xanadu's architecture is inherently "
            "data-center-style - networked server racks connected by optical fiber, modular "
            "expansion, similar to traditional cloud data center topology. PsiQuantum's architecture "
            "is factory-style - monolithic chips manufactured in semiconductor fabs, similar to "
            "traditional chip manufacturing. If the correct photonic scaling path is networking "
            "(the core thesis of the Aurora Nature 2025 paper), Xanadu may have an architectural "
            "advantage. If the correct path is chip-level integration, PsiQuantum's GlobalFoundries "
            "fab relationship is a stronger barrier."
        ),
    },
    {
        "title": "$3.1B vs $10.5B Valuation: Software Ecosystem Premium vs Hardware Manufacturing Premium",
        "desc": (
            "Xanadu's $3.1B public listing valuation (March 2026) compares to PsiQuantum's $10.5B "
            "private valuation (May 2026). The apparent 3.4x gap masks a more interesting story: "
            "Xanadu's $0.55B cumulative funding is only 12% of PsiQuantum's $4.7B. The valuation "
            "divergence reflects fundamentally different bets. PsiQuantum's valuation reflects "
            "hardware manufacturing costs (GlobalFoundries fab partnership, Brisbane factory "
            "construction) and government commitment scale (A$940M Australia) - a fixed-asset "
            "premium. Xanadu's valuation reflects software ecosystem value (PennyLane 47% developer "
            "share) - a network-effect premium. Neither logic can be validated by traditional "
            "valuation models at quantum computing's current stage: one company with no commercial "
            "revenue and another with $12K revenue per employee both commanding multi-billion-dollar "
            "valuations."
        ),
    },
]

ca = {"findings": findings}
conn.execute("UPDATE competitor_profiles SET cross_analysis=? WHERE id=4",
             (json.dumps(ca, ensure_ascii=False),))
conn.commit()

# Import key papers from institution_news
inst_conn = sqlite3.connect("../institution_news/institutions.db")
inst_conn.row_factory = sqlite3.Row
inst_c = inst_conn.cursor()

imported = 0
key_urls = [
    ("nature.com/articles/s41586-022-04725-x", "Nature", "journal_article"),
    ("nature.com/articles/s41586-024-08406-9", "Nature", "journal_article"),
    ("arxiv.org/abs/2605.20334", "", "preprint"),
    ("arxiv.org/abs/2602.20270", "", "preprint"),
]

for url_frag, journal, pub_type in key_urls:
    inst_c.execute(
        "SELECT title, url, publish_date FROM articles WHERE url LIKE ? AND source='Xanadu Research' LIMIT 1",
        (f"%{url_frag}%",)
    )
    row = inst_c.fetchone()
    if row:
        try:
            conn.execute(
                "INSERT INTO profile_publications (profile_id, title, authors, journal, pub_date, url, pub_type) VALUES (4, ?, 'Xanadu et al.', ?, ?, ?, ?)",
                (row["title"][:300], journal, row["publish_date"] or "", row["url"], pub_type)
            )
            imported += 1
            print(f"  + {row['title'][:80]}")
        except Exception as e:
            print(f"  Skip: {e}")

inst_conn.close()
conn.commit()

total = conn.execute("SELECT COUNT(*) FROM profile_publications WHERE profile_id=4").fetchone()[0]
conn.close()

print(f"\nCross-analysis: {len(findings)} findings")
for f in findings:
    print(f"  - {f['title']}")
print(f"\nImported papers: {imported} ({total} total)")
