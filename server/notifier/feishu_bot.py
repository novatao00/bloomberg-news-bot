import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, List

import requests

logger = logging.getLogger(__name__)


class FeishuBot:
    """飞书机器人"""
    
    def __init__(self, config: dict):
        self.config = config
        self.feishu_config = config.get('feishu', {})
        
        self.app_id = os.environ.get('FEISHU_APP_ID')
        self.app_secret = os.environ.get('FEISHU_APP_SECRET')
        self.chat_id = os.environ.get('FEISHU_CHAT_ID')
        
        if not all([self.app_id, self.app_secret, self.chat_id]):
            raise ValueError("Feishu credentials not set in environment variables")
        
        self.access_token = None
        self.token_expires_at = 0
    
    def _get_access_token(self) -> str:
        """获取飞书访问令牌"""
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token
        
        url = 'https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal'
        
        response = requests.post(url, json={
            'app_id': self.app_id,
            'app_secret': self.app_secret
        }, timeout=30)
        
        response.raise_for_status()
        data = response.json()
        
        if data.get('code') != 0:
            raise ValueError(f"Failed to get access token: {data}")
        
        self.access_token = data['app_access_token']
        # 提前5分钟过期
        self.token_expires_at = time.time() + data['expire'] - 300
        
        return self.access_token
    
    def send_news(self, articles: List[dict], metadata: dict) -> bool:
        """发送新闻到飞书"""
        if not articles:
            logger.info("No articles to send")
            return True
        
        token = self._get_access_token()
        
        # 构建消息内容
        message = self._build_message(articles, metadata)
        
        url = 'https://open.feishu.cn/open-apis/im/v1/messages'
        
        params = {
            'receive_id_type': 'chat_id'
        }
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'receive_id': self.chat_id,
            'msg_type': 'interactive',
            'content': json.dumps(message)
        }
        
        try:
            response = requests.post(url, params=params, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get('code') == 0:
                logger.info(f"✓ Message sent successfully, message_id: {data.get('data', {}).get('message_id')}")
                return True
            else:
                logger.error(f"Failed to send message: {data}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    def _build_message(self, articles: List[dict], metadata: dict) -> dict:
        """构建飞书卡片消息"""
        # 统计来源
        source_stats = {}
        for article in articles:
            source = article.get('source', 'unknown')
            source_stats[source] = source_stats.get(source, 0) + 1
        
        source_text = ' | '.join([f"{k.title()}: {v}篇" for k, v in source_stats.items()])
        
        # 构建卡片内容
        elements = []
        
        # 标题
        elements.append({
            'tag': 'div',
            'text': {
                'tag': 'lark_md',
                'content': f"**📰 Bloomberg 财经早报 ({datetime.now().strftime('%m月%d日 %H:%M')})**"
            }
        })
        
        elements.append({'tag': 'hr'})
        
        # 文章列表
        for i, article in enumerate(articles[:10], 1):
            # 文章标题（带链接）
            title_zh = article.get('title_zh', article['title'])
            link = article['link']
            source = article.get('source', '').upper()
            
            # 重要性标记
            importance = '🔴' if i <= 3 else ('🟡' if i <= 6 else '⚪')
            
            elements.append({
                'tag': 'div',
                'text': {
                    'tag': 'lark_md',
                    'content': f"{importance} **[{source}]** [{title_zh}]({link})"
                }
            })
            
            # 摘要
            summary_zh = article.get('summary_zh', article.get('summary', ''))
            if summary_zh:
                # 截断过长的摘要
                if len(summary_zh) > 120:
                    summary_zh = summary_zh[:120] + "..."
                
                elements.append({
                    'tag': 'div',
                    'text': {
                        'tag': 'lark_md',
                        'content': f"💡 {summary_zh}"
                    }
                })
            
            # 如果有全文，添加折叠内容
            if article.get('has_full_content') and article.get('full_content_zh'):
                full_content = article['full_content_zh']
                if len(full_content) > 500:
                    full_content = full_content[:500] + "..."
                
                elements.append({
                    'tag': 'div',
                    'text': {
                        'tag': 'lark_md',
                        'content': f"📄 *全文摘要：*{full_content[:200]}..."
                    }
                })
            
            elements.append({'tag': 'hr'})
        
        # 底部统计
        elements.append({
            'tag': 'div',
            'text': {
                'tag': 'lark_md',
                'content': f"📊 **来源分布：** {source_text}\n⏰ **更新时间：** {metadata.get('generated_at', 'Unknown')[:19]}"
            }
        })
        
        # 构建完整卡片
        card = {
            'config': {
                'wide_screen_mode': True
            },
            'header': {
                'title': {
                    'tag': 'plain_text',
                    'content': 'Bloomberg 财经新闻'
                },
                'template': 'blue'
            },
            'elements': elements
        }
        
        return card
