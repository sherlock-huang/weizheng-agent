@echo off
chcp 65001 >nul 2>&1
echo ========================================
echo  启动魏征像素服务器（后台模式）
echo ========================================
echo.

REM 使用 pythonw.exe 启动（无控制台窗口）
start /B pythonw.exe -m src.server --port 7788

REM 等待服务器启动
timeout /t 2 /nobreak >nul

REM 检查状态
python.exe -m src.cli status >nul 2>&1
if errorlevel 1 (
    echo [错误] 启动失败！
    echo.
    pause
) else (
    echo [OK] 服务器已在后台启动！
    echo.
    echo 端口: 7788
    echo API: http://localhost:7788
    echo.
    echo 管理命令:
    echo   stop_server.bat    - 停止服务器
    echo   check_status.bat   - 查看状态
    echo.
    echo 提示: 可以关闭此窗口，服务器会继续运行
    timeout /t 3 >nul
)
