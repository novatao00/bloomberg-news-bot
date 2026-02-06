import hashlib
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)


class NewsCache:
    """SQLite缓存管理"""
    
    def __init__(self, config: dict):
        self.config = config
        self.cache_config = config.get('cache', {})
        self.db_path = Path(self.cache_config.get('db_path', 'data/cache/news_cache.db'))
        self.retention_hours = self.cache_config.get('retention_hours', 24)
        
        # 确保目录存在
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 初始化数据库
        self._init_db()
    
    def _init_db(self):
        """初始化数据库表"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id TEXT PRIMARY KEY,
                title TEXT,
                link TEXT,
                source TEXT,
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建索引
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_cached_at ON articles(cached_at)
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"Cache database initialized: {self.db_path}")
    
    def filter_new_articles(self, articles: List[dict]) -> List[dict]:
        """过滤掉已缓存的文章"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # 清理过期缓存
        self._cleanup_old_cache(cursor)
        conn.commit()
        
        # 获取所有已缓存的ID
        cursor.execute('SELECT id FROM articles')
        cached_ids = {row[0] for row in cursor.fetchall()}
        
        # 过滤新文章
        new_articles = []
        for article in articles:
            if article['id'] not in cached_ids:
                new_articles.append(article)
        
        conn.close()
        
        logger.info(f"Cache check: {len(articles)} total, {len(new_articles)} new, {len(articles) - len(new_articles)} cached")
        return new_articles
    
    def add_articles(self, articles: List[dict]):
        """添加文章到缓存"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        for article in articles:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO articles (id, title, link, source, cached_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (
                    article['id'],
                    article.get('title', '')[:200],  # 限制长度
                    article.get('link', ''),
                    article.get('source', '')
                ))
            except Exception as e:
                logger.error(f"Error caching article {article.get('id')}: {e}")
        
        conn.commit()
        conn.close()
        logger.info(f"Added {len(articles)} articles to cache")
    
    def _cleanup_old_cache(self, cursor):
        """清理过期的缓存"""
        cutoff_time = datetime.now() - timedelta(hours=self.retention_hours)
        cursor.execute('''
            DELETE FROM articles WHERE cached_at < ?
        ''', (cutoff_time.isoformat(),))
        
        deleted = cursor.rowcount
        if deleted > 0:
            logger.info(f"Cleaned up {deleted} old cache entries")
    
    def get_stats(self) -> dict:
        """获取缓存统计信息"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM articles')
        total = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT source, COUNT(*) FROM articles GROUP BY source
        ''')
        by_source = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'total_cached': total,
            'by_source': by_source
        }
