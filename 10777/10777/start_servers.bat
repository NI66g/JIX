@echo off
chcp 65001 >nul
title 電腦周邊退換貨風控系統 - 服務啟動器

echo ========================================================
echo   電腦周邊智慧退換貨與爭議風控系統 (前後台雙服務)
echo ========================================================
echo.
echo [1/2] 正在啟動 商家管理後台 (Port 8501)...
start "周邊風控管理後台 - Admin (8501)" cmd /k "streamlit run app.py --server.port 8501"

echo [2/2] 正在啟動 買家申請門戶 (Port 8502)...
start "周邊售後買家門戶 - Buyer (8502)" cmd /k "streamlit run buyer.py --server.port 8502"

echo.
echo --------------------------------------------------------
echo ✅ 兩組伺服器已成功啟動！
echo.
echo 🛍️ 買家獨立前台：http://localhost:8502
echo 🧑‍💼 商家管理後台：http://localhost:8501
echo --------------------------------------------------------
echo 提示：請保持各伺服器命令視窗開啟，關閉命令視窗即停止服務。
pause
