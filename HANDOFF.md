# 量子科技情报平台 — 项目接手指南 / 迁移计划

> 本文档面向接手的开发者或 AI 模型：读完即可理解项目全貌、启动环境并继续日常运营。
> 最后更新：2026-08-24（修订：仓库拓扑修正为 6 个；dataprojection 标注废弃）。配套文档：`ARCHITECTURE.md`（架构图）、`SOP.md`（日常操作）、各子仓库 `README.md`。

---

## 1. 项目一句话定位

**量子科技情报聚合 + 分析平台**：从量科网、16 家海外量子机构、投融资 WebSearch 三条线采集数据，存入 MySQL + SQLite 双库，经 RAG 与 LLM 打标，统一呈现于 **Streamlit 看板（http://localhost:8501）**——包含每日资讯、投融资看板、竞对档案、会议信息、知识图谱、周报生成 6 大板块。

## 2. 运行环境

| 项 | 值 |
|----|----|
| OS | Windows 11 Home China（Git Bash 为默认 shell） |
| Python | **3.14**，位于 `C:/Python314/python.exe`（所有脚本用它） |
| 数据库 | MySQL 8.4（`C:/Program Files/MySQL/MySQL Server 8.4`），配置 `liangke_daily/config/my.ini` |
| 浏览器 | Edge（Cookie 提取走 CDP 端口 9222） |
| 关键环境变量 | `DEEPSEEK_API_KEY_LOCALUSE`（看板 LLM / 周报 共用） |
| 备份 | OneDrive，由 `liangke_daily/core/sync_to_onedrive.py` 同步 `historical_final.db` |

> ⚠️ 环境变量命名坑：会话内使用 `DEEPSEEK_API_KEY_LOCALUSE`，与 Claude Code 自己的 token 相互独立，不要写成 `DEEPSEEK_API_KEY`。

## 3. Git 仓库拓扑（重要）

**6 个独立 GitHub 仓库，全部属主 `JZ407`**，路径固定不可改（脚本硬编码 `D:/Claude_code/...` 绝对路径）：

| 目录 | 远程仓库 | 角色 |
|------|---------|------|
| `D:/Claude_code`（根） | `JZ407/quantum-competitor-intelligence` | 编排 + 竞对档案 |
| `liangke_daily/` | `JZ407/liangke-daily-scraper` | 每日抓取 + MySQL ORM + 投融资 |
| `liangke_historical/` | `JZ407/liangke-historical` | 历史库脚本 |
| `rag_system/` | `JZ407/quantum-intelligence-platform` | 看板 + RAG + 周报 |
| `knowledge_graph/` | `JZ407/quantum-knowledge-graph` | 知识图谱 |
| `institution_news/` | `JZ407/quantum-institution-crawlers` | 机构新闻爬虫 |

> ⚠️ `dataprojection/`（数镜 DataMirror）**已废弃**，不属于维护范围；`dataprojection.db` 保留在备份中仅供归档，不要再启动 `dataprojection/app.py`。

**⚠️ 子模块警告**：根仓库的 index 记录了 5 个 gitlink（`git status` 中显示为 `m`），但**没有 `.gitmodules` 文件**。因此 `git clone` 根仓库**不会自动拉子模块**——接手时必须手动 `git clone` 5 个子仓库到上述对应目录。数据文件（`*.db`、`*.pkl`、`cookies.txt`）均在 `.gitignore` 中，**不随 git 走**，需从备份/OneDrive 或重新生成恢复。

**提交约定**：子模块先提交 → 根仓库最后提交（更新 gitlink 指针）；提交信息用 `类型: 中文描述` 格式（feat/fix/chore/docs）；每个 commit 附 `Co-Authored-By: Claude <noreply@anthropic.com>`。

## 4. 数据库地图（2026-08-24 快照）

| 库 | 位置 | 数据 | 写入方 | 读取方 |
|----|------|------|--------|--------|
| `liangke_scraper` (MySQL) | 127.0.0.1:3306，user=`scraper`（密码走环境变量 `LIANGKE_MYSQL_PASSWORD`） | articles **2,769**（page_type: reference/flash/article/websearch） | `scrape_daily.py` + websearch 入库脚本 | 看板 |
| `historical_final.db` | `liangke_historical/` | articles **11,582**（**唯一历史真源**） | `sync_ws_to_final.py`、`merge_v2_v3.py` | 看板、知识图谱、导出 |
| `institutions.db` | `institution_news/` | articles **3,740** + quera_articles 582 | `run_all.py` | 看板 |
| `profiles.db` | `competitor_profiles/` | 4 档案 / 173 来源 / 345 论文 | 档案建设脚本 | `render.py` → HTML |
| `conferences.db` | `conference_db/` | conferences 211 | conf_fetcher | 看板 |
| `literature.db` | `lit-review/data/` | 22 论文 / 223 作者 | 文献笔记流程 | 文献综述 |
| `resources.db` | `rag_system/data/` | reports 10 | 专题简报入库 | RAG |
| ~~`dataprojection.db`~~ | ~~`dataprojection/data/`~~ | ~~对话会话~~ | ~~dataprojection app~~ | ~~自身~~ |

**架构要点**：投融资看板是**双库架构**——同时查 MySQL（tags.funding 结构化）和 SQLite final（tags LIKE '%融资%'），`pd.concat` 后按 公司+轮次+年 去重，标题黑名单过滤股市/财报/资助类误标。

> ⚠️ 历史教训（2026-06-23 修复）：曾存在 `historical.db` 空壳被 6 个脚本引用、而数据在 `historical_final.db` 的分裂状态。**已统一**：全项目唯一历史库路径 = `historical_final.db`；final 表补齐了 `list_scraped_at`/`detail_fetched_at`/`fetch_status` 三列以兼容 ORM。接手后如再看到 `historical.db`（不带 final）字样即为回归 bug。

## 5. 数据管线

```
① 量科网每日  scrape_daily.py ──→ MySQL (page_type != websearch)
② 投融资      WebSearch Agent ──→ ingest_websearch_*.py ──→ MySQL (page_type='websearch')
                                                        └─→ sync_ws_to_final.py ──→ final.db
③ 机构新闻    run_all.py (16 家机构) ──→ institutions.db（QuEra 走 Playwright）
④ 历史归档    merge_v2_v3.py（一次性）──→ historical_final.db
⑤ 展示        daily_report_app.py 读 ①+②+③+④+会议库+档案库
```

## 6. 启动与日常操作

```powershell
# 一键启动（幂等：MySQL 检查→僵尸 Streamlit 清理→启动→开浏览器）
powershell -ExecutionPolicy Bypass -File D:/Claude_code/startup.ps1
```

- 服务清单由 `services.json` 驱动（数据驱动设计：新增服务只改此文件）
- 已知现象：Dashboard 的 `wait_seconds` 报 Timeout 常为误报（Streamlit 首次编译慢），稍后端口 8501 就绪即正常
- 每日抓取：`cd liangke_daily/core && C:/Python314/python.exe scrape_daily.py`
- **修改看板代码后必须**：`taskkill //F //IM python.exe` → 清 `__pycache__` → 重启 streamlit → 浏览器 Ctrl+Shift+R（否则改动不生效）

### 定时任务（Windows Task Scheduler）

| 任务 | 状态 | 时间 |
|------|------|------|
| `Quantum_DailyScrape`（量科每日抓取） | ✅ 运行中 | 每日 13:00 |
| `Quantum_InstCrawl`（机构新闻） | ✅ 运行中 | 每日 13:01 |
| `QuantumKG_AutoBuild`（知识图谱） | ❌ 已关闭 | —（注册脚本 `knowledge_graph/setup_schedule.ps1`） |

## 7. Cookie 机制（高频操作）

量科网会话 Cookie 有 **3 个同步位置**，优先级：`liangke_daily/cookies.txt`（手动粘贴，最高） > `liangke_daily/data/cookies/qtc_cookies.pkl`（CDP 提取） > `liangke_historical/qtc_cookies.pkl`（由 `update_cookie.bat` 复制）。更新流程：

1. Edge 登录 www.qtc.com.cn → F12 Network → 复制 Cookie header → 粘贴进 `cookies.txt`
2. 跑 `python liangke_daily/core/extract_cookie.py`（CDP 9222 自动提取，需 Edge）或手动同步 pickle
3. `check_cookie.py` 校验（exit 0 = OK）
4. Cookie 文件全部 gitignore，**不入库**

## 8. 历史坑位清单（接手必读）

| 坑 | 一句话 |
|----|--------|
| Kimi k2.6 temperature | 只接受 `1` 或省略，其他值报错 |
| Moonshot 域名 | `.cn` 与 `.ai` 的 API Key 绑定不同，别混用 |
| 禁止编造 URL | WebSearch 入库必须用搜索返回的原始链接，逐条 WebFetch 验证（AI 摘要糅合多结果，不可信） |
| 估值/金额混淆 | tagger 常把估值当融资额，入库需人工核对 >5 亿事件 |
| 历史库误标 | 股市/财报/资助类新闻会被误标为融资，需人工审核 |
| 「出资×基金」误标轮次 | 跨 title/content 正则匹配会把 A 轮误标成「基金」 |
| Streamlit 缓存 | 改 render.py 不生效 = 没清 `__pycache__` + 没硬刷新 |
| 历史库路径分裂 | 所有脚本必须指向 `historical_final.db`（见 §4） |

## 9. 完整迁移流程（模型可照此直接执行）

> 迁移 = 代码走 git、数据走 zip、凭证走手工。执行者（人或模型）需要：能敲命令的新机器 + GitHub 推送权限 + `DEEPSEEK_API_KEY_LOCALUSE` 的值 + 量科网账号（真人登录一次）。

### 9a. 旧机器（出发端）

```powershell
# 1. 代码推送到 GitHub（5 个仓库，子模块先推）
cd D:/Claude_code/liangke_daily && git push origin master   # 其他 3 个子仓库同理
cd D:/Claude_code && git push origin master

# 2. 数据打包（约 180MB 一个 zip，含 MySQL dump + RAG 索引 + AI 会话记忆）
powershell -ExecutionPolicy Bypass -File D:/Claude_code/backup.ps1
#    产物: D:/Claude_code/archive/backups/quantum_intel_backup_<时间戳>.zip

# 3. 把 zip 传给新机器（OneDrive / U盘 / 局域网，任意方式）
```

### 9b. 新机器（接收端）

```bash
# 1. 装环境: Python 3.14 + MySQL 8.4 + Edge 浏览器

# 2. 拉代码（根仓库不含子模块，必须手动 clone 全部 6 个）
git clone https://github.com/JZ407/quantum-competitor-intelligence.git D:/Claude_code
git clone https://github.com/JZ407/liangke-daily-scraper.git    D:/Claude_code/liangke_daily
git clone https://github.com/JZ407/liangke-historical.git       D:/Claude_code/liangke_historical
git clone https://github.com/JZ407/quantum-intelligence-platform.git D:/Claude_code/rag_system
git clone https://github.com/JZ407/quantum-knowledge-graph.git  D:/Claude_code/knowledge_graph
git clone https://github.com/JZ407/quantum-institution-crawlers.git D:/Claude_code/institution_news

# 3. 解压 zip 并放回原位
#    databases/*.db → 对应项目目录（historical_final.db 是最关键的）
#    rag_corpus/* → rag_system/data*; rag_indexes/* → rag_system/index*
#    memory/ → C:\Users\<用户>\.claude\projects\D--Claude-code\memory\（AI 接手时）

# 4. 恢复 MySQL（二选一：导 dump 或直接复制 datadir）
mysql -u root -p -e "CREATE DATABASE liangke_scraper; CREATE USER 'scraper'@'localhost' IDENTIFIED BY '<LIANGKE_MYSQL_PASSWORD 的值>'; GRANT ALL ON liangke_scraper.* TO 'scraper'@'localhost';"
mysql -u scraper -p%LIANGKE_MYSQL_PASSWORD% liangke_scraper < databases/liangke_scraper_mysql_dump.sql

# 5. 装依赖 + 设环境变量（torch/faiss/sentence-transformers 在 3.14 有成功记录）
pip install -r 各仓库/requirements.txt
setx DEEPSEEK_API_KEY_LOCALUSE "<key>"

# 6. 注册定时任务（每日抓取 13:00 / 机构爬虫 13:01）
powershell -File D:/Claude_code/liangke_daily/setup_schedule.ps1
powershell -File D:/Claude_code/institution_news/setup_schedule.ps1

# 7. 启动
powershell -ExecutionPolicy Bypass -File D:/Claude_code/startup.ps1
```

### 9c. 验收清单（4 项全过 = 迁移完成）

| 检查 | 命令 | 期望 |
|------|------|------|
| 看板存活 | `curl http://localhost:8501/_stcore/health` | `ok` |
| Cookie 有效 | `cd liangke_daily && python core/check_cookie.py` | `COOKIE_OK`（先真人登录量科网提取，见 §7） |
| 历史库完整 | 看板显示 ~11,582 篇历史 + ~2,769 篇每日 | 数字对得上 |
| 抓取可用 | `cd liangke_daily/core && python scrape_daily.py` | 无报错入库 |

### 9d. 三个不能靠文件传递的东西

1. **Cookie** — 会过期，新机器必须重新登录 www.qtc.com.cn 提取
2. **环境变量** — `DEEPSEEK_API_KEY_LOCALUSE` 需手动设置
3. **定时任务** — Windows Task Scheduler 注册不随文件走，需重跑 `setup_schedule.ps1`

## 10. 当前工作进度与下一步

- 已完成：投融资 websearch 覆盖 2023-2026（~30 独立事件已入库审计）；QuEra/PsiQuantum/Xanadu/Algorithmiq 竞对档案；周报第 193 期；历史库路径统一。
- 进行中：投融资增量搜索（2-3 天一轮）、周报人工标签双轨、竞对档案扩展。
- 待办：统一标签中间层（jieba+词典方案已规划未实施，见 `memory/project_tagging_strategy.md`）。

## 11. 快速定位表

| 要做什么 | 去哪 |
|---------|------|
| 看板主入口 | `rag_system/examples/daily_report_app.py` |
| 改服务清单 | `services.json` |
| 加新的每日数据源 | `liangke_daily/core/scrape_daily.py` + services.json |
| 加机构 | `institution_news/sources/` + `run_all.py` |
| 竞对档案 schema | `competitor_profiles/schema.py` |
| 投融资词典 | `liangke_daily/core/funding_dict.py` |
| 周报模板 | `rag_system/weekly_templates/` |
| 会话级经验记忆 | `C:/Users/zhouj/.claude/projects/D--Claude-code/memory/*.md` |
