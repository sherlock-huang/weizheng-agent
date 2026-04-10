@echo off
chcp 65001 >nul 2>&1
echo ========================================
echo  魏征像素服务器状态
echo ========================================
echo.

python.exe -m src.cli status

echo.
echo 管理命令:
echo   start_background.bat - 启动服务器（后台）
echo   stop_server.bat      - 停止服务器
echo.
pause
