"""
ModelScope Image Generator - 主应用
"""
import streamlit as st
from streamlit.components.v1 import html

from src.core.config_manager import ConfigManager
from src.core.history_manager import HistoryManager
from src.utils.logger import get_logger

logger = get_logger("app")


def init_session_state():
    """初始化会话状态"""
    if "config_manager" not in st.session_state:
        st.session_state.config_manager = ConfigManager()
    
    if "history_manager" not in st.session_state:
        st.session_state.history_manager = HistoryManager()
    
    if "current_task" not in st.session_state:
        st.session_state.current_task = None
    
    if "task_status" not in st.session_state:
        st.session_state.task_status = "idle"
    
    if "should_generate" not in st.session_state:
        st.session_state.should_generate = False
    
    if "params" not in st.session_state:
        st.session_state.params = {
            "prompt": "",
            "negative_prompt": "",
            "model": "Tongyi-MAI/Z-Image-Turbo",
            "size": "1024x1024",
            "steps": 20,
            "guidance_scale": 3.0,
            "seed": -1,
        }


def set_page_config():
    """设置页面配置"""
    st.set_page_config(
        page_title="ModelScope Image Generator",
        page_icon="🎨",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def main():
    """主函数"""
    set_page_config()
    init_session_state()
    
    # 自定义 CSS
    st.markdown("""
        <style>
        .stApp {
            background-color: #f5f5f5;
        }
        .main-header {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            color: white;
        }
        .status-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.875rem;
            font-weight: 500;
        }
        .status-idle { background-color: #e5e7eb; color: #374151; }
        .status-pending { background-color: #fef3c7; color: #92400e; }
        .status-processing { background-color: #dbeafe; color: #1e40af; }
        .status-succeed { background-color: #d1fae5; color: #065f46; }
        .status-failed { background-color: #fee2e2; color: #991b1b; }
        </style>
    """, unsafe_allow_html=True)
    
    # 页面标题
    st.markdown("""
        <div class="main-header">
            <h1 style="margin: 0; font-size: 1.8rem;">🎨 ModelScope Image Generator</h1>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">AI 绘图助手 - 基于 ModelScope API</p>
        </div>
    """, unsafe_allow_html=True)
    
    # 主布局
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # 左侧栏：参数控制区
        from src.ui.components.sidebar import render_sidebar
        render_sidebar()
    
    with col2:
        # 右侧主区域：历史生图区
        from src.ui.components.main_area import render_main_area
        render_main_area()


if __name__ == "__main__":
    main()