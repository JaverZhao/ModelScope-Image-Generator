"""
左侧栏组件
"""
import streamlit as st
from src.ui.components.api_config import render_api_config
from src.ui.components.generation_params import render_generation_params
from src.ui.components.generate_button import render_generate_button
from src.utils.logger import get_logger

logger = get_logger("sidebar")


def render_sidebar():
    """渲染左侧栏"""
    with st.container():
        # API 配置
        render_api_config()
        
        st.divider()
        
        # 生图参数
        is_valid = render_generation_params()
        
        st.divider()
        
        # 生图按钮
        if is_valid:
            render_generate_button()
        
        st.divider()
        
        # 统计信息
        history_manager = st.session_state.history_manager
        stats = history_manager.get_stats()
        
        st.subheader("📊 统计信息")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("总数", stats["total"])
            st.metric("成功", stats["succeed"], delta_color="normal")
        with col2:
            st.metric("处理中", stats["processing"])
            st.metric("失败", stats["failed"], delta_color="inverse")