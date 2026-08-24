# Quantum Intel Platform Backup
# 一键打包所有 git 之外的数据文件 + MySQL dump，产出可迁移的 zip。
# 用法: powershell -ExecutionPolicy Bypass -File backup.ps1
# PS5.1 解析怪癖：param 块内禁止行尾注释，默认值后禁止跟逗号（否则路径变 "backups False False"）
# SkipMysql: MySQL 未运行或无需 dump 时跳过；SkipMemory: 不含 Claude 会话记忆
param(
      [string]$OutDir = "D:/Claude_code/archive/backups"
    , [switch]$SkipMysql
    , [switch]$SkipMemory
)

$ErrorActionPreference = "Continue"
$ts = Get-Date -Format "yyyyMMdd_HHmmss"
$stamp = "quantum_intel_backup_$ts"
$stage = Join-Path $env:TEMP $stamp
$zip = Join-Path $OutDir "$stamp.zip"
$ROOT = $PSScriptRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Quantum Intel Backup -> $zip" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# ── 数据文件清单（git 之外的一切） ──
$files = @(
    "liangke_historical/historical_final.db",     # 历史库唯一真源
    "institution_news/institutions.db",           # 机构新闻
    "competitor_profiles/profiles.db",            # 竞对档案
    "conference_db/conferences.db",               # 会议库
    "lit-review/data/literature.db",              # 文献库
    "dataprojection/data/dataprojection.db",      # 数据投影
    "knowledge_graph/knowledge_graph.json",       # 知识图谱
    "dataprojection/.env"                         # LLM key 环境变量
)
$dirs = @(
    "rag_system/data", "rag_system/data_all", "rag_system/data_pro",
    "rag_system/data_en", "rag_system/data_lite",  # RAG 语料
    "rag_system/index", "rag_system/index_en",
    "rag_system/index_lite", "rag_system/index_pro" # RAG 向量索引
)

New-Item -ItemType Directory -Force -Path "$stage/databases", "$stage/rag_corpus", "$stage/rag_indexes", $OutDir | Out-Null

$ok = 0
$total = $files.Count + $dirs.Count + $(if ($SkipMysql) { 0 } else { 1 }) + $(if ($SkipMemory) { 0 } else { 1 })

# ── 1. SQLite / 小文件 ──
Write-Host "[1/$total] 拷贝数据文件 ..." -ForegroundColor Yellow
foreach ($f in $files) {
    $src = Join-Path $ROOT $f
    $dst = Join-Path $stage "databases/$(Split-Path $f -Leaf)"
    if (Test-Path $src) {
        if ((Get-Item $src).PSIsContainer) { Copy-Item -Recurse $src $dst -ErrorAction Stop }
        else { Copy-Item $src $dst -ErrorAction Stop }
        Write-Host "  OK  $f" -ForegroundColor Green
        $ok++
    } else {
        Write-Host "  [SKIP] 不存在: $f" -ForegroundColor Yellow
    }
}

# ── 2. RAG 语料 ──
Write-Host "[$($ok+1)/$total] 拷贝 RAG 语料 (data*) ..." -ForegroundColor Yellow
foreach ($d in $dirs) {
    $src = Join-Path $ROOT $d
    if (Test-Path $src) {
        if ($d -match "^rag_system/data") {
            Copy-Item -Recurse $src (Join-Path $stage "rag_corpus/$(Split-Path $d -Leaf)") -ErrorAction Stop
        } else {
            Copy-Item -Recurse $src (Join-Path $stage "rag_indexes/$(Split-Path $d -Leaf)") -ErrorAction Stop
        }
        Write-Host "  OK  $d" -ForegroundColor Green
        $ok++
    } else {
        Write-Host "  [SKIP] 不存在: $d" -ForegroundColor Yellow
    }
}

# ── 3. MySQL dump ──
if ($SkipMysql) {
    Write-Host "[$($ok+1)/$total] [SKIP] MySQL dump" -ForegroundColor Yellow
} else {
    Write-Host "[$($ok+1)/$total] MySQL dump (liangke_scraper) ..." -ForegroundColor Yellow
    $dump = "C:/Program Files/MySQL/MySQL Server 8.4/bin/mysqldump.exe"
    if (Test-Path $dump) {
        & $dump -h 127.0.0.1 -u scraper -pscraper123 --single-transaction --routines liangke_scraper 2>$null |
            Out-File -Encoding utf8 (Join-Path $stage "databases/liangke_scraper_mysql_dump.sql")
        if ($LASTEXITCODE -eq 0) {
            $sizeMB = [math]::Round((Get-Item (Join-Path $stage "databases/liangke_scraper_mysql_dump.sql")).Length / 1MB, 1)
            Write-Host "  OK  liangke_scraper -> dump.sql ($sizeMB MB)" -ForegroundColor Green
            $ok++
        } else {
            Write-Host "  [FAIL] mysqldump 退出码 $LASTEXITCODE（检查 MySQL 是否运行/权限）" -ForegroundColor Red
        }
    } else {
        Write-Host "  [SKIP] 未找到 mysqldump.exe" -ForegroundColor Yellow
    }
}

# ── 4. Claude 会话记忆（AI 接手关键上下文） ──
if (-not $SkipMemory) {
    $mem = "C:/Users/zhouj/.claude/projects/D--Claude-code/memory"
    if (Test-Path $mem) {
        Copy-Item -Recurse $mem (Join-Path $stage "memory") -ErrorAction Stop
        Write-Host "  OK  Claude 会话记忆 memory/" -ForegroundColor Green
        $ok++
    } else {
        Write-Host "  [SKIP] 记忆目录不存在: $mem" -ForegroundColor Yellow
    }
}

# ── 5. 打包 ──
Write-Host "[打包] $zip ..." -ForegroundColor Yellow
# 注意：必须用绝对路径调用 Windows 原生 bsdtar——从 Git Bash 启动时
# PATH 里的 msys tar 会把 "D:/" 误认为远程主机而失败。
$tar = "C:/Windows/System32/tar.exe"
if (Test-Path $tar) {
    Push-Location (Split-Path $stage)
    & $tar -a -c -f $zip (Split-Path $stage -Leaf) 2>$null
    Pop-Location
} else {
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::CreateFromDirectory($stage, $zip)
}

if (Test-Path $zip) {
    $zipMB = [math]::Round((Get-Item $zip).Length / 1MB, 1)
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  BACKUP OK: $zip ($zipMB MB)" -ForegroundColor Green
    Write-Host "  $ok/$total 项已包含" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
} else {
    Write-Host "[FAIL] 打包失败，暂存目录: $stage" -ForegroundColor Red
    exit 1
}

# 清理暂存
Remove-Item -Recurse -Force $stage -ErrorAction SilentlyContinue
