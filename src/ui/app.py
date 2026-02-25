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
    
    if "selected_record_id" not in st.session_state:
        st.session_state.selected_record_id = None


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
    
    # 检查 API Key 是否配置
    config_manager = st.session_state.config_manager
    api_key = config_manager.get_api_key()
    has_api_key = api_key is not None and api_key != ""
    
    # 如果没有配置 API Key，显示弹窗提示
    if not has_api_key:
        with st.expander("⚠️ 请先配置 API Key", expanded=True):
            st.warning("""
            为了使用 AI 绘图功能，您需要先配置 ModelScope API Key。
            
            **如何获取 API Key：**
            1. 访问 [ModelScope 官网](https://modelscope.cn/)
            2. 注册并登录账号
            3. 进入个人中心 → API Keys
            4. 点击"创建新的 API Key"
            5. 复制生成的 API Key
            
            配置完成后，请滚动到页面最下方的"API 配置"区域进行配置。
            """)
    
# 自定义 CSS
    st.markdown("""
        <style>
        .stApp {
            background-color: #f5f5f5;
        }
        .main-header {
            background: linear-gradient(95deg, #644cfd 0%, #cdc5ff 100%);
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
        /* 自定义 secondary 按钮颜色 - 生图按钮和保存API Key按钮 */
        div[data-testid="stForm"] button[kind="secondary"] {
            background-color: #644cfd;
            color: white;
        }
        div[data-testid="stForm"] button[kind="secondary"]:hover {
            background-color: #5a42f0;
        }
        button[kind="secondary"] {
            background-color: #644cfd !important;
            color: white !important;
        }
        button[kind="secondary"]:hover {
            background-color: #5a42f0 !important;
        }
        /* 确保 primary 按钮显示为白色 */
        button[kind="primary"] {
            background-color: white !important;
            color: #644cfd !important;
            border: 1px solid #cecece;
        }
        button[kind="primary"]:hover {
            background-color: #f0f0f0 !important;
            border: 1px solid #644cfd;
        }
        /* 隐藏图片的 fullscreen 按钮 */
        button[data-testid="stFullScreenButton"] {
            display: none !important;
        }
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