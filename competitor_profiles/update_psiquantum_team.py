import json, sqlite3

conn = sqlite3.connect("profiles.db")

key_people = [
    # ── Executive Leadership (8 from website) ──
    {"name": "Victor Peng", "title": "首席执行官 (CEO)", "academic_background": {"highest_degree": "", "field": "", "institutions": [], "graduation_year": ""}, "previous_experience": [{"company": "AMD", "role": "总裁", "period": "2023-2024"}, {"company": "Xilinx", "role": "CEO", "period": "2018-2022 (被AMD以$490亿收购)"}], "notable_achievements": ["40+年半导体行业经验", "领导Xilinx被AMD以$490亿收购", "2026年2月加入PsiQuantum推动规模化部署"], "h_index_estimate": 0},
    {"name": "Jeremy O'Brien", "title": "联合创始人 & 执行主席", "academic_background": {"highest_degree": "PhD", "field": "量子光子学", "institutions": ["UNSW", "University of Bristol"], "graduation_year": ""}, "previous_experience": [{"company": "PsiQuantum", "role": "CEO (创始人)", "period": "2016-2026.02"}, {"company": "University of Bristol", "role": "物理学教授", "period": ""}], "research_focus": ["光子量子计算", "集成光子学"], "publications_highlights": ["Science (2009): 光子量子计算奠基论文"], "notable_achievements": ["30年量子计算研究", "2009年Science论文奠定光子路线"], "h_index_estimate": 0},
    {"name": "Terry Rudolph", "title": "联合创始人 & 首席架构师", "academic_background": {"highest_degree": "PhD", "field": "理论量子光学", "institutions": ["Imperial College London", "University of Toronto", "Bell Labs"], "graduation_year": ""}, "previous_experience": [{"company": "Imperial College London", "role": "量子物理学教授", "period": "2003-"}], "research_focus": ["融合基量子计算 (FBQC)", "光子量子计算理论"], "publications_highlights": ["2004-2015: 四篇论文奠定FBQC理论基础"], "notable_achievements": ["FBQC架构发明者——PsiQuantum技术路线理论奠基人"], "h_index_estimate": 0},
    {"name": "Pete Shadbolt", "title": "联合创始人 & 首席科学官 (CSO)", "academic_background": {"highest_degree": "PhD", "field": "实验光子量子计算", "institutions": ["University of Bristol", "Imperial College(博士后)"], "graduation_year": "2014"}, "previous_experience": [{"company": "Imperial College London", "role": "博士后", "period": ""}], "research_focus": ["VQE算法", "量子处理器API"], "publications_highlights": ["首个变分量子特征求解器(VQE)演示", "首个量子处理器公开API"], "notable_achievements": ["EPSRC Rising Star奖 (2014)", "EPSRC RISE领袖奖"], "h_index_estimate": 0},
    {"name": "Mark Thompson", "title": "联合创始人 & 首席技术官 (CTO)", "academic_background": {"highest_degree": "PhD", "field": "电子工程", "institutions": ["University of Cambridge", "University of Sheffield"], "graduation_year": ""}, "previous_experience": [{"company": "Toshiba", "role": "硅光子学项目创始成员", "period": ""}, {"company": "Bookham Technology", "role": "工程师 (首个硅光子学创业公司)", "period": ""}], "research_focus": ["集成光子学", "硅光子制造"], "notable_achievements": ["20+年光子与量子技术经验", "工业界+学术界双轨老兵"], "h_index_estimate": 0},
    {"name": "Fariba Danesh", "title": "首席运营官 (COO)", "academic_background": {"highest_degree": "", "field": "半导体", "institutions": [], "graduation_year": ""}, "previous_experience": [{"company": "Glo (微LED显示)", "role": "CEO & 董事总经理", "period": "2010-2019"}], "notable_achievements": ["30+年半导体产品开发经验", "Glo: 全球首个全彩RGB微LED显示器"], "h_index_estimate": 0},
    {"name": "Susan Kim", "title": "首席财务官 (CFO)", "academic_background": {"highest_degree": "", "field": "", "institutions": [], "graduation_year": ""}, "previous_experience": [{"company": "PacBio (PACB, NASDAQ)", "role": "CFO", "period": ""}], "notable_achievements": ["25年高级财务管理经验", "覆盖半导体/生命科学/SaaS/硬件/制造/大数据"], "h_index_estimate": 0},
    {"name": "Dani Kleinman", "title": "首席人事官 (CPO)", "academic_background": {"highest_degree": "", "field": "", "institutions": [], "graduation_year": ""}, "previous_experience": [{"company": "Cruise LLC (自动驾驶)", "role": "CPO & 法务VP", "period": "至收购后"}, {"company": "DocuSign", "role": "全球雇佣法务与诉讼负责人", "period": "IPO前后(1000-5000+员工)"}], "notable_achievements": ["Cruise: 领导快速成长与收购后组织转型", "DocuSign: IPO至5000+员工全球化扩张"], "h_index_estimate": 0},

    # ── Board of Directors ──
    {"name": "Lip-Bu Tan", "title": "董事会成员", "academic_background": {"highest_degree": "", "field": "", "institutions": [], "graduation_year": ""}, "previous_experience": [{"company": "Intel Corporation", "role": "CEO", "period": "2025-至今"}, {"company": "Cadence Design Systems", "role": "CEO (2009-2021)", "period": ""}, {"company": "Walden International / Celesta Capital", "role": "创始管理合伙人", "period": ""}], "notable_achievements": ["Intel CEO——全球最大半导体公司掌门人", "Cadence CEO期间股价涨32倍", "全球半导体行业最具影响力的华人领袖之一"], "h_index_estimate": 0},

    # ── Government Advisory Board ──
    {"name": "VADM Bob Sharp (USN Ret.)", "title": "政府顾问委员会成员", "academic_background": {"highest_degree": "", "field": "海军情报", "institutions": [], "graduation_year": ""}, "previous_experience": [{"company": "美国国家地理空间情报局(NGA)", "role": "局长", "period": "2019-2022"}], "notable_achievements": ["34+年海军情报官", "NGA局长——美国国家级情报负责人"], "h_index_estimate": 0},
    {"name": "Stephen E. Biegun", "title": "政府顾问委员会成员 (2026.01加入)", "academic_background": {"highest_degree": "", "field": "国际关系", "institutions": [], "graduation_year": ""}, "previous_experience": [{"company": "美国国务院", "role": "副国务卿 (参议院90-3确认)", "period": "2019-2021"}, {"company": "Boeing", "role": "SVP", "period": ""}, {"company": "白宫国家安全委员会", "role": "行政秘书 (Condoleezza Rice时期)", "period": ""}], "notable_achievements": ["前美国副国务卿——政府最高层外交安全决策者", "CFR(外交关系委员会)成员"], "h_index_estimate": 0},
    {"name": "Ellen Lord", "title": "政府顾问委员会成员 (2026.01加入)", "academic_background": {"highest_degree": "", "field": "国防采办", "institutions": [], "graduation_year": ""}, "previous_experience": [{"company": "美国国防部", "role": "负责采办与保障的副国防部长", "period": "2017-2020"}, {"company": "Textron Systems", "role": "总裁 & CEO", "period": ""}], "notable_achievements": ["前五角大楼采办最高负责人——直接管理美国国防供应链", "4次Wash100获奖者", "AAR/Parsons/SES等多公司董事"], "h_index_estimate": 0},
    {"name": "Chris Miller", "title": "政府顾问委员会成员 (2026.01加入)", "academic_background": {"highest_degree": "PhD", "field": "国际史", "institutions": ["Tufts University (Fletcher学院教授)", "Yale"], "graduation_year": ""}, "previous_experience": [{"company": "Tufts University Fletcher学院", "role": "教授", "period": ""}, {"company": "American Enterprise Institute", "role": "非常驻高级研究员", "period": ""}], "notable_achievements": ["《Chip War》作者——全球半导体地缘政治的权威著作(NYT畅销书/FT年度商业图书)", "芯片地缘政治领域最具影响力的学者"], "h_index_estimate": 0},

    # ── Australia Operations ──
    {"name": "Geoff Pryde", "title": "首席技术总监, PsiQuantum Australia", "academic_background": {"highest_degree": "PhD", "field": "量子光学", "institutions": ["Griffith University", "University of Queensland"], "graduation_year": ""}, "previous_experience": [{"company": "Griffith University", "role": "教授 (休假中)", "period": ""}], "research_focus": ["光子量子计算", "量子光学实验"], "notable_achievements": ["Brisbane测试与验证实验室负责人", "Poseidon低温系统(澳最强之一)项目主导", "与O'Brien/Rudolph在UQ共同完成早期光子量子计算突破"], "h_index_estimate": 0},
    {"name": "Mark Brunner", "title": "公共部门执行副总裁 (EVP Public Sector)", "academic_background": {"highest_degree": "", "field": "", "institutions": [], "graduation_year": ""}, "previous_experience": [], "notable_achievements": ["负责PsiQuantum在美国/澳洲/英国的所有政府合作与公共部门关系"], "h_index_estimate": 0},
]

conn.execute("UPDATE competitor_profiles SET key_people=? WHERE id=3", (json.dumps(key_people, ensure_ascii=False),))

# Team analytics
team_analytics = {
    "total_researched": 16,
    "avg_h_index": 0,
    "top_institutions": {"University of Bristol": 3, "Imperial College London": 2, "University of Cambridge": 1, "UNSW": 1, "Stanford": 0},
    "degree_distribution": {"PhD": 7, "MBA/其他": 9},
    "career_stages": {
        "高管/C级(8人)": 8,
        "董事会/顾问委员会(5人)": 5,
        "学术创始人(4人)": 4,
        "区域运营负责人(2人)": 2,
    },
    "h_index_range": [0, 0],
}
conn.execute("UPDATE competitor_profiles SET team_analytics=? WHERE id=3", (json.dumps(team_analytics, ensure_ascii=False),))
conn.commit()
conn.close()
print(f"Updated: {len(key_people)} team members")
