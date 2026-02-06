import logging
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from urllib.parse import urljoin

import feedparser
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class RSSFetcher:
    """RSS抓取器"""
    
    def __init__(self, config: dict):
        self.config = config
        self.rss_sources = config['rss_sources']
        self.fetching_config = config['fetching']
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': random.choice(self.fetching_config['user_agents']),
            'Accept': 'application/rss+xml,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
    
    def fetch_all(self) -> List[dict]:
        """抓取所有RSS源"""
        all_articles = []
        
        for source_name, source_config in self.rss_sources.items():
            logger.info(f"Fetching from {source_name}...")
            
            for category, url in source_config.items():
                if category == 'priority':
                    continue
                
                try:
                    articles = self._fetch_rss(url, source_name, category, source_config.get('priority', 1))
                    all_articles.extend(articles)
                    logger.info(f"  {category}: {len(articles)} articles")
                    
                    # 请求间隔，避免被封
                    delay = self.fetching_config['delay_between_requests'] + random.uniform(0, self.fetching_config['delay_jitter'])
                    time.sleep(delay)
                    
                except Exception as e:
                    logger.error(f"  Error fetching {source_name}/{category}: {e}")
                    continue
        
        return all_articles
    
    def _fetch_rss(self, url: str, source: str, category: str, priority: int) -> List[dict]:
        """抓取单个RSS源"""
        articles = []
        
        try:
            response = self.session.get(
                url, 
                timeout=self.fetching_config['request_timeout']
            )
            response.raise_for_status()
            
            # 解析RSS
            feed = feedparser.parse(response.content)
            
            for entry in feed.entries[:15]:  # 每个源最多取15篇
                article = self._parse_entry(entry, source, category, priority)
                if article:
                    articles.append(article)
                    
        except Exception as e:
            logger.error(f"Error parsing RSS from {url}: {e}")
            raise
        
        return articles
    
    def _parse_entry(self, entry, source: str, category: str, priority: int) -> Optional[dict]:
        """解析单条RSS条目"""
        try:
            # 提取基本信息
            title = entry.get('title', '').strip()
            link = entry.get('link', '')
            summary = entry.get('summary', '') or entry.get('description', '')
            
            # 清理摘要（去除HTML标签）
            if summary:
                soup = BeautifulSoup(summary, 'html.parser')
                summary = soup.get_text(separator=' ', strip=True)[:500]
            
            # 解析发布时间
            published = self._parse_date(entry)
            
            # 提取作者
            author = entry.get('author', '')
            
            # 生成唯一ID
            article_id = self._generate_id(link, title)
            
            return {
                'id': article_id,
                'title': title,
                'summary': summary,
                'link': link,
                'source': source,
                'category': category,
                'priority': priority,
                'published': published.isoformat() if published else None,
                'author': author,
                'has_full_content': False,  # RSS默认没有全文
                'full_content': None
            }
            
        except Exception as e:
            logger.error(f"Error parsing entry: {e}")
            return None
    
    def _parse_date(self, entry) -> Optional[datetime]:
        """解析发布时间"""
        date_fields = ['published_parsed', 'updated_parsed', 'created_parsed']
        
        for field in date_fields:
            if hasattr(entry, field) and getattr(entry, field):
                try:
                    t = getattr(entry, field)
                    return datetime(*t[:6])
                except:
                    continue
        
        # 尝试解析字符串日期
        date_strings = ['published', 'updated', 'created']
        for field in date_strings:
            if hasattr(entry, field) and getattr(entry, field):
                try:
                    # feedparser应该已经解析过了
                    pass
                except:
                    continue
        
        return None
    
    def _generate_id(self, link: str, title: str) -> str:
        """生成文章唯一ID"""
        import hashlib
        content = f"{link}:{title}".encode('utf-8')
        return hashlib.md5(content).hexdigest()[:16]
