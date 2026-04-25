@echo off
chcp 65001 >nul
echo ==========================================
echo    EAMS 后端服务启动脚本 (开发环境)
echo ==========================================
echo.

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请安装Python 3.10+
    exit /b 1
)

REM 检查虚拟环境
if not exist venv (
    echo [信息] 创建虚拟环境...
    python -m venv venv
)

echo [信息] 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
echo [信息] 安装依赖...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo [错误] 依赖安装失败
    exit /b 1
)

REM 安装SQLite异步驱动
echo [信息] 安装SQLite驱动...
pip install -q aiosqlite

echo.
echo ==========================================
echo    启动 EAMS 服务 (开发环境)
echo ==========================================
echo 数据库: SQLite (eams_dev.db)
echo 访问地址: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo.

REM 使用开发环境配置启动
set APP_ENV=development
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause
