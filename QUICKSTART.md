# 🚀 快速启动指南

## 步骤1: 推送代码到GitHub（5分钟）

### 1.1 在GitHub创建仓库
1. 访问 https://github.com/new
2. 仓库名：`bloomberg-news-bot`
3. 选择 **Public**（推荐，免费）
4. **不要**勾选"Add a README file"
5. 点击"Create repository"

### 1.2 推送代码

**方法A：如果你有Git（Windows/Mac/Linux）**

打开终端/命令行，在项目目录执行：

```bash
cd bloomberg-news-bot

# 初始化Git
git init
git add .
git commit -m "Initial commit: Bloomberg News Bot"

# 添加你的GitHub仓库（替换YOUR_USERNAME）
git remote add origin https://github.com/YOUR_USERNAME/bloomberg-news-bot.git

# 推送代码
git branch -M main
git push -u origin main
```

**方法B：通过GitHub网页上传（如果你没有Git）**

1. 访问你刚创建的GitHub仓库
2. 点击 "uploading an existing file"
3. 将以下文件夹和文件拖拽上传：
   - `.github/` 文件夹（必须）
   - `github-actions-src/` 文件夹（必须）
   - `server/` 文件夹（必须）
   - `scripts/` 文件夹（必须）
   - `README.md`（必须）

4. 在底部输入提交信息：`Initial commit`
5. 点击 "Commit changes"

---

## 步骤2: 测试GitHub Actions（10分钟）

### 2.1 手动触发工作流

1. 访问你的GitHub仓库
2. 点击顶部的 **Actions** 标签
3. 左侧选择 "Bloomberg News Fetcher"
4. 点击 **Run workflow** 按钮
5. 选择分支：`main`
6. 点击绿色的 **Run workflow** 按钮

### 2.2 查看运行结果

- 等待3-5分钟
- 点击运行记录查看详细信息
- 如果成功，你应该看到：
  - ✅ "Checkout code"
  - ✅ "Set up Python"
  - ✅ "Install dependencies"
  - ✅ "Install Playwright"
  - ✅ "Fetch news"
  - ✅ "Upload news data"

### 2.3 检查Artifacts

1. 在Actions运行页面下方
2. 找到 "Artifacts" 部分
3. 下载 `news-data-xxx.zip` 文件
4. 解压查看，应该包含 `news_YYYYMMDD_HHMMSS.json`

---

## 步骤3: 获取必要凭证（15分钟）

### 3.1 获取OpenAI API Key

1. 访问 https://platform.openai.com/api-keys
2. 点击 "Create new secret key"
3. 复制生成的密钥（格式：`sk-proj-...`）
4. **保存好这个密钥，只显示一次！**

### 3.2 配置飞书机器人

1. 访问 https://open.feishu.cn/app
2. 点击 **"创建企业自建应用"**
3. 应用名称：`Bloomberg新闻机器人`
4. 选择应用类型：**企业自建应用**
5. 点击"确定创建"

6. 进入应用 → **"凭证与基础信息"**
   - 复制 **App ID**（格式：`cli_xxx`）
   - 点击 "查看"，复制 **App Secret**

7. 进入 **"权限管理"** → **"添加权限"**
   - 搜索并添加：
     - `im:chat:readonly` - 读取群组信息
     - `im:message:send` - 发送消息
   - 点击 "申请权限"

8. **发布应用**
   - 点击左侧 **"版本管理与发布"**
   - 点击 **"创建版本"**
   - 填写版本号：`1.0.0`
   - 点击 **"申请发布"**
   - 发布成功后才能使用！

9. **添加机器人到群聊**
   - 打开目标飞书群
   - 点击群设置 → 群机器人 → 添加机器人
   - 选择刚创建的 `Bloomberg新闻机器人`
   - 点击 "添加"

10. **获取群聊ID**
    - 在飞书群中，右键点击群名称
    - 选择 "复制链接"
    - 链接中包含 `chat_id=oc_xxx`
    - 复制 `oc_xxx` 部分

---

## 步骤4: 部署到CentOS服务器（20分钟）

### 4.1 SSH登录服务器

```bash
ssh root@your-digitalocean-ip
```

### 4.2 克隆仓库

```bash
cd /opt
git clone https://github.com/YOUR_USERNAME/bloomberg-news-bot.git
cd bloomberg-news-bot
```

### 4.3 运行安装脚本

```bash
chmod +x scripts/install_centos.sh
sudo ./scripts/install_centos.sh
```

这会自动安装：
- Python 3.11
- 系统依赖
- Python虚拟环境
- 创建目录结构

### 4.4 配置环境变量

```bash
cp server/.env.example .env
nano .env
```

填入以下内容：

```bash
# OpenAI API
OPENAI_API_KEY=sk-proj-your-key-here

# 飞书机器人
FEISHU_APP_ID=cli-your-app-id
FEISHU_APP_SECRET=your-app-secret-here
FEISHU_CHAT_ID=oc-your-chat-id

# 可选：GitHub Token（私有仓库需要）
# GITHUB_TOKEN=ghp-your-token
```

保存并退出（`Ctrl+X`, `Y`, `Enter`）

### 4.5 配置GitHub信息

```bash
nano server/config.yaml
```

修改：

```yaml
github:
  owner: "YOUR_USERNAME"      # 你的GitHub用户名
  repo: "bloomberg-news-bot" # 仓库名
```

### 4.6 复制服务器代码

```bash
cp -r server/* /opt/bloomberg-news-bot/server/
chown -R newsbot:newsbot /opt/bloomberg-news-bot
```

### 4.7 设置Cron定时任务

```bash
chmod +x scripts/setup_cron.sh
./scripts/setup_cron.sh
```

这会创建3个定时任务（北京时间 8:30/12:30/21:30）

### 4.8 手动测试

```bash
cd /opt/bloomberg-news-bot
source venv/bin/activate
python server/main.py
```

如果一切正常，你应该看到：
- ✅ "Step 1: Fetching data from GitHub..."
- ✅ "Step 2: Checking cache..."
- ✅ "Step 3: Translating articles..."
- ✅ "Step 4: Sending to Feishu..."
- ✅ "✓ News sent successfully"

同时，你的飞书群会收到第一条新闻消息！

---

## 步骤5: 验证系统运行（5分钟）

### 5.1 检查Cron任务

```bash
crontab -l
```

你应该看到3条定时任务。

### 5.2 检查日志

```bash
tail -f /opt/bloomberg-news-bot/logs/cron.log
```

### 5.3 验证飞书接收

- 等待下一个定时任务（最多8小时）
- 或手动触发服务器运行：
  ```bash
  cd /opt/bloomberg-news-bot
  source venv/bin/activate
  python server/main.py
  ```

---

## 🔧 故障排查

### 问题1: GitHub Actions失败

**症状**: Actions显示错误，没有生成Artifacts

**解决方案**:
1. 查看Actions日志中的具体错误信息
2. 检查仓库是否为Public
3. 确认代码已正确推送

### 问题2: 服务器无法获取数据

**症状**: "Failed to fetch news data"

**解决方案**:
1. 检查 `server/config.yaml` 中的GitHub信息
2. 确认GitHub Actions已成功运行
3. 检查网络连接：
   ```bash
   curl https://api.github.com
   ```

### 问题3: 飞书发送失败

**症状**: "Failed to send message"

**解决方案**:
1. 检查 `.env` 文件中的飞书凭证
2. 确认飞书应用已**发布**
3. 确认机器人已添加到群聊
4. 检查飞书应用权限（必须包含发送消息权限）

### 问题4: 翻译失败

**症状**: "OpenAI API error"

**解决方案**:
1. 检查 `OPENAI_API_KEY` 是否正确
2. 访问 https://platform.openai.com/usage 检查余额
3. 确认API密钥有足够的配额

---

## 📊 系统监控

### 查看GitHub Actions状态

访问你的GitHub仓库 → Actions标签

### 查看服务器日志

```bash
# 实时日志
tail -f /opt/bloomberg-news-bot/logs/cron.log

# 查看特定日期的日志
ls -lh /opt/bloomberg-news-bot/logs/

# 查看缓存状态
sqlite3 /opt/bloomberg-news-bot/data/cache/news_cache.db "SELECT source, COUNT(*) as count FROM articles GROUP BY source;"
```

### 重启定时任务

```bash
# 停止
sudo rm /etc/cron.d/bloomberg-news-bot

# 启动
sudo cp /opt/bloomberg-news-bot/scripts/setup_cron.sh /tmp/
cd /tmp
sudo ./setup_cron.sh
```

---

## ✅ 完成检查清单

部署完成后，请确认：

- [ ] GitHub Actions正常运行
- [ ] Artifacts成功生成（包含JSON文件）
- [ ] 服务器可以下载GitHub数据
- [ ] OpenAI翻译成功
- [ ] 飞书群收到消息
- [ ] Cron定时任务已设置
- [ ] 24小时去重功能正常

---

## 💰 费用确认

当前配置的月费用：

- GitHub Actions: **$0**（Public仓库）
- DigitalOcean: **$12/月**（已有）
- OpenAI API: **~$12-18/月**
- **总计: ~$24-30/月**

---

## 🎉 恭喜！

系统已完全部署完成！现在你将每天3次（8:30/12:30/21:30）自动收到最新的Bloomberg财经新闻，全部翻译成中文发送到飞书群。

有任何问题？随时问我！
