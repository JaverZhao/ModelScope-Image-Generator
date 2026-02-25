"""
生图按钮和进度显示组件
"""
import streamlit as st
from src.api.exceptions import (
    APIKeyInvalidError,
    QuotaExceededError,
    ContentViolationError,
    NetworkError,
    TimeoutError,
)
from src.core.config_manager import ConfigManager
from src.core.generation_service import GenerationService
from src.utils.logger import get_logger

logger = get_logger("generate-button")


def render_generate_button():
    """渲染生图按钮和进度显示"""
    params = st.session_state.params
    
    # 检查参数有效性
    if not params["prompt"].strip():
        st.error("请输入提示词")
        return
    
    # 检查 API Key
    config_manager = st.session_state.config_manager
    api_key = config_manager.get_api_key()
    if not api_key:
        st.error("请先配置 API Key")
        return
    
    # 生图按钮
    generate_button = st.button(
        "🎨 生成图片",
        type="primary",
        use_container_width=True,
        disabled=st.session_state.task_status == "processing"
    )
    
    # 状态显示
    status_badge = {
        "idle": "空闲",
        "pending": "准备中",
        "processing": "生成中",
        "succeed": "完成",
        "failed": "失败"
    }
    
    status_color = {
        "idle": "status-idle",
        "pending": "status-pending",
        "processing": "status-processing",
        "succeed": "status-succeed",
        "failed": "status-failed"
    }
    
    if st.session_state.task_status != "idle":
        st.markdown(
            f'<span class="status-badge {status_color[st.session_state.task_status]}">状态: {status_badge[st.session_state.task_status]}</span>',
            unsafe_allow_html=True
        )
    
    # 进度条
    if st.session_state.task_status == "processing":
        st.progress(0.5, text="正在生成图片，请稍候...")
    
    # 处理生图请求 - 直接执行，不使用 rerun
    if generate_button and st.session_state.task_status != "processing":
        _execute_generation(api_key, params)


def _execute_generation(api_key: str, params: dict):
    """执行生图流程"""
    try:
        # 设置状态为 processing
        st.session_state.task_status = "processing"
        
        # 使用 GenerationService 执行完整流程
        logger.info("Starting generation process")
        service = GenerationService(api_key)
        
        result = service.generate_image(
            prompt=params["prompt"],
            model=params["model"],
            size=params["size"],
            negative_prompt=params["negative_prompt"] or None,
            steps=params["steps"],
            guidance_scale=params["guidance_scale"],
            seed=params["seed"],
        )
        
        if result["success"]:
            st.session_state.task_status = "succeed"
            st.success(f"✅ {result['message']}！")
            st.rerun()
    
    except APIKeyInvalidError:
        st.error("❌ API Key 无效，请检查配置")
        st.session_state.task_status = "failed"
    except QuotaExceededError:
        st.error("❌ 余额不足，请充值")
        st.session_state.task_status = "failed"
    except ContentViolationError:
        st.error("❌ 内容违规，请修改提示词")
        st.session_state.task_status = "failed"
    except NetworkError:
        st.error("❌ 网络错误，请检查网络连接")
        st.session_state.task_status = "failed"
    except TimeoutError:
        st.error("❌ 请求超时，请稍后重试")
        st.session_state.task_status = "failed"
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        st.error(f"❌ 未知错误：{str(e)}")
        st.session_state.task_status = "failed"