"""
개선된 뉴스 크롤링 모듈

금융 뉴스 사이트에서 기사를 수집하고, 감성 분석을 수행하는 모듈입니다.
모니터링 및 유효성 검사 기능이 추가되었습니다.
"""
import json
import logging
import os
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

import requests
from bs4 import BeautifulSoup
import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
import pandas as pd

# 모니터링 및 유효성 검사 모듈 가져오기
from .monitoring.crawler_monitor import CrawlerMonitor
from .monitoring.crawler_validator import CrawlerValidator

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 환경 변수 로드
env_path = Path(__file__).parents[1] / '.env'
load_dotenv(dotenv_path=env_path)

# 설정 파일 로드
config_path = Path(__file__).parent / 'config.json'
with open(config_path, 'r') as f:
    CONFIG = json.load(f)


class EnhancedNewsC