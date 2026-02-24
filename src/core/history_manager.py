"""
历史记录管理模块
"""
import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

from src.config.settings import HISTORY_FILE, MAX_HISTORY_RECORDS
from src.utils.logger import get_logger

logger = get_logger("history-manager")


class HistoryManager:
    """历史记录管理器"""
    
    def __init__(self):
        self.history_file = HISTORY_FILE
        self.records: List[Dict[str, Any]] = []
        self._load_records()
    
    def _load_records(self) -> None:
        """加载历史记录"""
        if not os.path.exists(self.history_file):
            logger.info("History file not found, creating empty records")
            self.records = []
            self._save_records()
            return
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.records = data.get("records", [])
            logger.info(f"Loaded {len(self.records)} history records")
        except Exception as e:
            logger.error(f"Failed to load history: {e}")
            self.records = []
    
    def _save_records(self) -> bool:
        """
        保存历史记录
        
        Returns:
            是否保存成功
        """
        try:
            data = {
                "records": self.records,
                "total_count": len(self.records),
                "last_updated": datetime.now().isoformat(),
            }
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug("History saved successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to save history: {e}")
            return False
    
    def create_record(
        self,
        prompt: str,
        model: str,
        size: str,
        task_id: Optional[str] = None,
        negative_prompt: Optional[str] = None,
        steps: int = 20,
        guidance_scale: float = 3.0,
        seed: int = -1,
    ) -> str:
        """
        创建历史记录
        
        Args:
            prompt: 提示词
            model: 模型
            size: 尺寸
            task_id: 任务 ID
            negative_prompt: 负面提示词
            steps: 步数
            guidance_scale: 引导系数
            seed: 随机种子
            
        Returns:
            记录 ID
        """
        record_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        record = {
            "id": record_id,
            "task_id": task_id or "",
            "prompt": prompt,
            "negative_prompt": negative_prompt or "",
            "model": model,
            "size": size,
            "steps": steps,
            "guidance_scale": guidance_scale,
            "seed": seed,
            "status": "pending",
            "created_at": now,
            "completed_at": None,
            "original_path": "",
            "thumbnail_path": "",
            "error_message": None,
        }
        
        self.records.insert(0, record)  # 插入到开头
        self._save_records()
        logger.info(f"Created history record: {record_id}")
        return record_id
    
    def update_record(
        self,
        record_id: str,
        status: Optional[str] = None,
        task_id: Optional[str] = None,
        original_path: Optional[str] = None,
        thumbnail_path: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> bool:
        """
        更新历史记录
        
        Args:
            record_id: 记录 ID
            status: 状态
            task_id: 任务 ID
            original_path: 原图路径
            thumbnail_path: 缩略图路径
            error_message: 错误消息
            
        Returns:
            是否更新成功
        """
        for record in self.records:
            if record["id"] == record_id:
                if status is not None:
                    record["status"] = status
                    if status in ["succeed", "failed"]:
                        record["completed_at"] = datetime.now().isoformat()
                if task_id is not None:
                    record["task_id"] = task_id
                if original_path is not None:
                    record["original_path"] = original_path
                if thumbnail_path is not None:
                    record["thumbnail_path"] = thumbnail_path
                if error_message is not None:
                    record["error_message"] = error_message
                
                self._save_records()
                logger.info(f"Updated history record: {record_id}")
                return True
        
        logger.warning(f"Record not found: {record_id}")
        return False
    
    def get_record_by_id(self, record_id: str) -> Optional[Dict[str, Any]]:
        """
        根据记录 ID 获取记录
        
        Args:
            record_id: 记录 ID
            
        Returns:
            记录字典，如果未找到则返回 None
        """
        for record in self.records:
            if record["id"] == record_id:
                return record
        return None
    
    def get_records(
        self,
        page: int = 1,
        page_size: int = 20,
        status_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        获取记录列表（分页）
        
        Args:
            page: 页码（从 1 开始）
            page_size: 每页数量
            status_filter: 状态过滤
            
        Returns:
            记录列表
        """
        records = self.records
        
        if status_filter:
            records = [r for r in records if r["status"] == status_filter]
        
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        return records[start_idx:end_idx]
    
    def search_records(self, keyword: str) -> List[Dict[str, Any]]:
        """
        搜索记录
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            匹配的记录列表
        """
        keyword = keyword.lower()
        results = []
        
        for record in self.records:
            if (keyword in record["prompt"].lower() or
                keyword in record["model"].lower() or
                keyword in str(record["created_at"]).lower()):
                results.append(record)
        
        return results
    
    def delete_record(self, record_id: str) -> bool:
        """
        删除记录（包括关联的图片文件）
        
        Args:
            record_id: 记录 ID
            
        Returns:
            是否删除成功
        """
        record = self.get_record_by_id(record_id)
        if not record:
            logger.warning(f"Record not found: {record_id}")
            return False
        
        # 删除关联的图片文件
        for path in [record["original_path"], record["thumbnail_path"]]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                    logger.info(f"Deleted image file: {path}")
                except Exception as e:
                    logger.error(f"Failed to delete image file {path}: {e}")
        
        # 删除记录
        self.records = [r for r in self.records if r["id"] != record_id]
        self._save_records()
        logger.info(f"Deleted history record: {record_id}")
        return True
    
    def get_stats(self) -> Dict[str, int]:
        """
        获取统计信息
        
        Returns:
            统计信息字典
        """
        total = len(self.records)
        pending = len([r for r in self.records if r["status"] == "pending"])
        processing = len([r for r in self.records if r["status"] == "processing"])
        succeed = len([r for r in self.records if r["status"] == "succeed"])
        failed = len([r for r in self.records if r["status"] == "failed"])
        
        return {
            "total": total,
            "pending": pending,
            "processing": processing,
            "succeed": succeed,
            "failed": failed,
        }
    
    def _cleanup_old_records(self) -> None:
        """清理旧记录（如果超过最大数量）"""
        if len(self.records) > MAX_HISTORY_RECORDS:
            # 保留最近的记录
            self.records = self.records[:MAX_HISTORY_RECORDS]
            self._save_records()
            logger.info(f"Cleaned up old records, kept {MAX_HISTORY_RECORDS}")