import logging
import random
import time
from typing import List

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class StealthBrowser:
    """隐形浏览器 - 用于爬取文章全文"""
    
    def __init__(self, config: dict):
        self.config = config
        self.fetching_config = config['fetching']
    
    def fetch_full_content(self, articles: List[dict]) -> List[dict]:
        """为标记的文章抓取全文"""
        articles_to_fetch = [a for a in articles if a.get('fetch_full_content')]
        
        if not articles_to_fetch:
            logger.info("No articles marked for full content fetching")
            return articles
        
        logger.info(f"Fetching full content for {len(articles_to_fetch)} articles...")
        
        with sync_playwright() as p:
            # 启动浏览器（无头模式）
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                ]
            )
            
            # 创建新上下文（隔离Cookie和缓存）
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent=random.choice(self.fetching_config['user_agents']),
                locale='en-US',
                timezone_id='America/New_York',
            )
            
            # 添加 stealth 脚本
            context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                window.chrome = { runtime: {} };
            """)
            
            page = context.new_page()
            
            try:
                for i, article in enumerate(articles_to_fetch):
                    try:
                        logger.info(f"Fetching article {i+1}/{len(articles_to_fetch)}: {article['title'][:50]}...")
                        
                        # 随机延迟，模拟人工浏览
                        delay = self.fetching_config['delay_between_requests'] + random.uniform(
                            0, self.fetching_config['delay_jitter'] * 2
                        )
                        time.sleep(delay)
                        
                        content = self._fetch_single_article(page, article['link'])
                        
                        if content:
                            article['full_content'] = content
                            article['has_full_content'] = True
                            logger.info(f"  ✓ Successfully fetched {len(content)} characters")
                        else:
                            logger.warning(f"  ✗ Failed to extract content")
                            article['has_full_content'] = False
                            
                    except Exception as e:
                        logger.error(f"  ✗ Error fetching article: {e}")
                        article['has_full_content'] = False
                        continue
            
            finally:
                context.close()
                browser.close()
        
        return articles
    
    def _fetch_single_article(self, page, url: str) -> str:
        """抓取单篇文章"""
        try:
            # 访问页面
            page.goto(url, wait_until='networkidle', timeout=30000)
            
            # 等待内容加载
            page.wait_for_load_state('domcontentloaded')
            time.sleep(random.uniform(2, 4))  # 模拟阅读时间
            
            # 随机滚动，模拟真实用户
            self._simulate_scrolling(page)
            
            # 提取内容
            html = page.content()
            content = self._extract_content(html, url)
            
            return content
            
        except PlaywrightTimeout:
            logger.error(f"Timeout loading page: {url}")
            return None
        except Exception as e:
            logger.error(f"Error loading page {url}: {e}")
            return None
    
    def _simulate_scrolling(self, page):
        """模拟滚动行为"""
        try:
            # 随机滚动几次
            for _ in range(random.randint(2, 4)):
                scroll_amount = random.randint(300, 700)
                page.evaluate(f"window.scrollBy(0, {scroll_amount})")
                time.sleep(random.uniform(0.5, 1.5))
        except:
            pass
    
    def _extract_content(self, html: str, url: str) -> str:
        """从HTML中提取文章内容"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # 尝试多种选择器（Bloomberg的HTML结构可能变化）
        selectors = [
            'article[data-testid="paragraph"]',
            'article p',
            '[data-testid="paragraph"]',
            '.article-body__content p',
            '.article-body p',
            'article .body-content p',
            'article .body__content p',
            'article section p',
        ]
        
        content_parts = []
        
        for selector in selectors:
            paragraphs = soup.select(selector)
            if paragraphs:
                for p in paragraphs[:20]:  # 最多取20段
                    text = p.get_text(strip=True)
                    if text and len(text) > 20:  # 过滤短段落
                        content_parts.append(text)
                
                if content_parts:
                    break
        
        if not content_parts:
            # 备用方案：提取所有正文段落
            for p in soup.find_all('p'):
                text = p.get_text(strip=True)
                if len(text) > 100:  # 较长的段落可能是正文
                    content_parts.append(text)
                if len(content_parts) >= 15:
                    break
        
        content = '\n\n'.join(content_parts)
        
        # 清理内容
        content = self._clean_content(content)
        
        return content[:8000] if content else None  # 限制长度
    
    def _clean_content(self, content: str) -> str:
        """清理文章内容"""
        # 移除常见噪音
        noise_patterns = [
            'Sign up for',
            'Subscribe to',
            'Read more:',
            'To contact the author',
            'To contact the editor',
            'Most Read from Bloomberg',
            '©2024 Bloomberg L.P.',
            'Before it\'s here, it\'s on the Bloomberg Terminal',
        ]
        
        for pattern in noise_patterns:
            if pattern in content:
                content = content.split(pattern)[0].strip()
        
        return content.strip()
