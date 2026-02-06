import json
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class GitHubArtifactsUploader:
    """GitHub Artifacts上传器"""
    
    def __init__(self):
        # 在GitHub Actions中，文件会自动上传到Artifacts
        # 这个类主要用于日志记录和验证
        self.is_github_actions = os.environ.get('GITHUB_ACTIONS') == 'true'
        self.run_id = os.environ.get('GITHUB_RUN_ID', 'local')
    
    def upload(self, file_path: Path):
        """验证文件并记录上传信息"""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # 验证JSON格式
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            article_count = len(data.get('articles', []))
            logger.info(f"✓ Validated JSON file: {article_count} articles")
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON file: {e}")
        
        # 在GitHub Actions中，upload-artifact action会自动处理上传
        # 这里只是记录信息
        if self.is_github_actions:
            logger.info(f"✓ File ready for artifact upload: {file_path.name}")
            logger.info(f"  Run ID: {self.run_id}")
            logger.info(f"  File size: {file_path.stat().st_size} bytes")
        else:
            logger.info(f"✓ File saved locally: {file_path}")
        
        return True
