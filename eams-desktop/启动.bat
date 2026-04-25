@echo off
chcp 65001 >nul
echo ==========================================
echo    EAMS 智能客服管理系统 - 桌面版
echo ==========================================
echo.
echo 正在启动应用程序...
echo.

REM 检查 Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Node.js，请先安装 Node.js
    pause
    exit /b 1
)

REM 启动应用
cd /d "%~dp0"
npm start

pause
