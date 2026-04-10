@echo off
chcp 65001 >nul 2>&1
echo Starting Weizheng Headless Server (no GUI)...
echo Port: 7788
echo.
echo [NOTE] This mode runs without pixel animation
echo        Use this for testing API on RDP/headless systems
echo.

python src/server/headless_server.py --port 7788

if errorlevel 1 (
    echo.
    echo Failed to start server!
    pause
)
