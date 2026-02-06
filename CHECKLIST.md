# 部署检查清单

使用此清单确保所有步骤都已完成。

## 📋 准备阶段

### 必要凭证

- [ ] **OpenAI API Key**
  - 访问：https://platform.openai.com/api-keys
  - 创建API密钥
  - 保存密钥（格式：`sk-proj-...`）
  - 检查账户余额：https://platform.openai.com/usage

- [ ] **飞书应用**
  - 访问：https://open.feishu.cn/app
  - 创建企业自建应用
  - 复制 App ID（格式：`cli_xxx`）
  - 复制 App Secret
  - 添加权限：`im:chat:readonly`, `im:message:send`
  - **必须发布应用！**
  - 添加机器人到目标群聊
  - 复制群聊ID（格式：`oc_xxx`）

### GitHub账户

- [ ] GitHub账户已创建
- [ ] 准备好推送代码
- [ ] 记住用户名（用于配置文件）

---

## 🚀 Phase 1: GitHub Actions

### 1.1 创建GitHub仓库

- [ ] 访问 https://github.com/new
- [ ] 仓库名：`bloomberg-news-bot`
- [ ] 选择 **Public**（免费）
- [ ] **不要**勾选"Add a README file"
- [ ] 点击"Create repository"

### 1.2 推送代码

- [ ] 代码已推送到GitHub
  - 方法A：Git命令行
  - 方法B：GitHub网页上传

### 1.3 测试GitHub Actions

- [ ] 访问 GitHub仓库 → Actions
- [ ] 点击 "Run workflow" 手动触发
- [ ] 等待3-5分钟
- [ ] 所有步骤显示 ✅ 绿色成功
- [ ] 下载并检查Artifacts（`news-data-xxx.zip`）
- [ ] 解压确认包含 `news_YYYYMMDD_HHMMSS.json`

---

## 🖥️ Phase 2: CentOS服务器

### 2.1 SSH登录

- [ ] SSH登录到DigitalOcean服务器：
  ```bash
  ssh root@your-digitalocean-ip
  ```

### 2.2 安装系统

- [ ] 克隆仓库：
  ```bash
  cd /opt
  git clone https://github.com/YOUR_USERNAME/bloomberg-news-bot.git
  cd bloomberg-news-bot
  ```

- [ ] 运行安装脚本：
  ```bash
  chmod +x scripts/install_centos.sh
  sudo ./scripts/install_centos.sh
  ```
  [ ] 看到 "安装完成！"

### 2.3 配置环境变量

- [ ] 创建 `.env` 文件：
  ```bash
  cp server/.env.example .env
  nano .env
  ```

- [ ] 填入凭证：
  ```bash
  OPENAI_API_KEY=sk-proj-...
  FEISHU_APP_ID=cli-...
  FEISHU_APP_SECRET=...
  FEISHU_CHAT_ID=oc-...
  ```

- [ ] 保存并退出（`Ctrl+X`, `Y`, `Enter`）

### 2.4 配置GitHub信息

- [ ] 编辑配置文件：
  ```bash
  nano server/config.yaml
  ```

- [ ] 修改：
  ```yaml
  github:
    owner: "YOUR_USERNAME"
    repo: "bloomberg-news-bot"
  ```

- [ ] 保存并退出

### 2.5 复制服务器代码

- [ ] 执行：
  ```bash
  cp -r server/* /opt/bloomberg-news-bot/server/
  chown -R newsbot:newsbot /opt/bloomberg-news-bot
  ```

### 2.6 设置定时任务

- [ ] 运行：
  ```bash
  chmod +x scripts/setup_cron.sh
  ./scripts/setup_cron.sh
  ```
  [ ] 看到 "Cron任务设置完成！"

### 2.7 手动测试

- [ ] 激活虚拟环境：
  ```bash
  cd /opt/bloomberg-news-bot
  source venv/bin/activate
  ```

- [ ] 运行主程序：
  ```bash
  python server/main.py
  ```

- [ ] 检查输出：
  - [ ] "Step 1: Fetching data from GitHub..."
  - [ ] "Fetched X articles"
  - [ ] "Step 2: Checking cache..."
  - [ ] "Found X new articles"
  - [ ] "Step 3: Translating articles..."
  - [ ] "Translated X articles"
  - [ ] "Step 4: Sending to Feishu..."
  - [ ] "✓ News sent successfully"
  - [ ] "Process completed successfully"

---

## ✅ Phase 3: 验证系统运行

### 3.1 验证飞书接收

- [ ] 打开目标飞书群
- [ ] 查看是否收到新闻消息
- [ ] 消息包含：
  - [ ] 标题：📰 Bloomberg 财经早报
  - [ ] 10篇文章（带中文标题）
  - [ ] 2-3篇带全文摘要
  - [ ] 来源分布统计
  - [ ] 更新时间

### 3.2 检查定时任务

- [ ] 查看Cron任务：
  ```bash
  crontab -l
  ```
  [ ] 看到3条定时任务：
  ```
  25 0 * * * ...
  25 4 * * * ...
  25 13 * * * ...
  ```

### 3.3 检查日志

- [ ] 查看Cron日志：
  ```bash
  tail -f /opt/bloomberg-news-bot/logs/cron.log
  ```

- [ ] 查看应用日志：
  ```bash
  ls -lh /opt/bloomberg-news-bot/logs/
  ```

### 3.4 检查缓存

- [ ] 查看缓存状态：
  ```bash
  sqlite3 /opt/bloomberg-news-bot/data/cache/news_cache.db "SELECT * FROM articles;"
  ```

- [ ] 检查缓存统计：
  ```bash
  sqlite3 /opt/bloomberg-news-bot/data/cache/news_cache.db "SELECT source, COUNT(*) FROM articles GROUP BY source;"
  ```

---

## 🔧 故障排查

### GitHub Actions问题

- [ ] 如果Actions失败：
  - [ ] 查看Actions日志
  - [ ] 检查仓库是否为Public
  - [ ] 确认代码已正确推送
  - [ ] 检查Python版本兼容性

### 服务器获取数据失败

- [ ] 检查GitHub配置：
  ```bash
  cat /opt/bloomberg-news-bot/server/config.yaml
  ```

- [ ] 测试网络连接：
  ```bash
  curl https://api.github.com
  ```

- [ ] 检查GitHub Actions是否成功运行

### 飞书发送失败

- [ ] 检查环境变量：
  ```bash
  cat /opt/bloomberg-news-bot/.env
  ```

- [ ] 确认飞书应用已发布
- [ ] 确认机器人已添加到群聊
- [ ] 检查应用权限

### 翻译失败

- [ ] 检查OpenAI API Key
- [ ] 访问 https://platform.openai.com/usage
- [ ] 确认账户余额充足

---

## 📊 系统监控

### 日常检查

- [ ] 每天检查飞书是否收到3次消息
- [ ] 每周检查GitHub Actions运行状态
- [ ] 每月检查OpenAI API费用

### 日志管理

- [ ] 配置日志轮转（自动）
- [ ] 定期清理旧日志：
  ```bash
  find /opt/bloomberg-news-bot/logs -name "*.log" -mtime +7 -delete
  ```

---

## 💰 费用监控

### OpenAI费用

- [ ] 访问：https://platform.openai.com/usage
- [ ] 查看每日用量
- [ ] 预计费用：$12-18/月

### DigitalOcean费用

- [ ] 查看账单：DigitalOcean控制台
- [ ] 当前费用：$12/月

### GitHub费用

- [ ] Public仓库：免费
- [ ] Private仓库：检查使用量

---

## 🎉 完成状态

当所有检查项都 ✅ 时，说明系统已完全部署成功！

你将每天自动收到3次Bloomberg财经新闻（北京时间8:30/12:30/21:30），全部翻译成中文并发送到飞书群。

---

## 📞 需要帮助？

如果遇到任何问题，可以：

1. 查看 `QUICKSTART.md` 详细指南
2. 查看具体错误日志
3. 提问并附上错误信息

祝使用愉快！ 🚀
