@echo off
chcp 65001 >nul
echo 正在停止所有退換貨風控系統服務...
taskkill /F /IM streamlit.exe >nul 2>&1
echo ✅ 已成功停止所有 Streamlit 伺服器服務！
pause
