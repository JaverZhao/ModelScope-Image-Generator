"""
配置管理模块
"""
import json
import os
from typing import Dict, Any, Optional
import base64

from src.config.settings import CONFIG_FILE, ENV_FILE
from src.utils.logger import get_logger

logger = get_logger("config-manager")


DEFAULT_CONFIG = {
    "api_key": "",
    "default_model": "Tongyi-MAI/Z-Image-Turbo",
    "default_size": "1024x1024",
    "advanced_settings": {
        "steps": 20,
        "guidance_scale": 3.0,
        "seed": -1,
    },
    "ui_preferences": {
        "theme": "light",
        "auto_save_history": True,
    },
}


class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self.config_file = CONFIG_FILE
        self.config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """
        加载配置文件
        
        Returns:
            配置字典
        """
        if not os.path.exists(self.config_file):
            logger.info("Config file not found, creating default config")
            self.config = DEFAULT_CONFIG.copy()
            self.save_config()
            return self.config
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            logger.info("Config loaded successfully")
            
            # 合并默认配置（确保新字段存在）
            for key, value in DEFAULT_CONFIG.items():
                if key not in self.config:
                    self.config[key] = value
                elif isinstance(value, dict) and isinstance(self.config[key], dict):
                    for sub_key, sub_value in value.items():
                        if sub_key not in self.config[key]:
                            self.config[key][sub_key] = sub_value
            
            return self.config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            self.config = DEFAULT_CONFIG.copy()
            return self.config
    
    def save_config(self) -> bool:
        """
        保存配置文件
        
        Returns:
            是否保存成功
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logger.info("Config saved successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False
    
    def get_api_key(self) -> Optional[str]:
        """
        获取 API Key
        
        Returns:
            API Key，如果未设置则返回 None
        """
        # 优先从配置文件读取
        api_key = self.config.get("api_key", "")
        
        # 如果配置文件中没有，尝试从环境变量读取
        if not api_key:
            if os.path.exists(ENV_FILE):
                try:
                    from dotenv import load_dotenv
                    load_dotenv(ENV_FILE)
                    api_key = os.environ.get("MODELSCOPE_API_KEY", "")
                except Exception:
                    pass
        
        # 解密（如果使用了 base64 编码）
        if api_key:
            try:
                # 尝试解码，如果失败则返回原始值
                decoded = base64.b64decode(api_key).decode('utf-8')
                # 检查解码后的内容是否像是一个有效的 API Key
                if decoded.startswith('sk-') or len(decoded) > 20:
                    api_key = decoded
            except Exception:
                pass
        
        return api_key if api_key else None
    
    def set_api_key(self, api_key: str, encrypt: bool = True) -> bool:
        """
        设置 API Key
        
        Args:
            api_key: API Key
            encrypt: 是否加密存储
            
        Returns:
            是否设置成功
        """
        try:
            if encrypt and api_key:
                # 使用 base64 简单编码（不是真正的加密，但可以防止明文显示）
                api_key = base64.b64encode(api_key.encode('utf-8')).decode('utf-8')
            
            self.config["api_key"] = api_key
            return self.save_config()
        except Exception as e:
            logger.error(f"Failed to set API key: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any) -> bool:
        """
        设置配置项
        
        Args:
            key: 配置键
            value: 配置值
            
        Returns:
            是否设置成功
        """
        try:
            keys = key.split('.')
            config = self.config
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            config[keys[-1]] = value
            return self.save_config()
        except Exception as e:
            logger.error(f"Failed to set config: {e}")
            return False
    
    def validate_api_key(self, api_key: str) -> tuple[bool, str]:
        """
        验证 API Key 是否有效
        
        Args:
            api_key: API Key
            
        Returns:
            (是否有效, 错误消息)
        """
        try:
            from src.api.modelscope_client import ModelScopeClient
            client = ModelScopeClient(api_key)
            # 尝试查询一个不存在的任务来验证 API Key
            try:
                client.query_task_status("test_invalid_task_id")
            except Exception as e:
                # 如果是 401 错误，说明 API Key 无效
                if "401" in str(e) or "Unauthorized" in str(e):
                    return False, "API Key 无效"
                # 如果是网络错误但不是认证错误，说明 API Key 可能是有效的
                return True, "API Key 有效"
            
            # 如果没有抛出异常，说明 API Key 有效
            return True, "API Key 有效"
        except Exception as e:
            logger.error(f"Failed to validate API key: {e}")
            return False, f"验证失败：{str(e)}"