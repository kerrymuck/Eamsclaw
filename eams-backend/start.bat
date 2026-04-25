@echo off
chcp 65001 >nul
echo ==========================================
echo    EAMS 后端服务启动脚本
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

REM 检查环境变量
if not exist .env (
    echo [警告] 未找到.env文件，使用默认配置
    echo [提示] 请复制.env.example为.env并修改配置
)

REM 数据库迁移
echo [信息] 执行数据库迁移...
alembic upgrade head
if errorlevel 1 (
    echo [警告] 数据库迁移失败，请检查数据库连接
)

echo.
echo ==========================================
echo    启动 EAMS 服务
echo ==========================================
echo 访问地址: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo.

REM 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause
