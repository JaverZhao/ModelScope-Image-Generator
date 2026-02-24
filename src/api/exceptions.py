"""
API 异常类定义
"""


class ModelScopeAPIError(Exception):
    """ModelScope API 基础异常类"""
    pass


class APIKeyInvalidError(ModelScopeAPIError):
    """API Key 无效"""
    pass


class TaskFailedError(ModelScopeAPIError):
    """任务失败"""
    pass


class NetworkError(ModelScopeAPIError):
    """网络错误"""
    pass


class QuotaExceededError(ModelScopeAPIError):
    """余额不足"""
    pass


class ContentViolationError(ModelScopeAPIError):
    """内容违规"""
    pass


class TimeoutError(ModelScopeAPIError):
    """请求超时"""
    pass