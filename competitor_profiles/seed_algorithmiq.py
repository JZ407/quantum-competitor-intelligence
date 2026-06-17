"""Seed the Algorithmiq competitor profile."""
import sys, json, os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from competitor_profiles.schema import init_profile_db, upsert_profile, add_source

conn = init_profile_db()

profile = {
    'company_name': 'Algorithmiq',
    'name_cn': '算法量子',
    'founded_year': 2020,
    'hq': 'Milan, Italy (原Helsinki, Finland)',
    'website': 'https://algorithmiq.fi',
    'employee_count': 50,
    'qubit_modality': '软件层 — 硬件无关 (支持超导/离子阱/中性原子)',
    'tech_stage': '早期商业化 (2024年起)',
    'business_model': '量子算法软件 + 企业合作 (B2B SaaS + 联合研发)',
    'ceo': 'Sabrina Maniscalco',

    'founders': [
        {'name': 'Sabrina Maniscalco', 'role': 'CEO & Co-Founder', 'background': '赫尔辛基大学量子物理教授，WEF技术先锋，CERN量子技术顾问'},
        {'name': 'Guillermo García-Pérez', 'role': 'CSO & Co-Founder', 'background': '量子信息科学家，张量网络与误差缓解专家'},
        {'name': 'Matteo Rossi', 'role': 'CTO & Co-Founder', 'background': '量子计算与机器学习交叉领域'},
        {'name': 'Boris Sokolov', 'role': 'Lead Researcher & Co-Founder', 'background': '量子物理研究员'},
    ],

    'key_people': [
        {'name': 'Sabrina Maniscalco', 'role': 'CEO', 'background': 'WEF技术先锋，CERN量子技术顾问委员会成员'},
        {'name': 'Guillermo García-Pérez', 'role': 'CSO', 'background': '量子纠错与张量网络专家'},
        {'name': 'Ivano Tavernelli', 'role': '合作PI (IBM)', 'background': 'IBM量子研究科学家，Q4Bio项目共同PI'},
    ],

    'total_funding_usd': 42400000,
    'funding_history': [
        {'date': '2021', 'round': '种子轮', 'amount_usd': 4000000, 'investors': ['未公开'], 'note': '初始启动资金'},
        {'date': '2023', 'round': 'A轮', 'amount_usd': 15000000, 'investors': ['Inventure VC'], 'note': '约€13.7M'},
        {'date': '2025', 'round': '非稀释性奖金', 'amount_usd': 2000000, 'investors': ['Wellcome Leap'], 'note': 'Q4Bio Challenge 唯一冠军 ($50M总奖金池)'},
        {'date': '2026-05', 'round': 'B轮', 'amount_usd': 21200000, 'investors': ['United Ventures', 'CDP Venture Capital', 'Inventure VC'], 'note': '€18M，意大利最大量子VC轮。总部迁至米兰'},
    ],

    'valuation_usd': None,

    'products': [
        {'name': 'Aurora', 'type': '平台', 'description': '量子化学分子模拟平台。用于药物发现、材料科学、光动力癌症疗法模拟。', 'status': '商用', 'launch_date': '2024'},
        {'name': 'TEM (Tensor-network Error Mitigation)', 'type': '工具', 'description': '基于张量网络的后处理误差缓解。91量子比特x4095门验证。IBM Qiskit Catalog销售。', 'status': '商用', 'launch_date': '2024-09'},
        {'name': 'Digital Quantum Interface (DQI)', 'type': '平台', 'description': '连接量子计算机与经典HPC，专利信息完备测量(IC-POVM)。', 'status': '商用', 'launch_date': '2024'},
        {'name': 'Measurement Toolbox', 'type': '工具', 'description': '信息完备测量优化，减少误差并节约计算资源。', 'status': '商用', 'launch_date': '2024'},
        {'name': 'Circuit Optimisation Toolbox', 'type': '工具', 'description': '最小化量子电路中的门数和操作，降低噪声。', 'status': '商用', 'launch_date': '2024'},
    ],

    'partnerships': [
        {'partner': 'IBM Quantum', 'date': '2022', 'type': '核心硬件伙伴', 'description': 'TEM上架Qiskit Functions Catalog；联合验证量子优势；Quantum Advantage Tracker'},
        {'partner': 'NVIDIA', 'date': '2024-11', 'type': '计算加速', 'description': 'GPU加速TEM，实现300倍速度提升'},
        {'partner': 'Microsoft Azure Quantum', 'date': '2024', 'type': '云平台合作', 'description': '算法集成至Azure Quantum平台和QDK'},
        {'partner': 'Rigetti Computing', 'date': '2024', 'type': '硬件合作', 'description': '商业硬件接入协议'},
        {'partner': 'Cleveland Clinic', 'date': '2023', 'type': '医疗应用', 'description': '光动力癌症疗法量子化学模拟；量子网络医学'},
        {'partner': 'Fraunhofer ISC', 'date': '2025', 'type': '材料研发', 'description': '量子计算+AI加速材料开发（制药、能源、制造）'},
        {'partner': 'Quantum Circuits Inc.', 'date': '2024', 'type': '硬件合作', 'description': '酶反应速率预测（药物代谢）'},
        {'partner': 'CERN', 'date': '2024', 'type': '研究合作', 'description': 'CEO担任CERN量子技术顾问'},
    ],

    'tech_milestones': [
        {'date': '2024-09', 'description': 'TEM上架IBM Qiskit Functions Catalog，首批第三方量子工具', 'significance': '首次商业化产品'},
        {'date': '2025-02', 'description': 'Q4Bio冠军：100量子比特端到端模拟光动力癌症药物', 'significance': '击败Harvard/Oxford/Stanford，行业最高水平验证'},
        {'date': '2025-06', 'description': 'IBM Heron上91量子比特x4095纠缠门模拟，声称验证量子优势', 'significance': '迄今最大规模误差缓解实验之一'},
        {'date': '2025-11', 'description': 'NVIDIA加速TEM实现300倍提速', 'significance': '走向实用化速度'},
        {'date': '2026-05', 'description': '总部从赫尔辛基迁至米兰，€18M B轮融资', 'significance': '战略重心转向欧洲大陆，商业化提速'},
    ],

    'swot': {
        'strengths': [
            '学术血统强：CEO是赫尔辛基大学教授，WEF技术先锋，CERN顾问',
            '硬件无关：不绑定任何量子硬件，可跨IBM/微软/Rigetti/QCI多平台运行',
            '已获最高水平第三方验证：Q4Bio冠军（击败Harvard/Oxford/Stanford）',
            '产品已商用：TEM在IBM Qiskit Catalog销售，250+ IBM量子网络成员为潜在客户',
            '利基市场精确：专注生命科学/化学这一最有商业价值的量子应用方向',
        ],
        'weaknesses': [
            '纯软件公司，依赖硬件伙伴的性能提升才能发挥价值',
            '人员规模小(~50人)，相比竞争对手资源有限',
            '融资总额($42M)远低于量子中间件/硬件公司($190M-$280M级别)',
            '收入规模小(估算$3.4M/年)，尚未证明可持续商业模式',
            'CEO从学术界出身，商业化经验相对有限',
        ],
        'opportunities': [
            '意大利国家量子战略(2025启动)提供政策红利和人才储备',
            '生命科学行业量子应用市场快速增长（药物发现、个性化医疗）',
            'NISQ时代的误差缓解是所有硬件厂商的刚需，市场空间大',
            '多平台兼容策略可随着更多硬件成熟而扩大TAM',
            '量子网络医学等新方向有先发优势',
        ],
        'threats': [
            '硬件公司自研软件（如Quantinuum的tket、IBM的Qiskit原生功能）可能削弱第三方需求',
            '大厂(Google/Microsoft/IBM)可能通过收购或自研覆盖算法层',
            'Phasecraft等直接竞争对手也在做量子化学算法',
            '量子计算商业化时间表不确定性，客户可能缩减量子预算',
            '总部迁移可能导致团队流失',
        ],
    },

    'competitive_positioning': 'Algorithmiq 是量子软件栈中应用层的垂直专家，聚焦生命科学与化学模拟。与 Q-CTRL（控制基础设施层）和 Quantinuum（全栈硬件+软件）不在同一层级竞争。真正竞争对手是 Phasecraft、Quantistry 等量子化学算法公司。核心差异化：(1) TEM误差缓解技术的理论最优特性 (2) 硬件无关策略避免锁定风险 (3) Q4Bio冠军提供无与伦比的第三方背書。融资规模($42M)处于应用层公司前列，但与基础设施层公司($190M+)有数量级差距。',

    'latest_summary': '2026年5月，Algorithmiq完成€18M B轮融资（意大利最大量子VC轮），并将全球总部从赫尔辛基迁至米兰。公司正在从纯R&D向商业化转型，CEO表示2026年将是量子应用真正落地的年份。TEM已通过IBM Qiskit Catalog获得商业用户，NVIDIA加速版本实现300倍速度提升。Q4Bio冠军项目证明了100量子比特级药物模拟的可行性。',

    'profile_status': 'complete',
    'last_researched': datetime.now().isoformat(),
}

pid = upsert_profile(conn, profile)
print(f'Profile created: id={pid}')

sources = [
    ('https://quantumcomputingreport.com/algorithmiq-relocates-global-headquarters-to-milan-following-e18m-21-2m-usd-funding-round/', 'QCR: B轮融资+总部迁移'),
    ('https://tech.eu/2026/05/11/algorithmiq-moves-global-hq-to-milan-and-raises-eur18m-in-italys-largest-quantum-vc-round/', 'Tech.eu: €18M融资详情'),
    ('https://algorithmiq.fi/news/press-release-tem-ibm-qiskit-functions/', 'TEM在IBM Qiskit Catalog上架'),
    ('https://arcticstartup.com/algorithmiq-wins-2-million/', 'Q4Bio Challenge冠军'),
    ('https://www.algorithmiq.fi/news/press-release-algorithmiq-nvidia-partnership/', 'NVIDIA合作公告'),
    ('https://www.algorithmiq.fi/quantum-products/', 'Algorithmiq产品线'),
    ('https://www.insidequantumtechnology.com/news-archive/quantum-tech-pod-episode-75-algorithmiq-ceo-co-founder-sabrina-maniscalco/', 'CEO Sabrina Maniscalco专访'),
    ('https://quantumzeitgeist.com/top-quantum-software-companies/', '量子软件公司对比'),
]

for url, title in sources:
    add_source(conn, pid, 'general', url, title)

conn.close()
print(f'Saved {len(sources)} sources.')
print('Done.')
