import json
import logging
import os
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

import yaml

from crawler.stealth_browser import StealthBrowser
from rss.fetcher import RSSFetcher
from selector.article_ranker import ArticleRanker
from uploader.github_artifacts import GitHubArtifactsUploader

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/fetcher.log')
    ]
)
logger = logging.getLogger(__name__)


def load_config():
    """加载配置文件"""
    config_path = Path(__file__).parent / 'config.yaml'
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def main():
    """主程序"""
    logger.info("=" * 50)
    logger.info("Bloomberg News Fetcher Started")
    logger.info(f"Timestamp: {datetime.utcnow().isoformat()}")
    logger.info("=" * 50)
    
    # 创建输出目录
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)
    
    # 加载配置
    config = load_config()
    logger.info("Configuration loaded successfully")
    
    # 1. 抓取RSS源
    logger.info("Step 1: Fetching RSS feeds...")
    rss_fetcher = RSSFetcher(config)
    all_articles = rss_fetcher.fetch_all()
    logger.info(f"Total articles from RSS: {len(all_articles)}")
    
    if len(all_articles) < 5:
        logger.error("Too few articles fetched. Aborting.")
        sys.exit(1)
    
    # 2. 智能选择文章
    logger.info("Step 2: Ranking and selecting articles...")
    ranker = ArticleRanker(config)
    selected_articles = ranker.select_top_articles(all_articles)
    logger.info(f"Selected {len(selected_articles)} articles")
    
    # 3. 爬取选定文章的全文（仅前3篇）
    logger.info("Step 3: Fetching full content for top articles...")
    browser = StealthBrowser(config)
    articles_with_content = browser.fetch_full_content(selected_articles)
    logger.info(f"Full content fetched for {sum(1 for a in articles_with_content if a.get('full_content'))} articles")
    
    # 4. 保存数据
    logger.info("Step 4: Saving data...")
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f'news_{timestamp}.json'
    
    output_data = {
        'metadata': {
            'generated_at': datetime.utcnow().isoformat(),
            'total_articles': len(articles_with_content),
            'full_content_count': sum(1 for a in articles_with_content if a.get('full_content')),
            'sources': list(set(a['source'] for a in articles_with_content))
        },
        'articles': articles_with_content
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Data saved to: {output_file}")
    
    # 5. 上传到Artifacts（仅在GitHub Actions环境中）
    if os.environ.get('GITHUB_ACTIONS'):
        logger.info("Step 5: Uploading to GitHub Artifacts...")
        uploader = GitHubArtifactsUploader()
        uploader.upload(output_file)
    else:
        logger.info("Running locally, skipping artifact upload")
    
    logger.info("=" * 50)
    logger.info("Bloomberg News Fetcher Completed Successfully")
    logger.info("=" * 50)


if __name__ == '__main__':
    main()
