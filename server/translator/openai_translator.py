import logging
import os
import time
from typing import Dict, List

import openai

logger = logging.getLogger(__name__)


class OpenAITranslator:
    """OpenAI翻译器"""
    
    def __init__(self, config: dict):
        self.config = config
        self.openai_config = config.get('openai', {})
        
        # 设置API密钥
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        openai.api_key = api_key
        self.model = self.openai_config.get('model', 'gpt-4o-mini')
        self.max_tokens_title = self.openai_config.get('max_tokens_title', 100)
        self.max_tokens_summary = self.openai_config.get('max_tokens_summary', 300)
        self.max_tokens_content = self.openai_config.get('max_tokens_content', 1000)
    
    def translate_articles(self, articles: List[dict]) -> List[dict]:
        """翻译文章列表"""
        translated = []
        
        for i, article in enumerate(articles):
            logger.info(f"Translating article {i+1}/{len(articles)}: {article['title'][:50]}...")
            
            try:
                translated_article = self._translate_single(article)
                translated.append(translated_article)
                
                # 避免速率限制
                if i < len(articles) - 1:
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"Error translating article: {e}")
                # 如果翻译失败，使用原文
                article['title_zh'] = article['title']
                article['summary_zh'] = article.get('summary', '')
                article['full_content_zh'] = article.get('full_content', '')
                translated.append(article)
        
        return translated
    
    def _translate_single(self, article: dict) -> dict:
        """翻译单篇文章"""
        # 翻译标题
        title_zh = self._translate_text(
            article['title'],
            'title',
            self.max_tokens_title
        )
        
        # 翻译摘要
        summary = article.get('summary', '')
        if summary:
            summary_zh = self._translate_text(
                summary,
                'summary',
                self.max_tokens_summary
            )
        else:
            summary_zh = ''
        
        # 翻译全文（如果有）
        full_content = article.get('full_content', '')
        if full_content and article.get('has_full_content'):
            # 截断过长的内容
            if len(full_content) > 4000:
                full_content = full_content[:4000] + "..."
            
            full_content_zh = self._translate_text(
                full_content,
                'content',
                self.max_tokens_content
            )
        else:
            full_content_zh = ''
        
        # 更新文章
        article['title_zh'] = title_zh
        article['summary_zh'] = summary_zh
        article['full_content_zh'] = full_content_zh
        
        return article
    
    def _translate_text(self, text: str, text_type: str, max_tokens: int) -> str:
        """调用OpenAI API翻译"""
        if not text:
            return ''
        
        # 构建prompt
        prompts = {
            'title': '将以下英文新闻标题翻译成中文，保持简洁准确：',
            'summary': '将以下英文新闻摘要翻译成中文，控制在100字以内：',
            'content': '将以下英文新闻内容翻译成中文，保持专业术语准确，适当分段：'
        }
        
        prompt = prompts.get(text_type, '翻译成中文：')
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        'role': 'system',
                        'content': '你是一个专业的金融新闻翻译助手。请准确翻译，保持专业术语的一致性。'
                    },
                    {
                        'role': 'user',
                        'content': f"{prompt}\n\n{text}"
                    }
                ],
                max_tokens=max_tokens,
                temperature=0.3
            )
            
            translated = response.choices[0].message.content.strip()
            return translated
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
