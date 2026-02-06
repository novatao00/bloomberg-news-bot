#!/bin/bash

# Bloomberg News Bot - CentOS 9 安装脚本
# 用法: chmod +x install_centos.sh && ./install_centos.sh

set -e  # 遇到错误立即退出

echo "======================================"
echo "Bloomberg News Bot 安装脚本"
echo "======================================"

# 检查root权限
if [ "$EUID" -ne 0 ]; then 
    echo "请使用 sudo 运行此脚本"
    exit 1
fi

# 1. 更新系统
echo "[1/8] 更新系统..."
dnf update -y

# 2. 安装Python 3.11
echo "[2/8] 安装 Python 3.11..."
dnf install -y python3.11 python3.11-pip

# 3. 安装其他依赖
echo "[3/8] 安装系统依赖..."
dnf install -y git curl wget sqlite

# 4. 创建项目目录
echo "[4/8] 创建项目目录..."
PROJECT_DIR="/opt/bloomberg-news-bot"
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# 5. 创建Python虚拟环境
echo "[5/8] 创建Python虚拟环境..."
python3.11 -m venv venv
source venv/bin/activate

# 6. 安装Python依赖
echo "[6/8] 安装Python依赖..."
pip install --upgrade pip

# 创建临时requirements文件
cat > /tmp/server_requirements.txt << 'EOF'
requests
openai
python-dateutil
pyyaml
python-dotenv
EOF

pip install -r /tmp/server_requirements.txt

# 7. 创建目录结构
echo "[7/8] 创建目录结构..."
mkdir -p $PROJECT_DIR/{server,logs,data/cache,scripts}

# 8. 设置权限
echo "[8/8] 设置权限..."
useradd -r -s /bin/false newsbot 2>/dev/null || true
chown -R newsbot:newsbot $PROJECT_DIR
chmod 750 $PROJECT_DIR

echo ""
echo "======================================"
echo "安装完成！"
echo "======================================"
echo ""
echo "下一步:"
echo "1. 将 server/ 目录的代码复制到 $PROJECT_DIR/server/"
echo "2. 创建 /opt/bloomberg-news-bot/.env 文件并配置环境变量"
echo "3. 编辑 /opt/bloomberg-news-bot/server/config.yaml 配置GitHub信息"
echo "4. 运行 scripts/setup_cron.sh 设置定时任务"
echo ""
echo "环境变量示例 (.env):"
echo "  OPENAI_API_KEY=sk-..."
echo "  FEISHU_APP_ID=cli-..."
echo "  FEISHU_APP_SECRET=..."
echo "  FEISHU_CHAT_ID=oc-..."
echo ""
