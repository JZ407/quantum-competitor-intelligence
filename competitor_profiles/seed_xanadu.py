"""Seed Xanadu competitor profile."""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schema import init_profile_db, upsert_profile

conn = init_profile_db()

profile = {
    'company_name': 'Xanadu',
    'name_cn': 'Xanadu 量子技术',
    'founded_year': 2016,
    'hq': 'Toronto, Ontario, Canada',
    'website': 'https://www.xanadu.ai',
    'employee_count': 260,
    'qubit_modality': '光子量子计算 — 连续变量 (Continuous-Variable) + GKP 编码 + 高斯玻色采样 (GBS)',
    'tech_stage': '规模化验证期 — Aurora 12逻辑量子比特实时纠错(Nature 2025)，目标2028容错、2029-2030量子数据中心',
    'business_model': '硬件+软件垂直整合。光量子计算机(Aurora)+量子编程平台(PennyLane)+云服务(Xanadu Cloud)。2026年3月SPAC上市(Nasdaq/TSX: XNDU)，成为全球首家纯光量子计算上市公司。',
    'ceo': 'Christian Weedbrook (Founder, CEO & Chairman)',

    'founders': [
        {'name': 'Christian Weedbrook', 'role': 'Founder, CEO & Chairman', 'background': '澳大利亚裔物理学家，昆士兰大学物理学博士，MIT和UofT博士后。曾创立量子安全公司CipherQ(2014)，2016年独自创立Xanadu。理论背景出身，以"白皮书+信念"说服投资者押注光子路线。2026年带领公司完成SPAC上市，成为全球首家光量子计算上市公司。'},
    ],

    'key_people': [
        # ====== C-Suite ======
        {'name': 'Christian Weedbrook', 'title': 'Founder, CEO & Chairman',
         'academic_background': {'highest_degree': 'PhD Physics', 'field': 'Quantum Information Theory', 'institutions': ['University of Queensland', 'MIT', 'University of Toronto'], 'graduation_year': '2008'},
         'previous_experience': [{'company': 'CipherQ', 'role': 'Founder', 'years': '2014-2016'}, {'company': 'MIT / UofT', 'role': 'Postdoctoral Fellow', 'years': '2008-2014'}],
         'research_focus': ['Quantum Information Theory', 'Continuous-Variable QC', 'Photonic QC Architecture'],
         'publications_highlights': ['Nature 2022: Borealis quantum advantage (co-author)', 'Nature 2025: Aurora modular photonic QC (co-author)'],
         'h_index_estimate': '~35', 'papers': 12},

        {'name': 'Zachary Vernon', 'title': 'CTO / Head of Hardware',
         'academic_background': {'highest_degree': 'PhD Physics', 'field': 'Integrated Photonics / Quantum Light', 'institutions': ['University of Toronto'], 'graduation_year': '2017'},
         'previous_experience': [{'company': 'Xanadu', 'role': 'Physicist -> Head of Hardware -> CTO', 'years': '2017-present'}],
         'research_focus': ['Integrated Photonics', 'GKP Qubits', 'Photonic QEC', 'Quantum Hardware Architecture'],
         'publications_highlights': ['Nature 2025: Aurora modular photonic QC (lead author)', 'OFC 2024: Universal Fault-Tolerant Photonic QC'],
         'h_index_estimate': '#1 Xanadu patent inventor (14)', 'papers': 9},

        {'name': 'Nathan Killoran', 'title': 'CTO Software / Head of Software & Algorithms',
         'academic_background': {'highest_degree': 'PhD Quantum Information', 'field': 'Quantum Computing', 'institutions': ['University of Waterloo (IQC)', 'University of Toronto', 'University of Guelph'], 'graduation_year': '2012'},
         'previous_experience': [{'company': 'UofT / evolutionQ', 'role': 'ML Researcher / Quantum Consultant', 'years': '2016-2021'}, {'company': 'University of Ulm', 'role': 'QC Researcher', 'years': '2013-2016'}],
         'research_focus': ['Quantum ML', 'Differentiable Quantum Programming', 'Hybrid Quantum-Classical Compilation'],
         'publications_highlights': ['PennyLane: Auto-diff of hybrid quantum-classical computations (1811.04968)', '36 papers -- #2 most prolific author at Xanadu'],
         'h_index_estimate': '~30', 'papers': 36},

        {'name': 'Juan Miguel Arrazola', 'title': 'Head of Algorithms / Director of Quantum Algorithms',
         'academic_background': {'highest_degree': 'PhD Quantum Information', 'field': 'Quantum Information', 'institutions': ['University of Waterloo (IQC)', 'University of Toronto', 'Universidad de Los Andes (Colombia)'], 'graduation_year': '2015'},
         'previous_experience': [{'company': 'CQT Singapore', 'role': 'Research Fellow', 'years': '2016-2017'}, {'company': 'Xanadu', 'role': 'Theoretical Physicist -> Head of Algorithms', 'years': '2017-present'}],
         'research_focus': ['Quantum Algorithms', 'Quantum Chemistry', 'Photonic QC', 'Fault-Tolerant Algorithms'],
         'publications_highlights': ['53 papers -- #1 most prolific Xanadu author', 'PRX Quantum 2024: Initial State Preparation for Quantum Chemistry'],
         'h_index_estimate': '~25', 'papers': 53},

        {'name': 'Rafal Janik', 'title': 'COO',
         'academic_background': {'highest_degree': '', 'field': '', 'institutions': [], 'graduation_year': ''},
         'previous_experience': [], 'research_focus': ['Operations', 'Scale-up Management'],
         'publications_highlights': [], 'papers': 0},

        {'name': 'Michael Trzupek', 'title': 'CFO',
         'academic_background': {'highest_degree': '', 'field': '', 'institutions': [], 'graduation_year': ''},
         'previous_experience': [{'company': 'Core Scientific', 'role': 'CFO', 'years': ''}, {'company': 'Microsoft / Intel / Imagination Tech', 'role': 'Finance Leadership', 'years': ''}],
         'research_focus': ['Public Market Finance', 'SPAC/IPO Execution'],
         'publications_highlights': ['Joined Jan 2026 for IPO readiness'], 'papers': 0},

        {'name': 'Natalie Wilmore', 'title': 'CLO',
         'academic_background': {'highest_degree': '', 'field': '', 'institutions': [], 'graduation_year': ''},
         'previous_experience': [{'company': 'Pagaya / Skillz / IBM', 'role': 'VP/Deputy GC & Legal', 'years': ''}],
         'research_focus': ['IPO Compliance', 'IP Strategy'],
         'publications_highlights': ['Joined Jan 2026'], 'papers': 0},

        {'name': 'Rebecca Laramee', 'title': 'CPO',
         'academic_background': {'highest_degree': '', 'field': '', 'institutions': [], 'graduation_year': ''},
         'previous_experience': [], 'research_focus': ['Talent Strategy', 'Org Expansion (260->310+)'],
         'publications_highlights': [], 'papers': 0},

        # ====== Hardware ======
        {'name': 'Blair Morrison', 'title': 'Senior Hardware Scientist',
         'academic_background': {'highest_degree': 'PhD', 'field': 'Integrated Photonics / Optical Engineering', 'institutions': [], 'graduation_year': ''},
         'previous_experience': [],
         'research_focus': ['Integrated Photonic Components', 'Waveguides/Couplers', 'GKP Qubit Chips', 'Optical Interconnects'],
         'publications_highlights': ['Nature 2025: Aurora co-author', '#2 patent inventor at Xanadu (9 patents)'],
         'h_index_estimate': '9 patents', 'papers': 9},

        {'name': 'Matteo Menotti', 'title': 'Photonic Hardware Researcher',
         'academic_background': {'highest_degree': 'PhD', 'field': 'Quantum Photonics', 'institutions': [], 'graduation_year': ''},
         'previous_experience': [],
         'research_focus': ['Integrated Quantum Photonics', 'Squeezed Light Generation', 'Nanophotonic Molecules'],
         'publications_highlights': ['Nature 2021: 8(1)dB on-chip squeezing (record at time)', 'Nature 2021: many-photon nanophotonic chip'],
         'h_index_estimate': '', 'papers': 8},

        {'name': 'Lukas Helt', 'title': 'Photonic Hardware Researcher',
         'academic_background': {'highest_degree': 'PhD', 'field': 'Quantum Photonics', 'institutions': [], 'graduation_year': ''},
         'previous_experience': [],
         'research_focus': ['Integrated Quantum Photonics', 'Squeezed Light', 'Photonic Chips'],
         'publications_highlights': ['Nature 2021: nanophotonic chip co-author', 'Nature 2025: Aurora co-author'],
         'h_index_estimate': '', 'papers': 6},

        {'name': 'Kianna Tan', 'title': 'Photonic Hardware Researcher',
         'academic_background': {'highest_degree': 'PhD', 'field': 'Nanophotonics / Quantum Optics', 'institutions': [], 'graduation_year': ''},
         'previous_experience': [],
         'research_focus': ['Nanophotonics', 'On-Chip Squeezed Light'],
         'publications_highlights': ['Nature 2021: nanophotonic chip co-author', 'On-chip squeezed light paper'],
         'h_index_estimate': '', 'papers': 6},

        # ====== Software & Algorithms ======
        {'name': 'Josh Izaac', 'title': 'Director of Product / Quantum Software Lead',
         'academic_background': {'highest_degree': 'PhD Quantum Computing', 'field': 'Computational Physics / Graph Algorithms', 'institutions': ['University of Western Australia'], 'graduation_year': '2017'},
         'previous_experience': [],
         'research_focus': ['Hybrid QC Compilation (Catalyst)', 'Differentiable QC (PennyLane)', 'Gaussian Boson Sampling', 'Quantum Software Dev'],
         'publications_highlights': ['Strawberry Fields + PennyLane founding developer', 'Catalyst QJIT compiler co-author', 'The Walrus (C++ GBS library)'],
         'h_index_estimate': '~20', 'papers': 18},

        {'name': 'Maria Schuld', 'title': 'Senior Researcher / Quantum ML Lead',
         'academic_background': {'highest_degree': 'PhD Physics', 'field': 'Quantum Computing & AI', 'institutions': ['University of KwaZulu-Natal (South Africa)', 'Technical University of Berlin'], 'graduation_year': '2017'},
         'previous_experience': [],
         'research_focus': ['Quantum Machine Learning', 'Quantum Kernel Methods', 'Hybrid Quantum-Classical Algorithms'],
         'publications_highlights': ['Book: Machine Learning with Quantum Computers (Springer, 2021)', 'PennyLane original developer'],
         'h_index_estimate': '~30', 'papers': 22},

        {'name': 'David Wierichs', 'title': 'PennyLane Core Developer',
         'academic_background': {'highest_degree': 'PhD', 'field': 'Quantum Computing', 'institutions': [], 'graduation_year': ''},
         'previous_experience': [],
         'research_focus': ['Quantum ML', 'Quantum Gradient Optimization', 'PennyLane Development'],
         'publications_highlights': ['PennyLane paper co-author (1811.04968)', 'Quantum kernel methods tutorial author'],
         'h_index_estimate': '', 'papers': 8},

        {'name': 'Thomas Bromley', 'title': 'Quantum Software Researcher',
         'academic_background': {'highest_degree': 'PhD', 'field': 'Quantum Computing / Quantum Information', 'institutions': [], 'graduation_year': ''},
         'previous_experience': [],
         'research_focus': ['Gaussian Boson Sampling Apps', 'CV Quantum Neural Networks', 'Quantum ML'],
         'publications_highlights': ['QST 2020: GBS applications (lead author, 7900+ citations)', 'Nature 2021: nanophotonic chip co-author'],
         'h_index_estimate': '25', 'papers': 17},

        # ====== Quantum Chemistry & Industrial Apps ======
        {'name': 'Alain Delgado', 'title': 'Quantum Algorithms Researcher (Battery & Materials)',
         'academic_background': {'highest_degree': 'PhD', 'field': 'Quantum Chemistry / Computational Physics', 'institutions': [], 'graduation_year': ''},
         'previous_experience': [],
         'research_focus': ['Fault-Tolerant QC Algorithms', 'Li-Ion Battery Simulation', 'XAS/X-ray Spectroscopy', 'Quantum Phase Estimation'],
         'publications_highlights': ['PR-A 2022: End-to-end Li-ion battery quantum algorithm (lead)', 'Volkswagen/Toyota collaborations'],
         'h_index_estimate': '', 'papers': 17},

        {'name': 'Stepan Fomichev', 'title': 'Algorithms Researcher (Condensed Matter & Chemistry)',
         'academic_background': {'highest_degree': 'PhD', 'field': 'Condensed Matter Physics / Quantum Chemistry', 'institutions': [], 'graduation_year': ''},
         'previous_experience': [],
         'research_focus': ['Condensed Matter Physics', 'Quantum Chemistry', 'Initial State Preparation'],
         'publications_highlights': ['PRX Quantum 2024: ISP for quantum chemistry (corresponding author)', 'Fields Institute talk (2024)'],
         'h_index_estimate': '', 'papers': 12},

        {'name': 'Modjtaba Shokrian Zini', 'title': 'Quantum Algorithms Researcher (Battery Simulation)',
         'academic_background': {'highest_degree': 'PhD', 'field': 'Quantum Chemistry / Materials Science', 'institutions': [], 'graduation_year': ''},
         'previous_experience': [],
         'research_focus': ['Battery Materials QC Simulation', 'Optically-Active Spin Defects', 'Ionic Pseudopotentials'],
         'publications_highlights': ['Battery materials QC simulation (Volkswagen collab)', 'PR-A 2024: Spin defect QC simulation'],
         'h_index_estimate': '', 'papers': 10},

        {'name': 'Ignacio Loaiza', 'title': 'Quantum Algorithms Researcher (Spectroscopy)',
         'academic_background': {'highest_degree': 'PhD', 'field': 'Quantum Chemistry / Chemical Physics', 'institutions': ['University of Toronto (affiliate)'], 'graduation_year': ''},
         'previous_experience': [],
         'research_focus': ['Quantum Spectroscopy Simulation', 'NIR/XAS Spectroscopy', 'Molecular Dynamics', 'pre-Born-Oppenheimer MD'],
         'publications_highlights': ['JCTC 2026: Trotter simulation of vibrational Hamiltonians', 'NIR quantum algorithm (orders-of-magnitude cost reduction)'],
         'h_index_estimate': '', 'papers': 8},

        {'name': 'Utkarsh Azad', 'title': 'Quantum Algorithms Researcher',
         'academic_background': {'highest_degree': '', 'field': 'Quantum Chemistry', 'institutions': [], 'graduation_year': ''},
         'previous_experience': [],
         'research_focus': ['Battery XAS Spectroscopy', 'Quantum Chemistry Simulation'],
         'publications_highlights': ['XAS battery fast QC simulation (Volkswagen collab)'],
         'h_index_estimate': '', 'papers': 6},

        {'name': 'Kasra Hejazi', 'title': 'Quantum Algorithms Researcher',
         'academic_background': {'highest_degree': 'PhD Physics', 'field': 'Condensed Matter Theory / Tensor Networks', 'institutions': ['UC Santa Barbara'], 'graduation_year': '2021'},
         'previous_experience': [{'company': 'Caltech', 'role': 'Postdoctoral Scholar', 'years': '2022'}, {'company': 'Xanadu', 'role': 'Quantum Algorithms Researcher', 'years': '2023-present'}],
         'research_focus': ['Condensed Matter Theory', 'Tensor Networks', 'Quantum Chaos', 'Quantum Dynamics'],
         'publications_highlights': ['PRX Quantum 2024: ISP for quantum chemistry'],
         'h_index_estimate': '', 'papers': 5},

        # ====== QEC & Architecture ======
        {'name': 'Guillaume Dauphinais', 'title': 'Lead Quantum Architecture Scientist',
         'academic_background': {'highest_degree': 'PhD', 'field': 'Quantum Information', 'institutions': [], 'graduation_year': ''},
         'previous_experience': [],
         'research_focus': ['Quantum Error Correction', 'Stabilizer QEC', 'Fault-Tolerant Photonic Architecture', 'Weight-Reduced Codes'],
         'publications_highlights': ['Quantum 2024: STAB-QEC (lead author)', 'PRX Quantum 2024: Low-overhead weight-reduced stabilizer codes', 'Blueprint paper co-author'],
         'h_index_estimate': '', 'papers': 8},

        {'name': 'J. Eli Bourassa', 'title': 'Quantum Architecture Researcher',
         'academic_background': {'highest_degree': 'PhD Physics', 'field': 'Photonic QC / Quantum Key Distribution', 'institutions': ['University of Toronto'], 'graduation_year': ''},
         'previous_experience': [{'company': 'Xanadu + UofT', 'role': 'Joint Researcher', 'years': 'during PhD'}],
         'research_focus': ['Fault-Tolerant Photonic QC', 'GKP Qubits', 'Quantum Key Distribution'],
         'publications_highlights': ['Quantum 2021: Blueprint for scalable photonic FTQC (lead author, 161 citations)'],
         'h_index_estimate': '', 'papers': 7},

        {'name': 'Ilan Tzitrin', 'title': 'Quantum Architecture Researcher',
         'academic_background': {'highest_degree': 'PhD Physics', 'field': 'Entanglement Theory / Optical QI', 'institutions': ['University of Toronto'], 'graduation_year': ''},
         'previous_experience': [{'company': 'Xanadu + UofT', 'role': 'Joint Postdoc -> Researcher', 'years': ''}],
         'research_focus': ['Entanglement Theory', 'Optical QI', 'Fault-Tolerant Photonic Architecture'],
         'publications_highlights': ['PR-A 2025: Single-shot measurement-based QEC', 'Blueprint paper co-author'],
         'h_index_estimate': '', 'papers': 7},

        {'name': 'Rafael N. Alexander', 'title': 'Quantum Architecture Researcher',
         'academic_background': {'highest_degree': 'PhD', 'field': 'QI / Continuous-Variable QC', 'institutions': ['RMIT University', 'Univ. of New Mexico', 'Univ. of Virginia'], 'graduation_year': ''},
         'previous_experience': [],
         'research_focus': ['GKP Qubits', 'CV Cluster States', 'Measurement-Based QC', 'All-Optical Quantum Communication'],
         'publications_highlights': ['PRX 2021: FTQC with Static Linear Optics', 'Blueprint + Nature 2025 co-author'],
         'h_index_estimate': '', 'papers': 5},

        {'name': 'Haoyu Qi', 'title': 'Quantum Researcher (Patents & Tensor Networks)',
         'academic_background': {'highest_degree': 'PhD', 'field': 'Quantum Information', 'institutions': [], 'graduation_year': ''},
         'previous_experience': [],
         'research_focus': ['Tensor Network QC Simulation', 'Quantum Circuit Optimization', 'GKP Non-Gaussian State Generation'],
         'publications_highlights': ['#10 patent inventor at Xanadu (4 patents)', 'Parallel tensor network QC simulation patent'],
         'h_index_estimate': '', 'papers': 11},

        # ====== Cross-cutting Research ======
        {'name': 'Pablo Antonio Moreno Casares', 'title': 'Senior Quantum Scientist',
         'academic_background': {'highest_degree': 'PhD Quantum Algorithms', 'field': 'Fault-Tolerant Quantum Algorithms', 'institutions': ['Universidad Complutense de Madrid', 'University of Oxford (MSc)'], 'graduation_year': ''},
         'previous_experience': [{'company': 'FAR AI', 'role': 'Sr. Communications Specialist', 'years': ''}],
         'research_focus': ['Fault-Tolerant Quantum Algorithms', 'Grover/Quantum Walks', 'Time-Dependent Hamiltonian Simulation'],
         'publications_highlights': ['PhD thesis: Fault-tolerant quantum algorithms', 'ML:S&T 2020 Reviewer of the Year'],
         'h_index_estimate': 'Remote from Madrid', 'papers': 12},

        {'name': 'K. K. Sabapathy', 'title': 'Quantum Researcher (Non-Gaussian States)',
         'academic_background': {'highest_degree': 'PhD', 'field': 'Quantum Optics / Quantum Information', 'institutions': [], 'graduation_year': ''},
         'previous_experience': [],
         'research_focus': ['Non-Gaussian Quantum States', 'GKP Qubits', 'CV Quantum Information'],
         'publications_highlights': ['Nature 2021: nanophotonic chip co-author', 'GKP non-Gaussian state generation patent'],
         'h_index_estimate': '', 'papers': 11},

        {'name': 'Kamil Bradler', 'title': 'Quantum Researcher (Algorithms & Patents)',
         'academic_background': {'highest_degree': 'PhD', 'field': 'Quantum Information / Quantum Optics', 'institutions': [], 'graduation_year': ''},
         'previous_experience': [],
         'research_focus': ['Quantum Algorithms', 'Temporal Photonic Cluster States', 'Quantum Blackboxes'],
         'publications_highlights': ['#6 patent inventor at Xanadu (5 patents)', 'Nature 2021: nanophotonic chip co-author', '2018: co-author of Xanadu earliest paper'],
         'h_index_estimate': '', 'papers': 10},

        {'name': 'Danial Motlagh', 'title': 'Quantum Algorithms Researcher',
         'academic_background': {'highest_degree': '', 'field': 'Quantum Computing', 'institutions': [], 'graduation_year': ''},
         'previous_experience': [],
         'research_focus': ['Quantum Algorithm Optimization', 'QROM', 'Nonlinear Spectroscopy'],
         'publications_highlights': ['2026: QROM cost halving (lead author) -- latest Xanadu algorithm breakthrough', 'Quantum 2025: Nonlinear spectroscopy QC algorithm'],
         'h_index_estimate': '', 'papers': 10},

        {'name': 'Joseph Bowles', 'title': 'Quantum ML Researcher',
         'academic_background': {'highest_degree': 'PhD', 'field': 'Quantum Information / Quantum Foundations', 'institutions': [], 'graduation_year': ''},
         'previous_experience': [],
         'research_focus': ['Quantum ML', 'Quantum Self-Testing', 'Quantum Networks', 'Device-Independent Protocols'],
         'publications_highlights': ['45 papers, h-index 25, 3098 citations', 'Nature Physics 2023: Quantum network self-testing', '2025: 1000-qubit generative quantum ML'],
         'h_index_estimate': '25', 'papers': 7},

        {'name': 'Soran Jahangiri', 'title': 'Quantum Chemistry Researcher',
         'academic_background': {'highest_degree': 'PhD Computational Chemistry', 'field': 'Molecular Dynamics / Quantum Chemistry', 'institutions': ["Queen's University (Mosey group)"], 'graduation_year': ''},
         'previous_experience': [],
         'research_focus': ['Quantum Computational Chemistry', 'Molecular Vibronic Spectra', 'Variational Quantum Algorithms'],
         'publications_highlights': ['Nature 2021: nanophotonic chip co-author', 'PennyLane quantum chemistry module contributor'],
         'h_index_estimate': '', 'papers': 16},

        # ====== Advisors / Former Employees ======
        {'name': 'Seth Lloyd', 'title': 'Chief Scientific Advisor (External / MIT Professor)',
         'academic_background': {'highest_degree': 'PhD', 'field': 'Quantum Computing / Quantum ML', 'institutions': ['MIT (Professor, MechE + Physics)'], 'graduation_year': ''},
         'previous_experience': [],
         'research_focus': ['Quantum Computing', 'Quantum ML', 'Quantum Error Correction'],
         'publications_highlights': ['Founding figure in QC and QML', 'Xanadu patent co-inventor', 'PennyLane launch endorsement'],
         'h_index_estimate': '~80', 'papers': 6},

        {'name': 'Ish Dhand', 'title': 'Former Head of Architecture -> QC Design CEO',
         'academic_background': {'highest_degree': 'PhD', 'field': 'Quantum Information / QC', 'institutions': [], 'graduation_year': ''},
         'previous_experience': [{'company': 'Xanadu', 'role': 'Head of Architecture', 'years': '2019-2023'}, {'company': 'QC Design', 'role': 'CEO & Co-founder', 'years': '2023-present'}],
         'research_focus': ['Fault-Tolerant Photonic Architecture', 'Blueprint Paper', 'Quantum Advantage Path Design'],
         'publications_highlights': ['Quantum 2021: Blueprint paper (core co-author)', 'Led theoretical design of Xanadu FTQC roadmap'],
         'h_index_estimate': '', 'papers': 12},

        {'name': 'Nicolas Quesada', 'title': 'Former Lead Developer -> Polytechnique Montreal Professor',
         'academic_background': {'highest_degree': 'PhD Physics', 'field': 'Very Nonlinear Quantum Optics', 'institutions': ['University of Toronto (Vanier Scholar + Stoicheff Scholar)'], 'graduation_year': '2015'},
         'previous_experience': [{'company': 'Xanadu', 'role': 'Lead Developer (Strawberry Fields/The Walrus)', 'years': ''}, {'company': 'Polytechnique Montreal', 'role': 'Assoc. Prof / MEI Chair in Quantum Photonics / COPL Director', 'years': 'present'}],
         'research_focus': ['Gaussian Boson Sampling', 'Photonic Quantum Advantage', 'CV Quantum Optics'],
         'publications_highlights': ['Strawberry Fields + The Walrus lead developer', 'Led photonic quantum advantage theory validation'],
         'h_index_estimate': '', 'papers': 22},

        {'name': 'Daiqin Su', 'title': 'Former Research Scientist -> PolyU Hong Kong Professor',
         'academic_background': {'highest_degree': 'PhD Physics', 'field': 'Optical Quantum Computing', 'institutions': ['University of Queensland', 'USTC (BSc+MSc)'], 'graduation_year': '2017'},
         'previous_experience': [{'company': 'Xanadu', 'role': 'Research Scientist', 'years': '2017-2020'}, {'company': 'HUST (Wuhan)', 'role': 'Associate Professor', 'years': '2020-2025'}, {'company': 'PolyU Hong Kong', 'role': 'Assistant Professor (EEE)', 'years': '2025-present'}],
         'research_focus': ['Optical Quantum Computing', 'QEC (GKP/Cat Qubits)', 'Fault-Tolerant Photonic Architecture'],
         'publications_highlights': ['Nature 2021: nanophotonic chip co-author'],
         'h_index_estimate': '', 'papers': 13},

        {'name': 'Olivia Di Matteo', 'title': 'Former PennyLane Developer -> UBC Professor',
         'academic_background': {'highest_degree': 'PhD', 'field': 'Quantum Computing', 'institutions': [], 'graduation_year': ''},
         'previous_experience': [{'company': 'Xanadu', 'role': 'PennyLane Core Developer', 'years': ''}, {'company': 'UBC (ECE)', 'role': 'Professor / Catalyst collaboration', 'years': 'present'}],
         'research_focus': ['Differentiable Quantum Transforms', 'Quantum Software Compilation', 'PennyLane'],
         'publications_highlights': ['Differentiable Quantum Transforms (lead author, 2202.13414)', 'PennyLane Quantum Codebook author'],
         'h_index_estimate': '', 'papers': 5},

        {'name': 'Michael Vasmer', 'title': 'Former Sr. Quantum Architecture -> Inria Paris Faculty',
         'academic_background': {'highest_degree': 'PhD Quantum Computing', 'field': 'FTQC / 3D Surface Codes', 'institutions': ['University College London (Dan Browne group)', 'Durham University (Physics+CS, 1st Class)'], 'graduation_year': '2019'},
         'previous_experience': [{'company': 'Perimeter Institute + IQC', 'role': 'Joint Postdoc (Laflamme + Gottesman)', 'years': '2019-2021'}, {'company': 'Xanadu', 'role': 'QEC Researcher -> Sr. Quantum Architecture Scientist', 'years': '2021-2024'}, {'company': 'Inria Paris', 'role': 'Starting Faculty Position', 'years': '2025-present'}],
         'research_focus': ['Topological QEC', '3D Surface Codes', 'Fault-Tolerant Photonic Architecture'],
         'publications_highlights': ['PhD thesis: FTQC with 3D surface codes', 'Blueprint paper co-author', 'PRX Quantum 2024: Low-overhead weight-reduced codes'],
         'h_index_estimate': '', 'papers': 6},
    ],

    'total_funding_usd': 617000000,  # ~$535.5M股权 + $10M债务 + ~$71M政府拨款 = ~$617M（不含OPTIMISM谈判中$285M）
    'funding_history': [
        # ── 股权融资 ──
        {'date': '2017', 'round': 'Pre-Seed', 'amount_usd': 2500000, 'investors': ['未公开'], 'note': 'Weedbrook: "钱到账那天我以为那就是全世界的钱了"——独自一人、一张白皮书、$2.5M起步。'},
        {'date': '2018-05', 'round': 'Seed', 'amount_usd': 9000000, 'investors': ['OMERS Ventures', 'Golden Ventures', 'Real Ventures'], 'note': ''},
        {'date': '2019-06', 'round': 'Series A', 'amount_usd': 32000000, 'investors': ['OMERS Ventures(领投)', 'Georgian Partners', 'Radical Ventures', 'Real Ventures', 'Silicon Valley Bank', 'Tim Draper'], 'note': '注意: Bessemer尚未入局，2021年Series B才首次投资。'},
        {'date': '2021-05', 'round': 'Series B', 'amount_usd': 100000000, 'investors': ['Bessemer Venture Partners(领投)', 'Tiger Global Management', 'In-Q-Tel(CIA风投部门)', 'Capricorn Investment Group', 'BDC Capital', 'Georgian Partners', 'OMERS Ventures', 'Tim Draper'], 'note': 'Bessemer首次进入Xanadu即领投。估值~$400M。Bessemer在量子计算的第二笔投资(此前投了Rigetti)。'},
        {'date': '2022-11', 'round': 'Series C', 'amount_usd': 100000000, 'investors': ['Georgian(领投)', 'Porsche Automobil Holding SE', 'Bessemer Venture Partners', 'BDC Capital', 'Forward Ventures', 'Alumni Ventures', 'Pegasus Tech Ventures', 'Silicon Valley Bank($10M风险债务)'], 'note': '$90M股权+$10M SVB风险债务。估值$1B——加拿大首家量子独角兽。Porsche SE首次进入量子领域。'},
        {'date': '2025-11', 'round': 'SPAC合并公告', 'amount_usd': 0, 'investors': ['Crane Harbor Acquisition Corp.(SPAC, Nasdaq: CHAC)'], 'note': '2025年11月3日签署最终合并协议。Pre-money企业价值$3.0B，PIPE $275M。'},
        {'date': '2026-03', 'round': 'SPAC交割上市', 'amount_usd': 302000000, 'investors': ['AMD', 'BMO Global Asset Management', 'CIBC Asset Management', 'MMCAP Ventures', 'Planet First Partners', 'Polar Asset Management Partners'], 'note': '2026年3月26日交割，3月27日Nasdaq/TSX上市(XNDU)。PIPE $275M超额认购(90%+新投资者)+Trust $27M。全球首家纯光量子上市公司。'},
        # ── 政府拨款 & 可偿还贡献 ──
        {'date': '2019-11', 'round': 'DARPA Grant', 'amount_usd': None, 'investors': ['DARPA'], 'note': '量子机器学习在真实硬件上的性能测试。金额未公开。'},
        {'date': '2020-01', 'round': 'SDTC Grant', 'amount_usd': 4400000, 'investors': ['SDTC(加拿大可持续发展技术基金)'], 'note': '政府拨款(非稀释性)。'},
        {'date': '2023-01', 'round': 'SIF 可偿还贡献', 'amount_usd': 30000000, 'investors': ['加拿大联邦政府(ISED/SIF)'], 'note': 'CAD$40M(~$30M USD)。2025年9月修订工作说明与里程碑。部分资金用于建设$10M先进光子封装工厂。类型为可偿还贡献(非纯拨款)。'},
        {'date': '2024-02', 'round': 'FedDev Ontario 可偿还贡献', 'amount_usd': 2800000, 'investors': ['FedDev Ontario(加拿大南安省联邦经济发展署)'], 'note': 'CAD$3.75M(~$2.8M USD)。区域量子倡议(RQI)——国家量子战略一部分。用于PennyLane加速开发，创造22个量子岗位。可偿还贡献。'},
        {'date': '2025-12', 'round': 'CQCP Phase 1 Grant', 'amount_usd': 17000000, 'investors': ['ISED(Canada Quantum Champions Program)'], 'note': 'CAD$23M(~$17M USD)。Phase 1共$92M分给四家公司(Xanadu/Nord Quantique/Photonic/Anyon)。NRC独立技术评估。附带"总部必须在加拿大"条件。Weedbrook称此项目"超过DARPA Phase 1+2的总和"。'},
        {'date': '2025', 'round': 'DARPA QBI Stage B', 'amount_usd': 15000000, 'investors': ['DARPA'], 'note': '量子基准测试计划Stage B。潜在Phase C可达$316M。'},
        {'date': '2026-03', 'round': 'ARPA-E Grant', 'amount_usd': 2030000, 'investors': ['ARPA-E(美国能源部)'], 'note': '量子电池研究3年项目，与芝加哥大学合作。'},
        # ── 谈判中 ──
        {'date': '2026-03', 'round': 'Project OPTIMISM (谈判中)', 'amount_usd': 285000000, 'investors': ['加拿大联邦政府', '安大略省政府'], 'note': 'CAD$390M(~$285M USD)用于国内量子制造设施。尚未正式签署。⚠️ 谈判中，未计入total_funding_usd。'},
    ],

    'valuation_usd': 3100000000,

    'products': [
        {'name': 'Borealis', 'type': '光量子处理器', 'description': '216压缩态模式光量子处理器，时间复用架构，三维纠缠连接。2022年在Nature发表量子计算优势——36微秒完成高斯玻色采样，经典超算估计需9000年。全球首个云可访问的量子优势机器(Amazon Braket + Xanadu Cloud)。全动态可编程(1296实参数/每次运行)。', 'status': '商用(云端)', 'launch_date': '2022-06'},
        {'name': 'Aurora', 'type': '模块化通用光量子计算机', 'description': '全球首台模块化、网络化、可扩展光子量子计算机。12逻辑GKP量子比特，实时纠错解码。35光子芯片，13km光纤，4个服务器机柜。室温运行。Nature 2025同行评审发表。演示foliated distance-2 repetition code，86.4B模式簇态。', 'status': '验证中(云端可用)', 'launch_date': '2025-01'},
        {'name': 'PennyLane', 'type': '量子编程SDK', 'description': '全球#1量子编程平台——47%量子开发者使用。开源Python框架，支持量子可微编程。集成PyTorch/JAX/TensorFlow/NumPy。40+模拟器和硬件后端。35,000+活跃用户，~200K月下载量。150+大学合作(横跨33国)。已产生商业收入(VW, Mitsubishi, Rolls-Royce)。', 'status': '商用', 'launch_date': '2018'},
        {'name': 'Xanadu Cloud', 'type': '量子云平台', 'description': '云端访问Aurora和Borealis。Amazon Braket集成。支持混合量子-经典工作流。', 'status': '商用', 'launch_date': '2020'},
        {'name': 'PennyLane Lightning', 'type': '高性能模拟器', 'description': 'CPU/GPU/HPC模拟器。MPI扩展支持Frontier超算(Oak Ridge国家实验室)。161% YoY下载增长。', 'status': '商用', 'launch_date': '2021'},
        {'name': 'Catalyst', 'type': '编译工具', 'description': 'JIT/MLIR编译器，混合量子-经典程序编译优化。', 'status': '商用', 'launch_date': '2022'},
    ],

    'partnerships': [
        {'partner': 'AMD', 'date': '2025-2026', 'type': '战略投资+技术合作', 'description': 'PIPE参投$275M。混合量子-经典计算合作，FPGA加速流体力学模拟实现25x加速。'},
        {'partner': 'Lockheed Martin', 'date': '2026-02', 'type': '应用合作', 'description': '量子机器学习联合研究计划，聚焦航空航天与国防应用。已付款合作的商业合同。'},
        {'partner': 'DARPA QBI', 'date': '2025-2026', 'type': '政府验证', 'description': '入选量子基准测试计划Stage B，解锁$15M。潜在Phase C可达$316M。'},
        {'partner': '加拿大联邦政府 & 安大略省', 'date': '2026', 'type': '政府资助', 'description': '"Project OPTIMISM"——CAD$390M(~$285M)谈判中，用于国内量子制造设施。加拿大量子冠军计划额外CAD$23M。'},
        {'partner': 'ARPA-E (美国能源部)', 'date': '2026-03', 'type': '政府资助', 'description': '$2.03M电池研究资助，与芝加哥大学合作3年项目。'},
        {'partner': 'Thorlabs', 'date': '2026-01', 'type': '供应链', 'description': '联合开发定制光纤组件，用于相位/偏振稳定性。光量子计算供应链关键环节。'},
        {'partner': 'Tower Semiconductor / Corning / Applied Materials / EV Group', 'date': '2025-2026', 'type': '制造合作', 'description': '光量子芯片制造与封装生态系统。EV Group提供光子芯片键合，Tower/Corning/Applied Materials提供量产工艺。'},
        {'partner': 'TELUS', 'date': '2025', 'type': '应用合作', 'description': '电信商业化应用探索。'},
        {'partner': 'Fidelity Center for Applied Technology', 'date': '2025', 'type': '应用合作', 'description': '金融服务量子工作负载研发。'},
        {'partner': 'Mitsubishi Chemical / Rolls-Royce / Volkswagen', 'date': '2024-2025', 'type': '商业客户', 'description': 'PennyLane商业用户——材料科学、航空航天优化、汽车应用。已贡献商业收入。'},
        {'partner': 'Oak Ridge National Laboratory', 'date': '2025-2026', 'type': '研究合作', 'description': 'Frontier超算集成PennyLane Lightning(MPI扩展)。'},
        {'partner': 'University of Maryland (ARLIS)', 'date': '2026-03', 'type': '研究合作', 'description': '3年合作提升量子计算安全性，人才培养。'},
    ],

    'tech_milestones': [
        {'date': '2016', 'description': 'Christian Weedbrook独自创立Xanadu，种子轮$2.5M', 'significance': '唯一由理论物理学家独自创立、无硬件联合创始人的量子计算公司'},
        {'date': '2018', 'description': 'PennyLane发布', 'significance': '首个量子可微编程框架，后来成为全球量子开发者使用率#1的平台'},
        {'date': '2021', 'description': 'C轮$100M，估值$1B', 'significance': '加拿大首家量子独角兽'},
        {'date': '2022-06', 'description': 'Borealis在Nature发表量子计算优势', 'significance': '全球第三个实现量子优势的系统(继Google悬铃木、中科大九章之后)。首个云可访问的量子优势机器。加拿大首个量子优势。'},
        {'date': '2022-07', 'description': 'Borealis上线Amazon Braket和Xanadu Cloud', 'significance': '量子优势机器首次向公众开放云端使用'},
        {'date': '2025-01', 'description': 'Aurora在Nature发表——12逻辑GKP量子比特+实时纠错', 'significance': '全球首台模块化、网络化、可扩展光子量子计算机。验证光子路线的容错可行性。86.4B模式簇态。'},
        {'date': '2025-11', 'description': '宣布与Crane Harbor SPAC合并，估值$3.1B', 'significance': '全球首家纯光量子计算上市公司'},
        {'date': '2026-01', 'description': '任命CFO和CLO，加强公共市场运营能力', 'significance': '从创业公司向上市公司转型的标志性人事调整'},
        {'date': '2026-03', 'description': 'SPAC完成，Nasdaq/TSX上市交易(XNDU)', 'significance': '$302M总收益，$275M PIPE超额认购。AMD参投。'},
        {'date': '2026-03', 'description': '分析师日：公布量子数据中心路线图(2029-2030)', 'significance': '500逻辑量子比特目标，~$1B多伦多量子数据中心规划。QROM算法突破——Toffoli门数减半。'},
    ],

    'swot': {
        'strengths': [
            'PennyLane生态霸主: 47%量子开发者使用率，35,000+活跃用户，200K月下载。是量子软件领域最接近"行业标准"的产品，竞争对手难以复制其网络效应',
            '光子路线天然优势: 室温运行(无需稀释制冷机)、光纤网络化原生能力、与半导体Fab工艺兼容。制造和部署成本理论上远低于超导/离子阱',
            '资本市场先发优势: 全球首家纯光量子上市公司(Nasdaq/TSX: XNDU)，$302M SPAC收益+$272.5M现金，品牌可见度远超私有光量子对手',
            '硬件+软件垂直整合: 从PennyLane(软件)到Aurora(硬件)到Xanadu Cloud(服务)全栈覆盖，商业变现路径多元',
            'Nature双发: Borealis(2022)+Aurora(2025)均经Nature同行评审，学术信用极高',
            '董事会战略性构建: Glenda Dorchak(GlobalFoundries董事)、Heidi Shyu(前美国国防部副部长)、Eliot Pence(Anduril)——半导体制造+国防+深度科技三重复合',
        ],
        'weaknesses': [
            '收入几乎为零: FY2025营收$4.6M，Q1 2026 $2.83M。vs $4.1B市值=700x+市销率，在所有量子上市公司中估值最极端',
            '深亏烧钱: FY2025净亏损$70.7M，Q1 2026经营费用$26.1M vs 收入$2.83M。现金跑道约2-3年',
            '创始人单枪匹马: Weedbrook独自创立，理论背景，无硬件联合创始人。与PsiQuantum(4位创始人含CTO/CSO)和IonQ(Chris Monroe+Jungsang Kim双院士)相比，创始团队技术深度不足',
            '光子门概率性本质: 光子量子门天然概率性，虽通过测量基反馈可克服，但相比超导/离子阱的确定性门存在根本性劣势',
            '无NISQ商业变现: 不提供NISQ阶段的量子计算服务(Borealis GBS无已知实际应用)，在FTQC实现前缺少中间收入来源',
            '稀释悬空: 294M股注册转售，62%股价下跌，锁定到期2026年9月。接近300M股的潜在抛压',
        ],
        'opportunities': [
            '量子数据中心先行者: 若2029-2030年交付500逻辑量子比特的量子数据中心，将定义"量子计算即基础设施"的新范式——对标AWS在云计算早期的角色',
            '加拿大国家量子战略深度绑定: CAD$390M OPTIMISM谈判+CAD$23M冠军计划，加拿大可能将Xanadu包装为国家级冠军企业(类似荷兰ASML)',
            '光子量子网络: 光子是量子互联网的唯一物理载体。Xanadu若将量子计算+量子通信整合，可开辟独立于纯计算的TAM',
            'AMD/NVIDIA生态融合: AMD已参投PIPE，量子-HPC混合计算可能创造新的工作负载范式',
            'M&A目标: 若技术验证成功但独立商业化困难，AMD/NVIDIA/ hyperscaler 可能溢价收购',
            'DARPA QBI Phase C: 若通过，$316M级别资金+美国政府最高级别技术背书',
        ],
        'threats': [
            'IonQ商业碾压: $64.7M Q1营收(755% YoY)，$470M backlog，2026年展望$260-270M。Xanadu的$2.83M vs IonQ的$64.7M——差距23倍且在扩大',
            'PsiQuantum规模威胁: $4.7B+融资($2B+股权)，GlobalFoundries硅光子量产路径，澳大利亚$620M+芝加哥$500M两大基地。若PsiQuantum IPO，可能吸走光量子赛道的资本关注',
            '光量子赛道拥挤: Quandela(法国)、ORCA(英国)、QuiX(荷兰)——都在光量子领域竞争。Xanadu没有像PsiQuantum那样的制造护城河(GF独家合作)',
            '估值难以维系: 700x+市销率在利率正常化时代难以长期支撑。若科技股回调，Xanadu融资成本将急剧上升',
            'FTQC时间表风险: 2028年容错操作、2029-2030年量子数据中心——任何延迟都可能被资本市场严厉惩罚(已是上市公司)',
            '人才竞争: Google/IBM/QuEra/IonQ都在加拿大设量子实验室，多伦多-滑铁卢量子走廊人才争夺白热化',
        ],
    },

    'competitive_positioning': (
        'Xanadu是全球首家也是唯一一家纯光量子计算上市公司(Nasdaq/TSX: XNDU)，定位在"量子计算的软件+硬件双平台"。'
        '与PsiQuantum(硅光子+半导体Fab路径)不同，Xanadu采用连续变量(CV)光子路线+时间复用架构，结合GKP编码实现量子纠错。'
        '其核心竞争优势不在硬件制造规模(PsiQuantum领先)，而在软件生态：PennyLane是量子开发者使用率#1的平台(47%)，远超IBM Qiskit和Google Cirq。'
        'Xanadu的战略本质是"量子时代的Red Hat"——用开源软件生态锁定开发者，再通过云服务和硬件变现。'
        '上市后，Xanadu面临双重压力：硬件上需要证明CV光子路线可以规模化到容错量子计算(2028年目标)，商业上需要证明PennyLane生态能转化为真实营收(当前软件收入极低)。'
        '与IonQ(聚焦NISQ商业应用，营收$130M+)和PsiQuantum(跳过NISQ直奔FTQC，融资$4.7B+)相比，Xanadu在两者之间：硬件定位不如PsiQuantum极致，商业落地不如IonQ实际。'
        '其最大价值可能不在于独立成功，而在于：如果光子路线被验证为量子计算的正确路径，Xanadu的PennyLane软件生态+光子硬件知识产权组合将成为任何想进入量子计算的大型科技公司的理想收购标的。'
    ),

    'latest_summary': (
        '2026年3月27日，Xanadu通过SPAC合并(Crane Harbor Acquisition Corp.)在Nasdaq和TSX上市，成为全球首家纯光量子计算上市公司，企业价值约$3.1B。'
        'SPAC总收益$302M(含$275M超额认购PIPE)，AMD作为战略投资者参投。'
        '公司同时宣布与加拿大联邦政府/安大略省政府谈判CAD$390M(~$285M)"Project OPTIMISM"量子制造资助。'
        '硬件方面，Aurora(Nature 2025)——全球首台模块化网络化光子量子计算机(12逻辑GKP量子比特)——已在Xanadu Cloud可用。'
        '软件方面，PennyLane达到200K月下载量，47%量子开发者使用率，150+大学合作。'
        '2026年分析师日公布量子数据中心路线图：2026-2027年量子比特工厂(多伦多)，2028年容错操作，2029-2030年500逻辑量子比特数据中心(约$1B投资)。'
        'Q1 2026营收$2.83M(+304% YoY)，净亏损$20.6M，现金$272.5M。'
    ),

    'profile_status': 'complete',
    'last_researched': '2026-07-14',
}

profile_id = upsert_profile(conn, profile)
print(f'Profile created: id={profile_id}')
print(f'Funding: ${profile["total_funding_usd"]/1e6:.0f}M')
print(f'Valuation: ${profile["valuation_usd"]/1e9:.1f}B')
print(f'Products: {len(profile["products"])}')
print(f'Partnerships: {len(profile["partnerships"])}')
print(f'Milestones: {len(profile["tech_milestones"])}')
print(f'SWOT: S={len(profile["swot"]["strengths"])} W={len(profile["swot"]["weaknesses"])} O={len(profile["swot"]["opportunities"])} T={len(profile["swot"]["threats"])}')

conn.close()
