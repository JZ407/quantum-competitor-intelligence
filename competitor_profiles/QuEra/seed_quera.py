"""Seed the QuEra Computing competitor profile."""
import sys, json, os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from competitor_profiles.schema import init_profile_db, upsert_profile, add_source

conn = init_profile_db()

profile = {
    'company_name': 'QuEra Computing',
    'name_cn': 'QuEra 量子计算',
    'founded_year': 2018,
    'hq': 'Boston, Massachusetts, USA',
    'website': 'https://www.quera.com',
    'employee_count': 150,
    'qubit_modality': '中性原子量子计算 (Neutral Atoms)',
    'tech_stage': '中期规模化 — 256 qubit 商用机 + 纠错路线图推进中',
    'business_model': '量子计算机硬件 + 云服务 (B2B)',
    'ceo': 'Alex Keesling (CEO) / Mikhail Lukin (Co-Founder, 哈佛教授)',

    'founders': [
        {'name': 'Mikhail Lukin', 'role': 'Co-Founder', 'background': '哈佛大学物理学教授，中性原子量子计算先驱，量子光学与冷原子物理权威'},
        {'name': 'Markus Greiner', 'role': 'Co-Founder', 'background': '哈佛大学物理学教授，光晶格与量子模拟专家'},
        {'name': 'Vladan Vuletic', 'role': 'Co-Founder', 'background': 'MIT物理学教授，冷原子与量子光学专家'},
        {'name': 'Alex Keesling', 'role': 'CEO & Co-Founder', 'background': '哈佛大学物理学博士，QuEra 创始 CEO'},
    ],

    'key_people': [
        {'name': 'Alex Keesling', 'role': 'CEO', 'background': '哈佛物理学博士，带领 QuEra 从0到256 qubit商用机'},
        {'name': 'Mikhail Lukin', 'role': 'Co-Founder / Chief Scientist', 'background': '哈佛教授，中性原子路线奠基人'},
        {'name': 'Nate Gemelke', 'role': 'CTO', 'background': '量子硬件工程负责人'},
        {'name': 'Yuval Boger', 'role': 'CMO', 'background': '前 Classiq CMO，量子计算行业营销专家'},
    ],

    'total_funding_usd': 330000000,
    'funding_history': [
        {'date': '2021-11', 'round': 'A轮', 'amount_usd': 17000000, 'investors': ['Rakuten', 'Day One Ventures', 'Frontiers Capital'], 'note': '17M from multiple investors'},
        {'date': '2022-08', 'round': '获得DARPA合同', 'amount_usd': 11000000, 'investors': ['DARPA'], 'note': 'DARPA ONISQ 计划合同'},
        {'date': '2023-06', 'round': 'B轮', 'amount_usd': 36000000, 'investors': ['Eclipse Ventures', 'Vaunted'], 'note': '36M B轮，日韩投资者参与'},
        {'date': '2024-11', 'round': '获得日本合同', 'amount_usd': 41000000, 'investors': ['日本AIST'], 'note': '与日本AIST合作部署量子计算机'},
        {'date': '2025-02', 'round': '战略轮', 'amount_usd': 230000000, 'investors': ['Google', '软银', 'Valor Equity Partners'], 'note': '2.3亿美元大额战略轮，Google和软银领投，非稀释性融资主体'},
    ],

    'valuation_usd': 1500000000,

    'products': [
        {'name': 'Aquila', 'type': '量子计算机', 'description': '256-qubit 中性原子量子计算机。基于铷原子光镊阵列，支持模拟和数字模式。已在 AWS Braket 上提供云服务。', 'status': '商用', 'launch_date': '2022-11'},
        {'name': 'Gemini-Class 系统', 'type': '量子计算机 (研发中)', 'description': '下一代系统，支持横向逻辑门(Transversal Gates)，纠错能力提升。目标：1000+逻辑量子比特。', 'status': '研发中', 'launch_date': '2028-2029'},
        {'name': 'Bloqade', 'type': '软件SDK', 'description': '中性原子量子计算开源编程框架。支持模拟和数字模式，脉冲级控制。Python SDK。', 'status': '商用', 'launch_date': '2023'},
        {'name': 'Tsim', 'type': '模拟器工具', 'description': '快速通用量子错误校正模拟器。支持非克利福德电路模拟，用于验证纠错方案性能。', 'status': '商用', 'launch_date': '2026-04'},
        {'name': 'Amazon Braket 集成', 'type': '云服务', 'description': 'Aquila 是首个上架 AWS Braket 的中性原子量子计算机。通过 qBraid 平台也可访问。', 'status': '商用', 'launch_date': '2023'},
    ],

    'partnerships': [
        {'partner': 'AWS (Amazon Braket)', 'date': '2023', 'type': '云平台', 'description': 'Aquila 首个上架 AWS Braket 的中性原子系统，2028年目标实现纠错量子计算'},
        {'partner': 'NVIDIA', 'date': '2024', 'type': '计算加速', 'description': 'GPU加速量子模拟与纠错算法开发'},
        {'partner': '日本 AIST', 'date': '2024-11', 'type': '国家项目', 'description': '4100万美元合同，在日本部署中性原子量子计算机'},
        {'partner': 'Pawsey 超算中心', 'date': '2025', 'type': 'HPC融合', 'description': '量子-HPC混合架构案例研究，澳大利亚国家级超算中心'},
        {'partner': 'Deloitte', 'date': '2026', 'type': '行业应用', 'description': '联合研究量子计算在医疗健康领域的应用'},
        {'partner': 'qBraid', 'date': '2024', 'type': '平台集成', 'description': '通过 qBraid 平台提供 Aquila 量子计算服务'},
        {'partner': 'NanoQT', 'date': '2025-03', 'type': '国际战略合作', 'description': '与日本 NanoQT 合作推进中性原子量子网络'},
        {'partner': 'HPE', 'date': '2026-06', 'type': 'HPC集成', 'description': '与 Hewlett Packard Enterprise 探索量子-HPC混合架构'},
        {'partner': '芬兰/欧洲 HPC 中心', 'date': '2024-2026', 'type': '政府合作', 'description': '欧洲多国HPC中心量子集成项目'},
    ],

    'tech_milestones': [
        {'date': '2021-11', 'description': '宣布256-qubit中性原子量子计算机 Aquila', 'significance': '当时最大规模的可编程中性原子量子系统'},
        {'date': '2022-11', 'description': 'Aquila 正式在 AWS Braket 上提供云服务', 'significance': '首个在公有云上运营的中性原子量子计算机'},
        {'date': '2023-05', 'description': 'Nature 封面：在 Aquila 上实现最大规模的量子优化实验', 'significance': '实验验证中性原子在组合优化问题上的优势'},
        {'date': '2024-03', 'description': 'Nature Physics: 恒开销容错量子计算方案 (Constant-Overhead FTQC)', 'significance': '理论突破——横向 STAR 架构可行的理论证明'},
        {'date': '2024-12', 'description': 'Nature: 逻辑魔态蒸馏实验验证', 'significance': '首次在中性原子平台上实验演示逻辑量子态制备'},
        {'date': '2025-09', 'description': 'Nature: 低开销横向容错架构实验验证', 'significance': '实现横向(Transversal)逻辑门的实验里程碑'},
        {'date': '2026-04', 'description': '发布 Tsim 快速纠错模拟器 + Transversal STAR 架构白皮书', 'significance': '展示 1000+ 逻辑量子比特的技术路线'},
        {'date': '2026-06', 'description': '与 AWS 联合宣布：目标2028年在 Braket 上提供纠错级量子计算', 'significance': '商业化路线图——3年内实现FTQC的公有云服务'},
    ],

    'swot': {
        'strengths': [
            '学术血统顶尖：哈佛+MIT三教授联合创办，Lukin是中性原子路线第一人',
            '硬件规模领先：256物理量子比特，工业界最大中性原子系统',
            '纠错路线图清晰：横向 STAR 架构已验证，目标2028年1000+逻辑比特',
            '公有云首发：首个在 AWS Braket 运营的中性原子平台，生态壁垒高',
            '大额融资支撑：2025年2.3亿美元战略轮(Google/软银)，估值15亿美元',
            '全球化布局：美国(Boston)+日本(AIST)+欧洲+澳洲 多地运营',
            '纵向一体化：Aquila硬件+Bloqade软件+Tsim模拟器全栈覆盖',
        ],
        'weaknesses': [
            '中性原子路线竞争加剧：Pasqal、Atom Computing 等同路线对手也在快速推进',
            '依赖超低温激光系统，硬件成本高、工程复杂度大',
            '与 IBM/Google 等超导路线巨头相比，品牌认知度仍有差距',
            'Aquila 当前仅支持模拟模式为主，数字门模式的保真度待提升',
            '日本/欧洲的大额政府合同虽多，但交付风险和时间表压力大',
        ],
        'opportunities': [
            '纠错路线率先突破：横向门架构可能有先发优势，领先离子阱和超导',
            '日本市场空白：AIST合同是全球最大中性原子国际合作项目',
            'HPC融合趋势：全球超算中心争相部署量子加速器，QuEra 已布局',
            '新路线图(2028 FTQC)可能吸引下一轮大规模融资或IPO',
            'AWS Braket 独家中性原子供应商地位带来持续云流量',
        ],
        'threats': [
            'Pasqal(法国)也是中性原子路线，欧洲市场可能优先倾向本土企业',
            'Atom Computing 已被 Quantinuum/Honeywell 体系吸收',
            'IBM 超导路线在纠错方面投入巨大(1000+物理量子比特计划)',
            '量子计算整体行业面临兑现压力——投资热潮后可能需要看到商业成果',
            '美国对华技术出口管制可能影响与中国/亚洲客户的合作',
        ],
    },

    'competitive_positioning': (
        'QuEra 是中性原子路线的全球领导者，拥有最大的可编程中性原子量子计算机(256 qubit)。'
        '与同路线对手 Pasqal(法国)和 Atom Computing 相比，QuEra 在云服务(AWS Braket)和'
        '纠错路线图(Transversal STAR 架构)上具有独特优势。'
        '在全员竞逐 FTQC 的 2026-2028 窗口期，QuEra 的横向门架构如果率先实现 1000+ 逻辑比特，'
        '将可能成为第一个实用化量子计算平台。'
        'Google 和软银的 2.3亿美元战略投资，以及日本AIST的国家级合同，为其提供了充足的资金支撑。'
    ),

    'latest_summary': (
        '2026年6月最新动态：QuEra 发布 Transversal STAR 架构路线图，宣称可在2028-2029年实现'
        '1000+逻辑量子比特，纠错后保真度达 99.9999999%。'
        '同期与 AWS 联合宣布目标2028年在 Amazon Braket 上提供容错量子计算服务。'
        '已与 HPE 合作探索量子-HPC 混合架构。'
        '公司目前在波士顿运营256-qubit Aquila量子计算机，并通过AWS Braket提供云访问。'
    ),

    'profile_status': 'complete',
    'last_researched': '2026-06-26',
}

profile_id = upsert_profile(conn, profile)
print(f'Profile created/updated: id={profile_id}')
print(f'Company: {profile["company_name"]}')
print(f'Funding: ${profile["total_funding_usd"]/1e6:.0f}M')
print(f'Employees: {profile["employee_count"]}')
print(f'Products: {len(profile["products"])}')
print(f'Partnerships: {len(profile["partnerships"])}')
print(f'Milestones: {len(profile["tech_milestones"])}')
print(f'SWOT: S={len(profile["swot"]["strengths"])} W={len(profile["swot"]["weaknesses"])} O={len(profile["swot"]["opportunities"])} T={len(profile["swot"]["threats"])}')

conn.close()
