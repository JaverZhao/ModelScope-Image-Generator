"""
图片下载管理模块
"""
import time
from typing import Optional, Callable
import requests

from src.utils.logger import get_logger

logger = get_logger("image-downloader")


class ImageDownloader:
    """图片下载器"""
    
    def __init__(self, max_retries: int = 3, retry_delay: int = 2):
        """
        初始化下载器
        
        Args:
            max_retries: 最大重试次数
            retry_delay: 重试延迟（秒）
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def download(
        self,
        url: str,
        timeout: int = 30,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> bytes:
        """
        下载图片
        
        Args:
            url: 图片 URL
            timeout: 超时时间（秒）
            progress_callback: 进度回调函数（当前大小，总大小）
            
        Returns:
            图片数据（字节）
            
        Raises:
            Exception: 下载失败
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Downloading image (attempt {attempt + 1}/{self.max_retries}): {url}")
                
                response = requests.get(url, stream=True, timeout=timeout)
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                current_size = 0
                chunks = []
                
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        chunks.append(chunk)
                        current_size += len(chunk)
                        
                        if progress_callback and total_size > 0:
                            progress_callback(current_size, total_size)
                
                image_data = b''.join(chunks)
                logger.info(f"Successfully downloaded image: {len(image_data)} bytes")
                return image_data
                
            except Exception as e:
                last_error = e
                logger.warning(f"Download attempt {attempt + 1} failed: {e}")
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        
        raise Exception(f"下载失败（重试 {self.max_retries} 次）: {last_error}")
    
    def download_multiple(
        self,
        urls: list[str],
        timeout: int = 30,
        progress_callback: Optional[Callable[[int, int, int], None]] = None,
    ) -> list[bytes]:
        """
        批量下载图片
        
        Args:
            urls: 图片 URL 列表
            timeout: 超时时间（秒）
            progress_callback: 进度回调函数（当前索引，总数，成功数）
            
        Returns:
            图片数据列表
        """
        results = []
        success_count = 0
        
        for idx, url in enumerate(urls):
            try:
                data = self.download(url, timeout)
                results.append(data)
                success_count += 1
                
                if progress_callback:
                    progress_callback(idx + 1, len(urls), success_count)
            except Exception as e:
                logger.error(f"Failed to download image {idx + 1}/{len(urls)}: {e}")
                results.append(None)
                
                if progress_callback:
                    progress_callback(idx + 1, len(urls), success_count)
        
        return results
    
    def test_connection(self, url: str) -> bool:
        """
        测试连接
        
        Args:
            url: 测试 URL
            
        Returns:
            是否可连接
        """
        try:
            response = requests.head(url, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False