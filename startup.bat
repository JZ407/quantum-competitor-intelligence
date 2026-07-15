@echo off
chcp 65001 >nul
echo ============================================
echo   量子科技情报平台 — 启动流程
echo ============================================
echo.

REM ── 1. MySQL ──────────────────────────────
echo [1/3] MySQL 8.4 ...
netstat -ano | findstr ":3306.*LISTENING" >nul
if %errorlevel%==0 (
    echo   MySQL 已在运行
) else (
    echo   启动 MySQL ...
    start "" "C:/Program Files/MySQL/MySQL Server 8.4/bin/mysqld.exe" --defaults-file="D:/Claude_code/liangke_daily/config/my.ini"
    REM 等待 MySQL 就绪（最多 15 秒）
    for /L %%i in (1,1,15) do (
        timeout /t 1 /nobreak >nul
        "C:/Python314/python" -c "import pymysql; pymysql.connect(host='127.0.0.1', user='scraper', password='scraper123', database='liangke_scraper').close()" >nul 2>&1
        if !errorlevel!==0 goto mysql_ready
        echo   等待 MySQL ... %%i/15
    )
    echo   [FAIL] MySQL 启动超时
    exit /b 1
)
:mysql_ready
echo   MySQL OK
echo.

REM ── 2. 清理残留 Streamlit ────────────────
echo [2/3] 清理残留进程 ...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8501.*LISTENING" 2^>nul') do (
    taskkill //F //PID %%a >nul 2>&1
    echo   已终止 PID %%a
)
timeout /t 2 /nobreak >nul
echo   清理完成
echo.

REM ── 3. 启动 Streamlit ─────────────────────
echo [3/3] 启动 Streamlit ...
cd /d D:/Claude_code/rag_system
start "" C:/Python314/python -B -m streamlit run examples/daily_report_app.py --server.address 0.0.0.0 --server.port 8501 --server.headless true
timeout /t 5 /nobreak >nul

REM 验证
netstat -ano | findstr ":8501.*LISTENING" >nul
if %errorlevel%==0 (
    echo   Streamlit OK: http://localhost:8501
) else (
    echo   [WARN] Streamlit 可能还在启动，稍等几秒
)
echo.
echo ============================================
echo   启动完成
echo ============================================
start http://localhost:8501
