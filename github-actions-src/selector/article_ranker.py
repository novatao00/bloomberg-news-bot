import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List

logger = logging.getLogger(__name__)


class ArticleRanker:
    """文章排序和选择器"""
    
    def __init__(self, config: dict):
        self.config = config
        self.selection_config = config['selection']
        self.keywords = config['keywords']
    
    def select_top_articles(self, articles: List[dict]) -> List[dict]:
        """选择最重要的文章"""
        total_needed = self.selection_config['total_articles']
        full_content_count = self.selection_config['full_content_count']
        bloomberg_priority = self.selection_config['bloomberg_priority']
        
        # 1. 计算每篇文章的分数
        scored_articles = []
        for article in articles:
            score = self._calculate_score(article)
            scored_articles.append((article, score))
        
        # 2. 排序
        scored_articles.sort(key=lambda x: x[1], reverse=True)
        
        # 3. 选择文章，保证来源多样性
        selected = []
        source_count = {'bloomberg': 0, 'yahoo': 0, 'reuters': 0}
        
        # Bloomberg优先策略
        if bloomberg_priority:
            # 首先选择Bloomberg的文章
            for article, score in scored_articles:
                if len(selected) >= total_needed:
                    break
                if article['source'] == 'bloomberg' and source_count['bloomberg'] < 7:
                    article['fetch_full_content'] = source_count['bloomberg'] < full_content_count
                    selected.append(article)
                    source_count['bloomberg'] += 1
            
            # 然后补充其他来源
            for article, score in scored_articles:
                if len(selected) >= total_needed:
                    break
                if article not in selected:
                    if article['source'] == 'yahoo' and source_count['yahoo'] < 2:
                        article['fetch_full_content'] = False
                        selected.append(article)
                        source_count['yahoo'] += 1
                    elif article['source'] == 'reuters' and source_count['reuters'] < 1:
                        article['fetch_full_content'] = False
                        selected.append(article)
                        source_count['reuters'] += 1
        else:
            # 均衡分布
            for article, score in scored_articles:
                if len(selected) >= total_needed:
                    break
                
                source = article['source']
                if source_count[source] < (total_needed // 3 + 1):
                    article['fetch_full_content'] = len([a for a in selected if a.get('fetch_full_content')]) < full_content_count
                    selected.append(article)
                    source_count[source] += 1
        
        # 如果没有选够，从剩余文章中补充
        if len(selected) < total_needed:
            for article, score in scored_articles:
                if len(selected) >= total_needed:
                    break
                if article not in selected:
                    article['fetch_full_content'] = False
                    selected.append(article)
        
        logger.info(f"Selection complete: Bloomberg {source_count['bloomberg']}, "
                   f"Yahoo {source_count['yahoo']}, Reuters {source_count['reuters']}")
        
        # 标记需要爬取全文的文章
        full_content_candidates = [a for a in selected if a.get('fetch_full_content')]
        logger.info(f"Articles marked for full content fetching: {len(full_content_candidates)}")
        
        return selected
    
    def _calculate_score(self, article: dict) -> float:
        """计算文章分数"""
        score = 0.0
        
        # 1. 时效性分数 (30%)
        freshness_score = self._calculate_freshness(article.get('published'))
        score += freshness_score * 0.3
        
        # 2. 关键词分数 (30%)
        keyword_score = self._calculate_keyword_score(article)
        score += keyword_score * 0.3
        
        # 3. 来源优先级 (25%)
        priority = article.get('priority', 1)
        score += (priority / 3.0) * 0.25
        
        # 4. 来源多样性奖励 (15%)
        # 这个在后续选择时处理，这里给基础分
        score += 0.15
        
        return score
    
    def _calculate_freshness(self, published: str) -> float:
        """计算时效性分数"""
        if not published:
            return 0.5
        
        try:
            pub_time = datetime.fromisoformat(published.replace('Z', '+00:00'))
            now = datetime.now(pub_time.tzinfo)
            hours_ago = (now - pub_time).total_seconds() / 3600
            
            # 越新分数越高
            if hours_ago < 1:
                return 1.0
            elif hours_ago < 6:
                return 0.9
            elif hours_ago < 12:
                return 0.8
            elif hours_ago < 24:
                return 0.7
            elif hours_ago < 48:
                return 0.5
            else:
                return 0.3
        except:
            return 0.5
    
    def _calculate_keyword_score(self, article: dict) -> float:
        """计算关键词匹配分数"""
        text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
        
        score = 0.0
        
        # 高优先级关键词
        for keyword in self.keywords['high']:
            if keyword in text:
                score += 0.15
        
        # 中优先级关键词
        for keyword in self.keywords['medium']:
            if keyword in text:
                score += 0.08
        
        # 低优先级关键词（减分）
        for keyword in self.keywords['low']:
            if keyword in text:
                score -= 0.1
        
        # 归一化到0-1
        return min(1.0, max(0.0, score))
