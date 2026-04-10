@echo off
chcp 65001 >nul 2>&1
echo Starting Weizheng Pixel Server...
echo Port: 7788
echo.

REM 使用系统默认的 python，如果失败请检查环境变量
python -m src.server --port 7788 2>&1

if errorlevel 1 (
    echo.
    echo Failed to start server!
    echo.
    echo Trying with full Python path...
    "C:\Users\openclaw-windows-2\AppData\Local\Programs\Python\Python312\python.exe" -m src.server --port 7788
    
    if errorlevel 1 (
        echo.
        echo Still failed! Please ensure:
        echo   1. Python is installed
        echo   2. Pillow is installed: pip install Pillow
        echo   3. You are on Windows with a display
        pause
    )
)
