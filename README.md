# Bloomberg News Bot

Bloomberg财经新闻自动抓取、翻译并推送到飞书的完整解决方案。

## 📋 系统架构

```
GitHub Actions（免费层）
├── 抓取Bloomberg/Yahoo/Reuters RSS
├── 智能选择10篇文章
├── 爬取2-3篇Bloomberg全文（使用Playwright）
└── 推送到GitHub Artifacts

DigitalOcean CentOS 9服务器
├── 从GitHub拉取数据
├── SQLite缓存去重（24小时）
├── OpenAI GPT-4o-mini翻译
└── 飞书机器人推送
```

## 🚀 部署步骤

### Phase 1: GitHub Actions配置（已完成 ✓）

1. **创建GitHub仓库**
   ```bash
   # 在你的GitHub账户创建仓库：bloomberg-news-bot
   ```

2. **推送代码到GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/bloomberg-news-bot.git
   git push -u origin main
   ```

3. **配置GitHub Actions**
   - 代码已包含 `.github/workflows/fetch-news.yml`
   - 定时任务已配置：每天3次（北京时间 8:30/12:30/21:30）

### Phase 2: 服务器配置

1. **在CentOS服务器上运行安装脚本**
   ```bash
   cd /opt
   git clone https://github.com/yourusername/bloomberg-news-bot.git
   cd bloomberg-news-bot
   sudo chmod +x scripts/install_centos.sh
   sudo ./scripts/install_centos.sh
   ```

2. **配置环境变量**
   ```bash
   sudo cp server/.env.example /opt/bloomberg-news-bot/.env
   sudo nano /opt/bloomberg-news-bot/.env
   # 填入：
   # OPENAI_API_KEY=sk-...
   # FEISHU_APP_ID=cli-...
   # FEISHU_APP_SECRET=...
   # FEISHU_CHAT_ID=oc-...
   ```

3. **配置服务器config.yaml**
   ```bash
   sudo nano /opt/bloomberg-news-bot/server/config.yaml
   # 填入你的GitHub信息：
   # github:
   #   owner: "yourusername"
   #   repo: "bloomberg-news-bot"
   ```

4. **复制服务器代码**
   ```bash
   sudo cp -r server/* /opt/bloomberg-news-bot/server/
   sudo chown -R newsbot:newsbot /opt/bloomberg-news-bot
   ```

5. **设置定时任务**
   ```bash
   sudo chmod +x scripts/setup_cron.sh
   sudo ./scripts/setup_cron.sh
   ```

6. **手动测试运行**
   ```bash
   cd /opt/bloomberg-news-bot
   source venv/bin/activate
   python server/main.py
   ```

## 📁 项目结构

```
bloomberg-news-bot/
├── .github/workflows/
│   └── fetch-news.yml              # GitHub Actions工作流
├── github-actions-src/              # GitHub Actions层代码
│   ├── main.py
│   ├── config.yaml
│   ├── requirements.txt
│   ├── rss/fetcher.py              # RSS抓取
│   ├── crawler/stealth_browser.py  # 反爬浏览器
│   ├── selector/article_ranker.py  # 文章排序
│   └── uploader/github_artifacts.py # 上传器
├── server/                          # CentOS服务器代码
│   ├── main.py
│   ├── config.yaml
│   ├── requirements.txt
│   ├── .env.example
│   ├── fetcher/github_downloader.py
│   ├── cache/sqlite_cache.py
│   ├── translator/openai_translator.py
│   ├── notifier/feishu_bot.py
│   └── utils/logger.py
├── scripts/
│   ├── install_centos.sh           # CentOS安装脚本
│   └── setup_cron.sh               # Cron设置脚本
└── docs/
    ├── setup_github.md             # GitHub配置指南
    ├── setup_server.md             # 服务器配置指南
    └── setup_feishu.md             # 飞书配置指南
```

## ⚙️ 配置说明

### GitHub Actions配置（config.yaml）

- **RSS源**: Bloomberg（优先）、Yahoo、Reuters
- **文章数量**: 10篇/次
- **全文爬取**: 2-3篇（Bloomberg优先）
- **请求间隔**: 5-8秒（随机）
- **定时**: 每天3次，±5分钟随机偏移

### 服务器配置（server/config.yaml）

```yaml
github:
  owner: "yourusername"      # 你的GitHub用户名
  repo: "bloomberg-news-bot" # 仓库名

cache:
  db_path: "data/cache/news_cache.db"
  retention_hours: 24        # 24小时去重

openai:
  model: "gpt-4o-mini"       # 翻译模型
  max_tokens_title: 100
  max_tokens_summary: 300
  max_tokens_content: 1000
```

### 环境变量（.env）

```bash
OPENAI_API_KEY=sk-...           # OpenAI API密钥
FEISHU_APP_ID=cli-...           # 飞书应用ID
FEISHU_APP_SECRET=...           # 飞书应用密钥
FEISHU_CHAT_ID=oc-...           # 飞书群聊ID
GITHUB_TOKEN=ghp-...            # 可选：私有仓库需要
```

## 💰 费用估算

| 项目 | 月费用 | 说明 |
|------|--------|------|
| GitHub Actions | $0 | 公开仓库免费 |
| DigitalOcean | $12 | 已有配置 |
| OpenAI API | ~$12-18 | GPT-4o-mini，30篇/天 |
| **总计** | **~$24-30/月** | |

## 🔒 安全措施

1. **IP隐藏**: GitHub Actions自动轮换IP
2. **请求频率**: 随机延迟，模拟人工行为
3. **浏览器指纹**: Playwright stealth模式
4. **零代理成本**: 使用RSS和官方API

## 📝 日志查看

```bash
# GitHub Actions日志
# GitHub仓库 -> Actions -> 选择工作流运行

# 服务器日志
tail -f /opt/bloomberg-news-bot/logs/cron.log
tail -f /opt/bloomberg-news-bot/logs/bot_$(date +%Y%m%d).log
```

## 🐛 故障排查

### 常见问题

1. **GitHub Actions运行失败**
   - 检查仓库是否为公开（或配置GITHUB_TOKEN）
   - 查看Actions日志获取详细错误

2. **服务器无法获取数据**
   - 检查config.yaml中的GitHub owner/repo配置
   - 确认GitHub Actions已成功运行并生成Artifacts

3. **飞书发送失败**
   - 检查.env文件中的飞书凭证
   - 确认机器人已添加到目标群聊
   - 检查飞书应用权限配置

4. **翻译失败**
   - 检查OPENAI_API_KEY是否有效
   - 检查API配额是否充足

## 📞 支持

如有问题，请查看：
- `docs/setup_github.md` - GitHub详细配置
- `docs/setup_server.md` - 服务器详细配置
- `docs/setup_feishu.md` - 飞书详细配置

## 📄 License

MIT License
