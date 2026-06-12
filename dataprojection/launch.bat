@echo off
echo ============================================
echo   Data Projection - 对话式数据探索平台
echo ============================================
echo.

cd /d %~dp0

echo [1/2] 检查依赖...
pip install -r requirements.txt -q

echo [2/2] 启动 Streamlit...
echo.
echo 浏览器将自动打开 http://localhost:8501
echo 按 Ctrl+C 停止服务
echo.

python -m streamlit run app.py --server.port 8503 --server.address 0.0.0.0

pause
