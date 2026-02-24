"""
图片处理工具模块
"""
import os
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from io import BytesIO
import requests
from PIL import Image

from src.config.settings import IMAGES_DIR, THUMBNAIL_SIZE
from src.utils.logger import get_logger

logger = get_logger("image-processor")


class ImageProcessor:
    """图片处理器"""
    
    @staticmethod
    def create_date_directory() -> str:
        """
        按日期创建存储目录
        
        Returns:
            目录路径
        """
        today = datetime.now().strftime("%Y-%m-%d")
        date_dir = os.path.join(IMAGES_DIR, today)
        os.makedirs(date_dir, exist_ok=True)
        return date_dir
    
    @staticmethod
    def save_image(
        image_data: bytes,
        record_id: str,
        date_dir: Optional[str] = None,
    ) -> str:
        """
        保存原始图片
        
        Args:
            image_data: 图片数据（字节）
            record_id: 记录 ID
            date_dir: 日期目录（如果为 None 则自动创建）
            
        Returns:
            图片文件路径
        """
        if date_dir is None:
            date_dir = ImageProcessor.create_date_directory()
        
        filename = f"{record_id}_original.jpg"
        filepath = os.path.join(date_dir, filename)
        
        try:
            image = Image.open(BytesIO(image_data))
            image.save(filepath, "JPEG", quality=95)
            logger.info(f"Saved original image: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to save image: {e}")
            raise
    
    @staticmethod
    def generate_thumbnail(
        image_path: str,
        record_id: str,
        size: Tuple[int, int] = THUMBNAIL_SIZE,
        date_dir: Optional[str] = None,
    ) -> str:
        """
        生成缩略图
        
        Args:
            image_path: 原图路径
            record_id: 记录 ID
            size: 缩略图尺寸
            date_dir: 日期目录（如果为 None 则自动创建）
            
        Returns:
            缩略图文件路径
        """
        if date_dir is None:
            date_dir = ImageProcessor.create_date_directory()
        
        filename = f"{record_id}_thumb.jpg"
        filepath = os.path.join(date_dir, filename)
        
        try:
            image = Image.open(image_path)
            
            # 保持宽高比的缩略图
            image.thumbnail(size, Image.Resampling.LANCZOS)
            
            # 创建新图像以确保尺寸准确
            if image.size != size:
                new_image = Image.new("RGB", size, (255, 255, 255))
                # 居中粘贴
                offset = ((size[0] - image.size[0]) // 2, (size[1] - image.size[1]) // 2)
                new_image.paste(image, offset)
                image = new_image
            
            image.save(filepath, "JPEG", quality=85)
            logger.info(f"Generated thumbnail: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to generate thumbnail: {e}")
            raise
    
    @staticmethod
    def get_image_info(image_path: str) -> Dict[str, Any]:
        """
        获取图片信息
        
        Args:
            image_path: 图片路径
            
        Returns:
            图片信息字典（尺寸、大小等）
        """
        try:
            image = Image.open(image_path)
            file_size = os.path.getsize(image_path)
            
            return {
                "width": image.width,
                "height": image.height,
                "format": image.format,
                "mode": image.mode,
                "size_bytes": file_size,
                "size_mb": round(file_size / (1024 * 1024), 2),
            }
        except Exception as e:
            logger.error(f"Failed to get image info: {e}")
            return {}
    
    @staticmethod
    def download_and_save(
        image_url: str,
        record_id: Optional[str] = None,
        create_thumbnail: bool = True,
    ) -> Tuple[str, Optional[str]]:
        """
        从 URL 下载并保存图片
        
        Args:
            image_url: 图片 URL
            record_id: 记录 ID（如果为 None 则自动生成）
            create_thumbnail: 是否生成缩略图
            
        Returns:
            (原图路径, 缩略图路径)
        """
        # 下载图片
        logger.info(f"Downloading image from: {image_url}")
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        
        # 生成记录 ID
        if record_id is None:
            record_id = str(uuid.uuid4())[:8]
        
        # 创建日期目录
        date_dir = ImageProcessor.create_date_directory()
        
        # 保存原图
        original_path = ImageProcessor.save_image(response.content, record_id, date_dir)
        
        # 生成缩略图
        thumbnail_path = None
        if create_thumbnail:
            thumbnail_path = ImageProcessor.generate_thumbnail(original_path, record_id, date_dir=date_dir)
        
        return original_path, thumbnail_path
    
    @staticmethod
    def download_batch(
        image_urls: list[str],
        record_id: str,
    ) -> list[Dict[str, Any]]:
        """
        批量下载图片
        
        Args:
            image_urls: 图片 URL 列表
            record_id: 记录 ID
            
        Returns:
            下载结果列表
        """
        results = []
        
        for idx, url in enumerate(image_urls):
            try:
                # 为每张图片生成唯一的子 ID
                sub_id = f"{record_id}_{idx:02d}"
                original_path, thumbnail_path = ImageProcessor.download_and_save(
                    url,
                    record_id=sub_id,
                    create_thumbnail=True,
                )
                
                results.append({
                    "url": url,
                    "original_path": original_path,
                    "thumbnail_path": thumbnail_path,
                    "success": True,
                })
            except Exception as e:
                logger.error(f"Failed to download image {idx}: {e}")
                results.append({
                    "url": url,
                    "original_path": "",
                    "thumbnail_path": "",
                    "success": False,
                    "error": str(e),
                })
        
        return results