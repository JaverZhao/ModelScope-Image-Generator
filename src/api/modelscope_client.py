"""
ModelScope API 客户端
"""
import json
import time
from typing import Dict, List, Optional, Any
import requests

from src.api.exceptions import (
    APIKeyInvalidError,
    TaskFailedError,
    NetworkError,
    QuotaExceededError,
    ContentViolationError,
    TimeoutError,
)
from src.config.settings import (
    API_BASE_URL,
    DEFAULT_TIMEOUT,
    POLL_INTERVAL,
    MAX_RETRY_COUNT,
)
from src.utils.logger import get_logger

logger = get_logger("modelscope-client")


class ModelScopeClient:
    """ModelScope API 客户端类"""
    
    ERROR_CODE_MAP = {
        401: APIKeyInvalidError,
        402: QuotaExceededError,
        400: ContentViolationError,
    }
    
    def __init__(self, api_key: str):
        """
        初始化客户端
        
        Args:
            api_key: ModelScope API Key
        """
        self.api_key = api_key
        self.base_url = API_BASE_URL
        self._common_headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        logger.info("ModelScopeClient initialized")
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: int = 30,
    ) -> Dict:
        """
        发送 HTTP 请求
        
        Args:
            method: HTTP 方法 (GET, POST)
            endpoint: API 端点
            data: 请求数据
            params: URL 参数
            headers: 额外的请求头
            timeout: 超时时间（秒）
            
        Returns:
            响应数据
            
        Raises:
            NetworkError: 网络错误
            TimeoutError: 超时错误
        """
        url = f"{self.base_url}{endpoint}"
        request_headers = {**self._common_headers}
        if headers:
            request_headers.update(headers)
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=request_headers,
                json=data,
                params=params,
                timeout=timeout,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout: {url}")
            raise TimeoutError(f"请求超时：{url}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise NetworkError(f"网络请求失败：{str(e)}")
    
    def submit_generation_task(
        self,
        model: str,
        prompt: str,
        negative_prompt: Optional[str] = None,
        size: str = "1024x1024",
        steps: int = 20,
        guidance_scale: float = 3.0,
        seed: int = -1,
        loras: Optional[Dict[str, float]] = None,
    ) -> str:
        """
        提交生图任务
        
        Args:
            model: 模型 ID
            prompt: 提示词
            negative_prompt: 负面提示词
            size: 图片尺寸
            steps: 步数
            guidance_scale: 引导系数
            seed: 随机种子
            loras: LoRA 模型配置
            
        Returns:
            任务 ID
            
        Raises:
            APIKeyInvalidError: API Key 无效
            QuotaExceededError: 余额不足
            ContentViolationError: 内容违规
            NetworkError: 网络错误
        """
        data = {
            "model": model,
            "prompt": prompt,
            "size": size,
        }
        
        if negative_prompt:
            data["negative_prompt"] = negative_prompt
        
        if steps != 20:
            data["steps"] = steps
        
        if guidance_scale != 3.0:
            data["guidance_scale"] = guidance_scale
        
        if seed != -1:
            data["seed"] = seed
        
        if loras:
            data["loras"] = loras
        
        logger.info(f"Submitting generation task: model={model}, prompt={prompt[:50]}...")
        
        try:
            response = self._make_request(
                method="POST",
                endpoint="v1/images/generations",
                data=data,
                headers={"X-ModelScope-Async-Mode": "true"},
            )
            task_id = response.get("task_id")
            logger.info(f"Task submitted successfully: {task_id}")
            return task_id
        except NetworkError as e:
            if hasattr(e, '__cause__') and e.__cause__:
                status_code = getattr(e.__cause__, 'response', None)
                if status_code and hasattr(status_code, 'status_code'):
                    error_code = status_code.status_code
                    error_class = self.ERROR_CODE_MAP.get(error_code)
                    if error_class:
                        raise error_class(f"API 错误 (HTTP {error_code})")
            raise
    
    def query_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        查询任务状态
        
        Args:
            task_id: 任务 ID
            
        Returns:
            任务状态字典
            
        Raises:
            TaskFailedError: 任务失败
            NetworkError: 网络错误
        """
        logger.debug(f"Querying task status: {task_id}")
        
        try:
            response = self._make_request(
                method="GET",
                endpoint=f"v1/tasks/{task_id}",
                headers={"X-ModelScope-Task-Type": "image_generation"},
            )
            return response
        except NetworkError as e:
            logger.error(f"Failed to query task status: {e}")
            raise
    
    def wait_for_completion(
        self,
        task_id: str,
        timeout: int = DEFAULT_TIMEOUT,
        poll_interval: int = POLL_INTERVAL,
    ) -> Dict[str, Any]:
        """
        轮询等待任务完成
        
        Args:
            task_id: 任务 ID
            timeout: 超时时间（秒）
            poll_interval: 轮询间隔（秒）
            
        Returns:
            完成状态和图片 URL
            
        Raises:
            TaskFailedError: 任务失败
            TimeoutError: 超时
        """
        logger.info(f"Waiting for task completion: {task_id}, timeout={timeout}s")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                result = self.query_task_status(task_id)
                task_status = result.get("task_status", "UNKNOWN")
                
                logger.debug(f"Task status: {task_status}")
                
                if task_status == "SUCCEED":
                    output_images = result.get("output_images", [])
                    logger.info(f"Task succeeded: {task_id}, images: {len(output_images)}")
                    return {
                        "status": "SUCCEED",
                        "task_id": task_id,
                        "output_images": output_images,
                    }
                elif task_status == "FAILED":
                    error_message = result.get("error_message", "Unknown error")
                    logger.error(f"Task failed: {task_id}, error: {error_message}")
                    raise TaskFailedError(f"任务失败：{error_message}")
                
                time.sleep(poll_interval)
                
            except NetworkError:
                # 网络错误时继续轮询
                logger.warning("Network error while polling, retrying...")
                time.sleep(poll_interval)
        
        raise TimeoutError(f"任务超时（{timeout}秒）：{task_id}")