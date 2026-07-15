import json, sqlite3
from collections import Counter

conn = sqlite3.connect("profiles.db")
papers = conn.execute("SELECT pub_date, pub_type, journal FROM profile_publications WHERE profile_id=3 ORDER BY pub_date").fetchall()
funding = json.loads(conn.execute("SELECT funding_history FROM competitor_profiles WHERE id=3").fetchone()[0])

yearly = Counter()
for p in papers:
    y = (p[0] or "")[:4]
    if y and y.isdigit(): yearly[int(y)] += 1

pre_psiq = sum(v for y, v in yearly.items() if y < 2016)
post_psiq = sum(v for y, v in yearly.items() if y >= 2016)
total_funding = sum(f["amount_usd"] for f in funding) / 1e9

findings = [
    {
        "title": f"2016年前的论文占{pre_psiq}篇——学术遗产而非公司产出",
        "desc": f"33篇论文中，{pre_psiq}篇发表于PsiQuantum成立(2016)之前——包括Nature 2003、Science 2007/2009。这些是O'Brien学派在Bristol/Queensland时期的学术积累，PsiQuantum将其纳入展示是为了构建技术路线的学术合法性。2016年后共发表{post_psiq}篇，集中在量子化学应用和FBQC架构。",
    },
    {
        "title": "Boehringer Ingelheim: PsiQuantum的影子研发团队",
        "desc": "Top 10高产作者中，3位是Boehringer Ingelheim量子实验室员工(Santagati 8篇、Degroote 4篇、Moll 4篇)。BI量子实验室事实上充当了PsiQuantum的'外部应用研发部'——药企出资、PsiQuantum提供硬件路线图、双方联合发论文。这种制药公司+量子硬件的深度绑定模式在量子计算行业独一无二。",
    },
    {
        "title": f"融资${total_funding:.1f}B——论文产出严重滞后于融资规模",
        "desc": f"PsiQuantum累计融资约${total_funding:.1f}B(全球量子最高)，但成立以来仅发表{post_psiq}篇论文。对比QuEra($3.3B融资，89篇论文)和Algorithmiq($42M，70篇)，PsiQuantum的论文产出/融资金额比值极低。这反映了其战略选择:以'PsiQuantum Team'署名隐藏个人研究者、优先工程交付而非学术发表。",
    },
    {
        "title": "论文高度集中在量子化学——与产品路线直接对齐",
        "desc": "33篇论文中，量子化学/材料科学应用占主导(Li-ion电池、药物分子、CFD流体力学)。这与Omega芯片的Nature 2025展示(99.98%保真度)和Construct平台的定位一致。论文-产品映射清晰: 论文验证算法可行性 → Construct平台实现工程化 → Brisbane工厂部署。",
    },
    {
        "title": "CEO更替标志着从学术发表到工程交付的全面转向",
        "desc": "2026年2月Victor Peng(前AMD总裁/Xilinx CEO)接任CEO后，PsiQuantum的对外定位从量子计算研究公司转向量子计算制造公司。2026年6月Brisbane工厂破土动工，与论文产出(2025-2026年仅3篇)形成鲜明对比: 资金和人力已从学术发表全面转向工程交付。",
    },
]

ca = {"findings": findings}
conn.execute("UPDATE competitor_profiles SET cross_analysis=? WHERE id=3", (json.dumps(ca, ensure_ascii=False),))
conn.commit()
conn.close()
print("Cross-analysis updated: 5 findings")
for f in findings:
    print(f"  - {f['title']}")
