import logging
import sys
from datetime import datetime
from pathlib import Path


def setup_logger():
    """设置日志"""
    # 创建日志目录
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # 日志文件名
    log_file = log_dir / f"bot_{datetime.now().strftime('%Y%m%d')}.log"
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file, encoding='utf-8')
        ]
    )
