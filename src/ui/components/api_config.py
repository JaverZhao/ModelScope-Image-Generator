"""
API 配置界面组件
"""
import streamlit as st
from src.api.exceptions import APIKeyInvalidError, NetworkError
from src.api.modelscope_client import ModelScopeClient
from src.utils.logger import get_logger

logger = get_logger("api-config")


def render_api_config():
    """渲染 API 配置界面"""
    st.subheader("🔑 API 配置")
    
    config_manager = st.session_state.config_manager
    
    # 获取当前 API Key
    current_api_key = config_manager.get_api_key()
    
    # 显示配置状态
    if current_api_key:
        st.success("✅ API Key 已配置")
    else:
        st.warning("⚠️ API Key 未配置")
    
    st.divider()
    
    # API Key 输入框
    with st.form("api_key_form"):
        api_key_input = st.text_input(
            "API Key",
            value="",
            type="password",
            placeholder="请输入您的 ModelScope API Key",
            help="获取方式：访问 https://modelscope.cn/ 注册账号并获取 API Key"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            save_button = st.form_submit_button("保存 API Key", type="primary")
        with col2:
            test_button = st.form_submit_button("测试连接")
    
    # 保存 API Key
    if save_button:
        if not api_key_input.strip():
            st.error("请输入 API Key")
        else:
            if config_manager.set_api_key(api_key_input):
                st.success("API Key 保存成功！")
                st.rerun()
            else:
                st.error("API Key 保存失败")
    
    # 测试连接
    if test_button:
        api_key_to_test = api_key_input if api_key_input.strip() else current_api_key
        
        if not api_key_to_test:
            st.error("请先输入或配置 API Key")
        else:
            with st.spinner("正在测试连接..."):
                try:
                    is_valid, message = config_manager.validate_api_key(api_key_to_test)
                    if is_valid:
                        st.success(f"✅ {message}")
                    else:
                        st.error(f"❌ {message}")
                except Exception as e:
                    st.error(f"测试失败：{str(e)}")
    
    st.divider()
    
    # 帮助信息
    with st.expander("💡 如何获取 API Key？"):
        st.markdown("""
        1. 访问 [ModelScope 官网](https://modelscope.cn/)
        2. 注册并登录账号
        3. 进入个人中心 → API Keys
        4. 点击"创建新的 API Key"
        5. 复制生成的 API Key 并粘贴到上方输入框
        """)
    
    # 删除 API Key
    if current_api_key:
        if st.button("🗑️ 删除 API Key", type="secondary"):
            if config_manager.set_api_key(""):
                st.success("API Key 已删除")
                st.rerun()
            else:
                st.error("删除失败")