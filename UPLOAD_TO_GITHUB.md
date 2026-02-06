# 📤 通过GitHub网页上传代码指南

由于Windows系统没有安装Git，我们使用GitHub网页上传功能。

## 步骤1: 创建GitHub仓库（2分钟）

1. 访问 https://github.com/new
2. 仓库名：`bloomberg-news-bot`
3. 选择 **Public**（推荐，完全免费）
4. **不要**勾选"Add a README file"
5. **不要**勾选"Add .gitignore"
6. **不要**勾选"Choose a license"
7. 点击绿色按钮 **"Create repository"**

## 步骤2: 上传文件（5分钟）

### 方法A: 上传整个文件夹（推荐）

1. 在创建的仓库页面，点击 **"uploading an existing file"** 链接
2. 点击 **"drag files here"** 或选择文件夹图标

3. **一次性拖拽以下文件夹到GitHub**：
   ```
   📁 .github/          （必须！）
   📁 github-actions-src/  （必须！）
   📁 server/           （必须！）
   📁 scripts/          （必须！）
   ```

4. **然后拖拽以下单个文件**：
   ```
   📄 README.md
   📄 QUICKSTART.md
   📄 CHECKLIST.md
   📄 DEPLOYMENT_SUMMARY.md
   📄 .gitignore
   📄 .env.example
   ```

5. 在底部 **"Commit changes"** 区域：
   - 第一框输入：`Initial commit`
   - 第二框输入：`Create Bloomberg News Bot with GitHub Actions`
   - 选择：`Commit directly to the main branch`
   - 点击绿色按钮 **"Commit changes"**

### 方法B: 逐个文件夹上传（如果方法A失败）

如果一次性上传失败，按顺序上传：

**第1批：上传 .github 文件夹**
1. 点击"uploading an existing file"
2. 创建文件夹：`.github/workflows`
3. 上传 `.github/workflows/fetch-news.yml`
4. Commit: "Add GitHub Actions workflow"

**第2批：上传 github-actions-src 文件夹**
1. 创建文件夹：`github-actions-src`
2. 上传所有文件和子文件夹
3. Commit: "Add GitHub Actions source code"

**第3批：上传 server 文件夹**
1. 创建文件夹：`server`
2. 上传所有文件和子文件夹
3. Commit: "Add server code"

**第4批：上传 scripts 文件夹**
1. 创建文件夹：`scripts`
2. 上传所有文件
3. Commit: "Add deployment scripts"

**第5批：上传文档**
1. 上传所有 .md 文件
2. Commit: "Add documentation"

## 步骤3: 验证上传（1分钟）

上传完成后，检查：

1. ✅ 仓库首页显示所有文件夹
2. ✅ 点击 `.github/workflows/` 应该看到 `fetch-news.yml`
3. ✅ 点击 `github-actions-src/` 应该看到 `main.py`, `config.yaml`, `requirements.txt`
4. ✅ 点击 `server/` 应该看到 `main.py`, `config.yaml`, `requirements.txt`

## 步骤4: 测试GitHub Actions（3分钟）

1. 在你的GitHub仓库页面，点击顶部 **"Actions"** 标签
2. 应该看到 **"Bloomberg News Fetcher"** 工作流
3. 点击工作流名称
4. 点击 **"Run workflow"** 按钮（蓝色）
5. 选择分支：`main`
6. 点击 **"Run workflow"**（绿色）

等待3-5分钟，你应该看到：
- ✅ 所有步骤变成绿色
- ✅ "Upload news data" 步骤
- ✅ "Artifacts" 部分出现 `news-data-xxx.zip`

## 🎯 上传完成后

如果GitHub Actions成功运行，接下来你需要：

### 1. 准备服务器部署凭证

- OpenAI API Key
- 飞书 App ID + App Secret + Chat ID

### 2. SSH登录CentOS服务器

```bash
ssh root@your-digitalocean-ip
```

### 3. 克隆仓库并部署

```bash
cd /opt
git clone https://github.com/YOUR_USERNAME/bloomberg-news-bot.git
cd bloomberg-news-bot

chmod +x scripts/install_centos.sh
sudo ./scripts/install_centos.sh
```

### 4. 配置环境变量

```bash
cp server/.env.example .env
nano .env
# 填入凭证
```

### 5. 完成配置

按照 `QUICKSTART.md` 步骤4继续部署。

---

## 💡 提示

- 如果上传遇到问题，可以分批次上传
- 确保上传了所有 `.py` 和 `.yaml` 文件
- 上传后立即测试GitHub Actions
- 如果Actions失败，查看具体错误日志

---

## ✅ 完成检查

上传完成后，确保：

- [ ] 所有文件夹都已上传
- [ ] GitHub Actions可以手动运行
- [ ] Artifacts成功生成
- [ ] 代码没有遗漏

继续下一步：测试GitHub Actions！🚀
