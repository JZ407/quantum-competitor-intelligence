# 日常操作手册

## 每天早上

### 1. 一键启动平台
```
对 Claude 说: "启动" 或 "启动平台"
→ 自动执行: MySQL 就绪检查 → 清理僵尸 Streamlit → 启动 Streamlit → 打开浏览器
```
脚本: `D:/Claude_code/startup.ps1`

### 2. 更新量科网 Cookie（每周一/如过期）
```
报错特征: "Cookie expired — 参考来源指向登录页"
操作: 浏览器登录 www.qtc.com.cn → F12 → Network → 任意请求 → Copy Cookie header
      粘贴到 D:/Claude_code/liangke_daily/cookies.txt
      同步运行 python extract_cookie.py 更新 pickle 文件
```

### 3. 每日抓取 量科网
```bash
cd D:/Claude_code/liangke_daily/core
C:/Python314/python.exe scrape_daily.py
```

---

## 周期任务（2-3 天一次）

### 5. 投融资 websearch
```
对 Claude 说: "进行一次投融资websearch"
→ 自动执行 7 组 query，返回新事件
→ 验证 URL → 入库 → 刷新看板
```

### 6. 机构新闻抓取
```bash
cd D:/Claude_code/institution_news
C:/Python314/python.exe run_all.py
# 注意: Google Research 跳过了论文 LLM 翻译（改动在 sources/google_quantum_research.py 第 132 行）
```

---

## 代码变更后

### 7. 重启 Streamlit（关键步骤！）
```bash
# 必须做全流程，否则修改不生效：
taskkill //F //IM streamlit.exe
taskkill //F //IM python.exe
find D:/Claude_code -type d -name "__pycache__" -exec rm -rf {} +
cd D:/Claude_code/rag_system
C:/Python314/python.exe -B -m streamlit run examples/daily_report_app.py ...
# 浏览器: Ctrl+Shift+R
```

### 8. Git 提交
```bash
# 子模块优先
cd D:/Claude_code/liangke_daily && git add -A && git commit -m "fix: 描述具体改动"
cd D:/Claude_code/rag_system && git add -A && git commit -m "feat: 描述具体改动"
# ... 其他子模块同理

# 主仓库最后
cd D:/Claude_code && git add -A && git commit -m "feat: 一个主题一句话"

# 推送所有
cd D:/Claude_code && git push origin master
cd D:/Claude_code/rag_system && git push origin master
# ... 其他子模块同理
```

---

## 故障排查

| 现象 | 原因 | 修复 |
|------|------|------|
| Streamlit 报 MySQL 连接错误 | MySQL 未启动 | 执行步骤 1 |
| 抓取报 Cookie expired | Cookie 过期 | 执行步骤 2 |
| 看板修改不生效 | __pycache__ 缓存 | 执行步骤 7 |
| 看板数字异常 | 历史库误标 / 估值混淆 | 参考 `memory/feedback_*.md` |
| 投融资总额异常大 | 参考 `feedback_funding_tagger_amount.md` | 跑 SQL 查 >5亿事件 |
| 知识库搜不到新文档 | 索引未更新 | `build_kb.py --config config_pro.yaml --incremental` |

---

## 数据库速查

| 库 | 位置 | 用途 |
|----|------|------|
| liangke_scraper | MySQL 127.0.0.1:3306 | 每日抓取 + websearch |
| historical_final.db | liangke_historical/ | 历史归档 |
| institutions.db | institution_news/ | 海外机构新闻 + QuEra |
| profiles.db | competitor_profiles/ | 竞争对手档案 |
| conferences.db | conference_db/ | 量子会议 |
