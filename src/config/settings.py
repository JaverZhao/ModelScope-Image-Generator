"""
全局配置常量
"""
import os

# 项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 数据目录
DATA_DIR = os.path.join(BASE_DIR, "data")
IMAGES_DIR = os.path.join(DATA_DIR, "images")
HISTORY_DIR = os.path.join(DATA_DIR, "history")
CACHE_DIR = os.path.join(DATA_DIR, "cache")

# 日志目录
LOG_DIR = os.path.join(BASE_DIR, "logs")

# API 配置
API_BASE_URL = "https://api-inference.modelscope.cn/"

# 任务配置
DEFAULT_TIMEOUT = 300  # 默认超时时间（秒）
POLL_INTERVAL = 5  # 轮询间隔（秒）
MAX_RETRY_COUNT = 3  # 最大重试次数

# 图片配置
THUMBNAIL_SIZE = (256, 256)  # 缩略图尺寸
SUPPORTED_IMAGE_FORMATS = [".jpg", ".jpeg", ".png"]

# 历史记录配置
HISTORY_FILE = os.path.join(HISTORY_DIR, "history.json")
MAX_HISTORY_RECORDS = 1000  # 最大历史记录数

# 配置文件路径
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
ENV_FILE = os.path.join(BASE_DIR, ".env")

# 确保目录存在
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(HISTORY_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)