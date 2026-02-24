"""
主区域组件
"""
import streamlit as st
from src.ui.components.history_gallery import render_history_gallery
from src.utils.logger import get_logger

logger = get_logger("main-area")


def render_main_area():
    """渲染主区域"""
    # 历史生图区
    render_history_gallery()