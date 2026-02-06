#!/bin/bash

# Bloomberg News Bot - Cron定时任务设置
# 用法: chmod +x setup_cron.sh && ./setup_cron.sh

set -e

echo "======================================"
echo "设置Cron定时任务"
echo "======================================"

PROJECT_DIR="/opt/bloomberg-news-bot"
PYTHON="$PROJECT_DIR/venv/bin/python"
MAIN_SCRIPT="$PROJECT_DIR/server/main.py"

# 创建Cron任务文件
CRON_FILE="/tmp/newsbot_cron"

cat > $CRON_FILE << EOF
# Bloomberg News Bot - 每8小时运行一次
# 北京时间 8:30 / 12:30 / 21:30（带随机偏移）

# 早上 8:25-8:35 (北京时间 = UTC 00:25-00:35)
25 0 * * * root sleep \$((RANDOM % 600)) && cd $PROJECT_DIR && $PYTHON $MAIN_SCRIPT >> $PROJECT_DIR/logs/cron.log 2>&1

# 中午 12:25-12:35 (北京时间 = UTC 04:25-04:35)
25 4 * * * root sleep \$((RANDOM % 600)) && cd $PROJECT_DIR && $PYTHON $MAIN_SCRIPT >> $PROJECT_DIR/logs/cron.log 2>&1

# 晚上 21:25-21:35 (北京时间 = UTC 13:25-13:35)
25 13 * * * root sleep \$((RANDOM % 600)) && cd $PROJECT_DIR && $PYTHON $MAIN_SCRIPT >> $PROJECT_DIR/logs/cron.log 2>&1

# 日志清理 - 每周清理一次7天前的日志
0 2 * * 0 root find $PROJECT_DIR/logs -name "*.log" -mtime +7 -delete
EOF

# 安装Cron任务
echo "安装Cron任务..."
cp $CRON_FILE /etc/cron.d/bloomberg-news-bot
chmod 644 /etc/cron.d/bloomberg-news-bot

# 确保Cron服务运行
echo "启动Cron服务..."
systemctl enable crond
systemctl start crond

# 清理临时文件
rm -f $CRON_FILE

echo ""
echo "======================================"
echo "Cron任务设置完成！"
echo "======================================"
echo ""
echo "查看任务: crontab -l"
echo "查看日志: tail -f $PROJECT_DIR/logs/cron.log"
echo "手动运行: cd $PROJECT_DIR && $PYTHON $MAIN_SCRIPT"
echo ""
