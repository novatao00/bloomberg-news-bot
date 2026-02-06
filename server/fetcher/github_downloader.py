import json
import logging
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import requests
from dateutil import parser as date_parser

logger = logging.getLogger(__name__)


class GitHubDownloader:
    """从GitHub Actions Artifacts下载数据"""
    
    def __init__(self, config: dict):
        self.config = config
        self.github_config = config.get('github', {})
        self.owner = self.github_config.get('owner', '')
        self.repo = self.github_config.get('repo', '')
        self.token = os.environ.get('GITHUB_TOKEN', '')  # 可选，公开仓库不需要
    
    def download_latest(self) -> Optional[dict]:
        """下载最新的新闻数据"""
        logger.info("Fetching latest artifact from GitHub Actions...")
        
        # 方法1: 通过GitHub API获取最新Artifacts
        try:
            return self._download_via_api()
        except Exception as e:
            logger.warning(f"API download failed: {e}")
        
        # 方法2: 通过nightly.link获取（公开仓库）
        try:
            return self._download_via_nightly()
        except Exception as e:
            logger.warning(f"Nightly.link download failed: {e}")
        
        # 方法3: 从本地文件读取（测试用）
        return self._download_local()
    
    def _download_via_api(self) -> Optional[dict]:
        """通过GitHub API下载"""
        if not self.owner or not self.repo:
            raise ValueError("GitHub owner and repo must be configured")
        
        headers = {
            'Accept': 'application/vnd.github.v3+json',
        }
        if self.token:
            headers['Authorization'] = f'token {self.token}'
        
        # 获取最新workflow run
        runs_url = f'https://api.github.com/repos/{self.owner}/{self.repo}/actions/runs'
        params = {
            'branch': 'main',
            'per_page': 5,
            'status': 'success'
        }
        
        response = requests.get(runs_url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        runs = response.json()['workflow_runs']
        
        if not runs:
            raise ValueError("No successful runs found")
        
        # 找到最新完成的run
        latest_run = None
        for run in runs:
            if run['status'] == 'completed' and run['conclusion'] == 'success':
                latest_run = run
                break
        
        if not latest_run:
            raise ValueError("No successful completed runs found")
        
        run_id = latest_run['id']
        run_time = date_parser.parse(latest_run['created_at'])
        
        # 检查是否是最新的（24小时内）
        if datetime.now(run_time.tzinfo) - run_time > timedelta(hours=12):
            logger.warning(f"Latest run is from {run_time}, more than 12 hours ago")
        
        logger.info(f"Found successful run: {run_id} from {run_time}")
        
        # 获取artifacts
        artifacts_url = f'https://api.github.com/repos/{self.owner}/{self.repo}/actions/runs/{run_id}/artifacts'
        response = requests.get(artifacts_url, headers=headers, timeout=30)
        response.raise_for_status()
        artifacts = response.json()['artifacts']
        
        if not artifacts:
            raise ValueError("No artifacts found")
        
        # 找到news-data artifact
        news_artifact = None
        for artifact in artifacts:
            if artifact['name'].startswith('news-data-'):
                news_artifact = artifact
                break
        
        if not news_artifact:
            raise ValueError("No news-data artifact found")
        
        # 下载artifact
        download_url = news_artifact['archive_download_url']
        logger.info(f"Downloading artifact: {news_artifact['name']}")
        
        response = requests.get(download_url, headers=headers, timeout=60)
        response.raise_for_status()
        
        # 解压zip文件
        import zipfile
        import io
        
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            json_files = [f for f in z.namelist() if f.endswith('.json')]
            if not json_files:
                raise ValueError("No JSON files in artifact")
            
            # 读取最新的JSON文件
            json_files.sort()
            with z.open(json_files[-1]) as f:
                data = json.load(f)
        
        logger.info(f"✓ Successfully downloaded {len(data.get('articles', []))} articles")
        return data
    
    def _download_via_nightly(self) -> Optional[dict]:
        """通过nightly.link下载（适用于公开仓库）"""
        # nightly.link 是一个服务，可以直接下载GitHub Actions Artifacts
        # URL格式: https://nightly.link/{owner}/{repo}/workflows/{workflow}/{branch}/{artifact-name}.zip
        
        if not self.owner or not self.repo:
            raise ValueError("GitHub owner and repo must be configured")
        
        url = f"https://nightly.link/{self.owner}/{self.repo}/workflows/fetch-news.yml/main/news-data.zip"
        
        logger.info(f"Trying nightly.link: {url}")
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        
        # 解压并读取
        import zipfile
        import io
        
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            json_files = [f for f in z.namelist() if f.endswith('.json')]
            if not json_files:
                raise ValueError("No JSON files")
            
            json_files.sort()
            with z.open(json_files[-1]) as f:
                data = json.load(f)
        
        logger.info(f"✓ Downloaded via nightly.link: {len(data.get('articles', []))} articles")
        return data
    
    def _download_local(self) -> Optional[dict]:
        """从本地文件读取（测试用）"""
        local_path = Path('test_data/news_sample.json')
        if local_path.exists():
            logger.info(f"Loading from local file: {local_path}")
            with open(local_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
