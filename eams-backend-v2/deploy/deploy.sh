#!/bin/bash
# EAMS Backend V2 部署脚本

set -e

echo "🚀 开始部署 EAMS Backend V2..."

# 配置
APP_NAME="eams-backend-v2"
APP_DIR="/opt/eams-backend-v2"
LOG_DIR="/var/log/eams"
USER="eams"

# 创建用户
echo "👤 创建用户..."
id -u $USER &>/dev/null || useradd -r -s /bin/false $USER

# 创建目录
echo "📁 创建目录..."
mkdir -p $APP_DIR
mkdir -p $LOG_DIR
mkdir -p /var/www/eams/static

# 复制代码
echo "📦 复制代码..."
cp -r . $APP_DIR/
chown -R $USER:$USER $APP_DIR
chown -R $USER:$USER $LOG_DIR

# 安装依赖
echo "📥 安装依赖..."
cd $APP_DIR
pip install -r requirements.txt

# 配置环境变量
echo "⚙️ 配置环境变量..."
if [ ! -f "$APP_DIR/.env" ]; then
    cp $APP_DIR/.env.example $APP_DIR/.env
    echo "请编辑 $APP_DIR/.env 配置数据库和API密钥"
fi

# 数据库迁移
echo "🗄️ 数据库迁移..."
cd $APP_DIR
alembic upgrade head || echo "跳过迁移"

# 创建系统服务
echo "🔧 创建系统服务..."
cat > /etc/systemd/system/$APP_NAME.service << EOF
[Unit]
Description=EAMS Backend V2
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
Environment=PATH=/usr/local/bin:/usr/bin
EnvironmentFile=$APP_DIR/.env
ExecStart=/usr/local/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 重载systemd
systemctl daemon-reload

# 启动服务
echo "🚀 启动服务..."
systemctl enable $APP_NAME
systemctl restart $APP_NAME

# 配置Nginx
echo "🌐 配置Nginx..."
cp deploy/nginx.conf /etc/nginx/sites-available/eams
ln -sf /etc/nginx/sites-available/eams /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

echo "✅ 部署完成！"
echo ""
echo "📋 服务状态:"
systemctl status $APP_NAME --no-pager
echo ""
echo "📝 日志查看:"
echo "  tail -f $LOG_DIR/error.log"
echo ""
echo "🌐 API地址:"
echo "  http://your-domain/api/v1"
echo "  http://your-domain/docs (API文档)"
