"""Seed PsiQuantum competitor profile."""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schema import init_profile_db, upsert_profile

conn = init_profile_db()

profile = {
    'company_name': 'PsiQuantum',
    'name_cn': 'PsiQuantum',
    'founded_year': 2016,
    'hq': 'Palo Alto, California, USA',
    'website': 'https://www.psiquantum.com',
    'employee_count': 588,
    'qubit_modality': '光子量子计算 — 硅光子学 (Silicon Photonics) + 融合基量子计算 (FBQC)',
    'tech_stage': '工程建造期 — 从学术验证转向工厂部署，Brisbane 工厂 2026-06 破土动工',
    'business_model': '容错量子计算机硬件 + 量子云服务 (目标直指 FTQC，不开发 NISQ 中间产品)',
    'ceo': 'Victor Peng (Interim CEO, 前 AMD 总裁/Xilinx CEO) / Jeremy O\'Brien (Executive Chairman, 创始人)',

    'founders': [
        {'name': 'Jeremy O\'Brien', 'role': 'Executive Chairman (创始人/前CEO)', 'background': '量子光子学先驱，前布里斯托大学教授，UNSW博士。2009年Science发表光子量子计算奠基论文。2026年2月卸任CEO转任执行主席。'},
        {'name': 'Pete Shadbolt', 'role': 'CSO & Co-Founder', 'background': '布里斯托大学博士，领导首个光子量子处理器公开API和VQE开发。'},
        {'name': 'Terry Rudolph', 'role': 'Chief Architect & Co-Founder', 'background': '前帝国理工学院教授，量子信息理论家，提出资源高效线形光量子计算模型（FBQC理论基础）。'},
        {'name': 'Mark Thompson', 'role': 'CTO & Co-Founder', 'background': '剑桥大学电子工程博士，20+年工业界经验(Toshiba/Corning)，集成光子学专家。'},
    ],

    'key_people': [
        {'name': 'Victor Peng', 'role': 'Interim CEO', 'background': '前AMD总裁，前Xilinx CEO(被AMD以$490亿收购)。2026年2月被引入推动规模化部署。标志着PsiQuantum从研发走向工程交付。'},
        {'name': 'Jeremy O\'Brien', 'role': 'Executive Chairman', 'background': '创始人，量子光子学先驱。2009年Science论文奠定光子量子计算基础。2026年2月从CEO转任执行主席。'},
        {'name': 'Pete Shadbolt', 'role': 'CSO', 'background': '联合创始人，布里斯托博士，光子量子处理器和VQE开发负责人。'},
        {'name': 'Terry Rudolph', 'role': 'Chief Architect', 'background': '联合创始人，帝国理工教授，FBQC架构理论奠基人。'},
        {'name': 'Mark Thompson', 'role': 'CTO', 'background': '联合创始人，剑桥博士，集成光子学专家，20+年Toshiba/Corning经验。'},
        {'name': 'Geoff Pryde', 'role': 'CTD, PsiQuantum Australia', 'background': 'Griffith大学教授，Brisbane测试与验证实验室负责人，量子光学与测量专家。'},
    ],

    'total_funding_usd': 4600000000,
    'funding_history': [
        {'date': '2021-08', 'round': 'D轮', 'amount_usd': 450000000, 'investors': ['BlackRock', 'Baillie Gifford', 'Microsoft'], 'note': '估值~$3B'},
        {'date': '2024-04', 'round': '战略轮', 'amount_usd': 620000000, 'investors': ['澳洲联邦政府', '昆士兰州政府'], 'note': 'A$940M 澳政府承诺用于 Brisbane 工厂'},
        {'date': '2025-03', 'round': '战略轮', 'amount_usd': 750000000, 'investors': ['未公开'], 'note': ''},
        {'date': '2025-09', 'round': 'E轮', 'amount_usd': 1000000000, 'investors': ['BlackRock(领投)', 'Temasek', 'Baillie Gifford', 'Macquarie Capital', 'NVentures(NVIDIA)', 'QIA', 'Morgan Stanley'], 'note': '估值~$7B，NVIDIA战略入局'},
        {'date': '2026-05', 'round': '战略轮', 'amount_usd': 1500000000, 'investors': ['未公开'], 'note': '估值~$10.5B。全球估值最高的纯量子计算创业公司。'},
    ],

    'valuation_usd': 10500000000,

    'products': [
        {'name': 'Omega 芯片组', 'type': '量子处理器', 'description': '可量产的硅光子芯片组，集成单光子源、探测器、开关和BTO高速光开关。GF 45nm SOI工艺。99.98%单比特保真度，99.5%双光子干涉可见度，99.72%芯片间互联保真度。发表于Nature(2025)。', 'status': '验证中', 'launch_date': '2025-02'},
        {'name': 'Construct 平台', 'type': '软件SDK', 'description': '容错量子算法设计的开源工具集。支持可视化容错电路设计、Python函数级编程、QREF开源容错算法标准格式、BARTIQ开源编译工具集成。', 'status': '商用', 'launch_date': '2025-09'},
        {'name': 'Brisbane 量子计算机', 'type': '量子计算机(建造中)', 'description': '全球首台实用级容错量子计算机。A$940M澳政府资助，Moreton Bay Central。2026-06破土动工，目标2027年底投入运营。Linde Engineering承建大型低温冷却系统。', 'status': '建造中', 'launch_date': '2028-2029'},
        {'name': 'Chicago 量子计算机', 'type': '量子计算机(计划中)', 'description': '美国本土部署。$500M+州/地方激励。2025年破土，目标2028年首台系统上线。', 'status': '计划中', 'launch_date': '2028'},
    ],

    'partnerships': [
        {'partner': 'GlobalFoundries', 'date': '2019', 'type': '芯片制造', 'description': 'Fab 8(纽约)制造Omega芯片，200mm SOI工艺平台，已生产数千片晶圆。引入超导材料和BTO进入商用Fab。'},
        {'partner': 'NVIDIA', 'date': '2025-09', 'type': '战略投资+技术合作', 'description': 'NVentures参投E轮。CUDA-Q平台集成，Grace Hopper超算+QPU协同。'},
        {'partner': '澳洲联邦政府', 'date': '2024-04', 'type': '政府资助', 'description': 'A$940M承诺用于Brisbane工厂建设，是量子计算领域全球最大单笔政府资助。'},
        {'partner': 'Linde Engineering', 'date': '2026-03', 'type': '低温工程', 'description': '设计并交付Brisbane工厂的大型低温冷却系统(4K温区)。全球首个为量子计算定制的工业级液氦系统。'},
        {'partner': 'Griffith University', 'date': '2026', 'type': '测试验证', 'description': 'Brisbane测试与验证实验室，配备定制低温系统"Poseidon"，可同时冷却/测试/测量多片光子量子芯片。'},
        {'partner': 'DARPA', 'date': '2025', 'type': '政府验证', 'description': '入选DARPA量子基准测试计划(QBI)最终阶段，接受美国政府最严格的量子技术验证。'},
        {'partner': 'Airbus & Lockheed Martin', 'date': '2024', 'type': '应用合作', 'description': '探索量子计算在航空航天和国防领域的应用场景。'},
    ],

    'tech_milestones': [
        {'date': '2009', 'description': 'Jeremy O\'Brien在Science发表光子量子计算奠基论文', 'significance': '理论起点——证明光子路线可实现通用量子计算'},
        {'date': '2016', 'description': 'PsiQuantum成立，四位英国量子物理学家在硅谷创业', 'significance': '全球首个以硅光子学为路线的量子计算公司'},
        {'date': '2019', 'description': '与GlobalFoundries建立战略合作关系', 'significance': '确立"半导体Fab量产"路径，区别于所有竞争对手'},
        {'date': '2021-08', 'description': 'D轮$450M，估值$3B', 'significance': '光子量子计算路线首次获得大规模资本验证'},
        {'date': '2024-04', 'description': '获得澳洲A$940M政府承诺', 'significance': '量子计算史上最大单笔政府资助'},
        {'date': '2025-02', 'description': 'Omega芯片组在Nature发表', 'significance': '首次公开展示可量产的光子量子处理器芯片'},
        {'date': '2025-09', 'description': 'E轮$1B(NVIDIA参投)+Construct平台发布', 'significance': '估值$7B，NVIDIA战略入局，软件工具链成熟化'},
        {'date': '2026-02', 'description': 'Victor Peng(前AMD总裁/Xilinx CEO)出任Interim CEO', 'significance': '从学术创业→工业交付的领导力转型，标志工程化加速'},
        {'date': '2026-06', 'description': 'Brisbane工厂破土动工', 'significance': '全球首座实用级容错量子计算机实体建筑开建'},
    ],

    'swot': {
        'strengths': [
            '融资规模全球第一: $4.6B+，$10.5B估值，光子路线绝对龙头',
            '芯片量产路径独特: 与GlobalFoundries合作，利用现有半导体Fab而非自建产线，规模化路径最短',
            '政府关系深厚: 澳A$940M+美$500M+DARPA QBI，国家级战略资产定位',
            'CEO转型信号明确: Victor Peng(AMD/Xilinx)入主，对标半导体工业成熟的工程管理范式',
            'Omega芯片经同行评审: Nature 2025发表，第三方验证技术可行性',
            '软件工具链成型: Construct平台+QREF+BARTIQ开源生态',
        ],
        'weaknesses': [
            '零商业营收: 至今未交付任何商用产品，全部依赖融资和政府资助',
            'FBQC架构未经大规模验证: 单芯片演示→百万比特系统之间存在数量级工程鸿沟',
            'CEO不稳定: 创始人卸任、Interim CEO过渡期，高层战略连贯性存疑',
            '芯片间互联瓶颈: 99.72%保真度对FBQC的纠错开销可能仍有不足',
            '量子比特不可存储: 光子是"飞行量子比特"，无法像原子/超导那样静态保持，对时序同步要求极高',
            '路线单一: 无NISQ过渡产品，若FTQC延迟则无备选现金流',
        ],
        'opportunities': [
            '若2028年率先交付FTQC，将成为量子计算的"Intel时刻"——首个标准化、可复制的量子计算机工厂',
            '澳政府深度绑定，可能辐射亚太量子市场',
            '半导体供应链已建立(GF)，规模化复制边际成本递减',
            'NVIDIA生态集成: GPU-QPU协同可能创造新的混合计算范式',
            'DARPA QBI验证若通过，将获得美国政府最高级别的技术认证和后续合同',
        ],
        'threats': [
            'Brisbane 2027年底的运营目标可能延迟——1.5年内完成工厂建设+芯片量产+系统集成极不现实',
            'Google/IBM超导路线、QuEra中性原子路线也在2028-2029年瞄准FTQC，先发窗口极窄',
            '$10.5B估值需要FTQC成功才能支撑，若延迟则面临down round甚至破产',
            '澳政府A$940M附带交付条件，未达标可能导致资金撤回',
            '光子路线缺乏NISQ阶段的商业验证——没有像IonQ/Quantinuum那样的早期营收来缓冲风险',
            'Xanadu(加拿大)同为光子路线，虽然规模和融资远小于PsiQuantum，但在软件生态和学术界有竞争力',
        ],
    },

    'competitive_positioning': (
        'PsiQuantum是全球估值最高、融资最多的纯量子计算创业公司($10.5B, $4.6B+)，也是唯一采用硅光子学+半导体Fab量产策略的量子计算企业。'
        '不同于QuEra(中性原子)、IBM/Google(超导)、Quantinuum(离子阱)，PsiQuantum不开发NISQ中间产品，而是直接从"芯片量产"切入FTQC。'
        '其核心赌注是：量子计算的关键瓶颈不是物理原理，而是制造规模——只要能像生产CPU一样在半导体Fab里量产光子量子芯片，百万比特的FTQC就能实现。'
        '这一战略的逻辑基础成立(GF已验证Omega芯片)，但时间表极其激进(2年内从破土到运营)，且零商业营收的财务模型使公司完全依赖融资续命。'
    ),

    'latest_summary': (
        '2026年6月，PsiQuantum在澳大利亚Brisbane的$1B级量子计算机工厂正式破土动工，目标2027年底投入运营。'
        'CEO Jeremy O\'Brien于2026年2月卸任，前AMD总裁/Xilinx CEO Victor Peng出任Interim CEO，标志公司从学术创业转向工业交付。'
        'Omega芯片组(Nature 2025)已在GlobalFoundries Fab 8量产验证，Construct软件平台开源。'
        '公司与NVIDIA建立战略合作，入选DARPA QBI最终阶段。累计融资$4.6B+，估值$10.5B。'
    ),

    'profile_status': 'complete',
    'last_researched': '2026-07-14',
}

profile_id = upsert_profile(conn, profile)
print(f'Profile created: id={profile_id}')
print(f'Funding: ${profile["total_funding_usd"]/1e9:.1f}B')
print(f'Valuation: ${profile["valuation_usd"]/1e9:.1f}B')
print(f'Products: {len(profile["products"])}')
print(f'Partnerships: {len(profile["partnerships"])}')
print(f'Milestones: {len(profile["tech_milestones"])}')
print(f'SWOT: S={len(profile["swot"]["strengths"])} W={len(profile["swot"]["weaknesses"])} O={len(profile["swot"]["opportunities"])} T={len(profile["swot"]["threats"])}')

conn.close()
