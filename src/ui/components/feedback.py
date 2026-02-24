"""
反馈机制组件
"""
import streamlit as st
from src.utils.logger import get_logger

logger = get_logger("feedback")


def show_success(message: str, duration: int = 3):
    """显示成功消息"""
    st.toast(f"✅ {message}", icon="✅")


def show_warning(message: str, duration: int = 3):
    """显示警告消息"""
    st.toast(f"⚠️ {message}", icon="⚠️")


def show_error(message: str, duration: int = 5):
    """显示错误消息"""
    st.toast(f"❌ {message}", icon="❌")


def show_info(message: str, duration: int = 3):
    """显示信息消息"""
    st.toast(f"ℹ️ {message}", icon="ℹ️")


def handle_api_error(error: Exception):
    """处理 API 错误"""
    error_messages = {
        "APIKeyInvalidError": "API Key 无效，请检查配置",
        "QuotaExceededError": "余额不足，请充值后重试",
        "ContentViolationError": "内容违规，请修改提示词",
        "NetworkError": "网络错误，请检查网络连接",
        "TimeoutError": "请求超时，请稍后重试",
        "TaskFailedError": "任务失败，请稍后重试",
    }
    
    error_type = type(error).__name__
    message = error_messages.get(error_type, str(error))
    
    show_error(message)
    logger.error(f"API error: {error_type} - {message}")


def show_status_indicator(status: str):
    """显示状态指示器"""
    status_config = {
        "idle": {"icon": "⚪", "text": "空闲", "color": "#6b7280"},
        "pending": {"icon": "🟡", "text": "准备中", "color": "#f59e0b"},
        "processing": {"icon": "🔵", "text": "生成中", "color": "#3b82f6"},
        "succeed": {"icon": "🟢", "text": "完成", "color": "#10b981"},
        "failed": {"icon": "🔴", "text": "失败", "color": "#ef4444"},
    }
    
    config = status_config.get(status, status_config["idle"])
    
    st.markdown(
        f"""
        <div style="display:inline-flex;align-items:center;gap:0.5rem;padding:0.5rem 1rem;
            background-color:rgba({int(config['color'][1:3],16)},{int(config['color'][3:5],16)},{int(config['color'][5:7],16)},0.1);
            border-radius:9999px;border:1px solid {config['color']};">
            <span style="font-size:1.2rem;">{config['icon']}</span>
            <span style="color:{config['color']};font-weight:500;">{config['text']}</span>
        </div>
        """,
        unsafe_allow_html=True
    )