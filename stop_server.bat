@echo off
chcp 65001 >nul 2>&1
echo ========================================
echo  停止魏征像素服务器
echo ========================================
echo.

python.exe -m src.cli stop

if errorlevel 1 (
    echo.
    echo [提示] 服务器可能未运行，或已经停止
) else (
    echo.
    echo [OK] 服务器已停止
)

echo.
pause
