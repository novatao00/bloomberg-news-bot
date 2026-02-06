import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

import yaml

from cache.sqlite_cache import NewsCache
from fetcher.github_downloader import GitHubDownloader
from notifier.feishu_bot import FeishuBot
from translator.openai_translator import OpenAITranslator
from utils.logger import setup_logger

def load_config():
    """加载配置文件"""
    config_path = Path(__file__).parent / 'config.yaml'
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def main():
    """主程序"""
    # 设置日志
    setup_logger()
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 50)
    logger.info("Bloomberg News Bot - Server Side")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info("=" * 50)
    
    # 加载配置
    config = load_config()
    
    # 1. 从GitHub拉取最新数据
    logger.info("Step 1: Fetching data from GitHub...")
    downloader = GitHubDownloader(config)
    news_data = downloader.download_latest()
    
    if not news_data:
        logger.error("Failed to fetch news data. Exiting.")
        sys.exit(1)
    
    logger.info(f"Fetched {len(news_data['articles'])} articles")
    
    # 2. 检查缓存去重
    logger.info("Step 2: Checking cache...")
    cache = NewsCache(config)
    new_articles = cache.filter_new_articles(news_data['articles'])
    
    if not new_articles:
        logger.info("No new articles. Exiting.")
        return
    
    logger.info(f"Found {len(new_articles)} new articles")
    
    # 3. 翻译文章
    logger.info("Step 3: Translating articles...")
    translator = OpenAITranslator(config)
    translated_articles = translator.translate_articles(new_articles)
    logger.info(f"Translated {len(translated_articles)} articles")
    
    # 4. 发送到飞书
    logger.info("Step 4: Sending to Feishu...")
    bot = FeishuBot(config)
    success = bot.send_news(translated_articles, news_data['metadata'])
    
    if success:
        logger.info("✓ News sent successfully")
        # 5. 更新缓存
        cache.add_articles(translated_articles)
        logger.info("✓ Cache updated")
    else:
        logger.error("✗ Failed to send news")
        sys.exit(1)
    
    logger.info("=" * 50)
    logger.info("Process completed successfully")
    logger.info("=" * 50)

if __name__ == '__main__':
    main()
