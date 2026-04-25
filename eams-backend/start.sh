#!/bin/bash

echo "=========================================="
echo "   EAMS 后端服务启动脚本"
echo "=========================================="
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到Python3，请安装Python 3.10+"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "[信息] 创建虚拟环境..."
    python3 -m venv venv
fi

echo "[信息] 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "[信息] 安装依赖..."
pip install -q -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[错误] 依赖安装失败"
    exit 1
fi

# 检查环境变量
if [ ! -f ".env" ]; then
    echo "[警告] 未找到.env文件，使用默认配置"
    echo "[提示] 请复制.env.example为.env并修改配置"
fi

# 数据库迁移
echo "[信息] 执行数据库迁移..."
alembic upgrade head
if [ $? -ne 0 ]; then
    echo "[警告] 数据库迁移失败，请检查数据库连接"
fi

echo ""
echo "=========================================="
echo "   启动 EAMS 服务"
echo "=========================================="
echo "访问地址: http://localhost:8000"
echo "API文档: http://localhost:8000/docs"
echo ""

# 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
