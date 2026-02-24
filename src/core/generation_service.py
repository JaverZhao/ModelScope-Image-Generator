"""
生图业务流程控制器
"""
from typing import Dict, Any, Optional
from src.api.modelscope_client import ModelScopeClient
from src.api.exceptions import (
    APIKeyInvalidError,
    NetworkError,
    TaskFailedError,
    TimeoutError,
    QuotaExceededError,
    ContentViolationError,
)
from src.core.history_manager import HistoryManager
from src.utils.image_processor import ImageProcessor
from src.utils.logger import get_logger

logger = get_logger("generation-service")


class GenerationService:
    """生图服务类"""
    
    def __init__(self, api_key: str):
        """
        初始化生图服务
        
        Args:
            api_key: ModelScope API Key
        """
        self.api_key = api_key
        self.client = ModelScopeClient(api_key)
        self.history_manager = HistoryManager()
        self.image_processor = ImageProcessor()
        logger.info("GenerationService initialized")
    
    def generate_image(
        self,
        prompt: str,
        model: str,
        size: str,
        negative_prompt: Optional[str] = None,
        steps: int = 20,
        guidance_scale: float = 3.0,
        seed: int = -1,
    ) -> Dict[str, Any]:
        """
        执行完整生图流程
        
        Args:
            prompt: 提示词
            model: 模型 ID
            size: 图片尺寸
            negative_prompt: 负面提示词
            steps: 步数
            guidance_scale: 引导系数
            seed: 随机种子
            
        Returns:
            生图结果字典
            
        Raises:
            各种 API 异常
        """
        logger.info(f"Starting image generation: model={model}, prompt={prompt[:50]}...")
        
        record_id = None
        try:
            # 1. 验证参数
            if not prompt.strip():
                raise ValueError("提示词不能为空")
            
            # 2. 创建历史记录（状态：pending）
            record_id = self.history_manager.create_record(
                prompt=prompt,
                model=model,
                size=size,
                negative_prompt=negative_prompt,
                steps=steps,
                guidance_scale=guidance_scale,
                seed=seed,
            )
            logger.info(f"Created history record: {record_id}")
            
            # 3. 提交 API 任务
            task_id = self.client.submit_generation_task(
                model=model,
                prompt=prompt,
                negative_prompt=negative_prompt or None,
                size=size,
                steps=steps,
                guidance_scale=guidance_scale,
                seed=seed,
            )
            logger.info(f"Submitted API task: {task_id}")
            
            # 4. 更新历史记录（状态：processing）
            self.history_manager.update_record(record_id, task_id=task_id, status="processing")
            
            # 5. 轮询任务状态
            result = self.client.wait_for_completion(task_id)
            
            if result["status"] == "SUCCEED":
                # 6. 下载图片
                output_images = result.get("output_images", [])
                if not output_images:
                    raise TaskFailedError("未返回生成的图片")
                
                image_url = output_images[0]
                logger.info(f"Downloading image from: {image_url}")
                
                # 7. 按日期创建文件夹并保存图片
                original_path, thumbnail_path = self.image_processor.download_and_save(
                    image_url,
                    record_id=record_id,
                    create_thumbnail=True
                )
                logger.info(f"Saved images: {original_path}, {thumbnail_path}")
                
                # 8. 更新历史记录（状态：succeed）
                self.history_manager.update_record(
                    record_id,
                    status="succeed",
                    original_path=original_path,
                    thumbnail_path=thumbnail_path
                )
                
                logger.info(f"Image generation succeeded: {record_id}")
                
                return {
                    "success": True,
                    "record_id": record_id,
                    "original_path": original_path,
                    "thumbnail_path": thumbnail_path,
                    "message": "图片生成成功",
                }
            else:
                raise TaskFailedError(f"任务状态异常：{result.get('status')}")
        
        except (APIKeyInvalidError, QuotaExceededError, ContentViolationError,
                NetworkError, TimeoutError, TaskFailedError) as e:
            # 记录错误到历史记录
            if record_id:
                self.history_manager.update_record(
                    record_id,
                    status="failed",
                    error_message=str(e)
                )
            logger.error(f"Image generation failed: {e}")
            raise
        
        except Exception as e:
            # 记录未知错误到历史记录
            if record_id:
                self.history_manager.update_record(
                    record_id,
                    status="failed",
                    error_message=f"未知错误：{str(e)}"
                )
            logger.error(f"Unknown error during generation: {e}")
            raise RuntimeError(f"生图失败：{str(e)}")
    
    def get_generation_status(self, record_id: str) -> Optional[Dict[str, Any]]:
        """
        获取生图状态
        
        Args:
            record_id: 记录 ID
            
        Returns:
            记录信息字典
        """
        return self.history_manager.get_record_by_id(record_id)
    
    def cancel_generation(self, record_id: str) -> bool:
        """
        取消生图任务（标记为失败）
        
        Args:
            record_id: 记录 ID
            
        Returns:
            是否取消成功
        """
        record = self.history_manager.get_record_by_id(record_id)
        if not record:
            return False
        
        if record["status"] in ["pending", "processing"]:
            return self.history_manager.update_record(
                record_id,
                status="failed",
                error_message="用户取消"
            )
        
        return False