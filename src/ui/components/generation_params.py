"""
生图参数控制界面组件
"""
import streamlit as st
from src.utils.logger import get_logger

logger = get_logger("generation-params")


# 模型列表
MODELS = [
    "Tongyi-MAI/Z-Image-Turbo",
    "Tongyi-MAI/Z-Image",
    "Qwen/Qwen-Image-2512",
    "JaverZhao/JaverMix_CUTEbread",
    "JaverZhao/JaverMix_CUTE_REAL_bread",
]

# 尺寸预设
SIZE_PRESETS = {
    "标准": ["512x512", "768x1024", "640x480", "640x360", "360x640", "720x480", "480x720", "840x360"],
    "高清": ["1024x1024", "1152x1536", "1536x1152", "1920x1080", "1080x1920", "1536x1024", "1024x1536", "1680x720"],
    "超清": ["2048x2048", "1536x2048", "2048x1536", "2048x1152", "1152x2048", "2048x1365", "1365x2048", "2048x876"],
}


def render_generation_params():
    """渲染生图参数控制界面"""
    st.subheader("🎛️ 生图参数")
    
    # Prompt
    prompt = st.text_area(
        "Prompt (提示词)",
        value=st.session_state.params["prompt"],
        placeholder="描述您想要生成的图片...",
        height=120,
        help="详细描述您想要生成的图片内容，支持中英文"
    )
    st.session_state.params["prompt"] = prompt
    
    # Negative Prompt
    with st.expander("Negative Prompt (负面提示词)"):
        negative_prompt = st.text_area(
            "负面提示词",
            value=st.session_state.params["negative_prompt"],
            placeholder="描述您不希望出现的元素...",
            height=80,
            help="描述您不希望出现在图片中的内容"
        )
        st.session_state.params["negative_prompt"] = negative_prompt
    
    st.divider()
    
    # 模型选择
    model_option = st.selectbox(
        "模型",
        options=MODELS + ["自定义模型ID"],
        index=0 if st.session_state.params["model"] in MODELS else len(MODELS),
        help="选择要使用的 AI 绘图模型"
    )
    
    if model_option == "自定义模型ID":
        custom_model = st.text_input(
            "自定义模型ID",
            value=st.session_state.params["model"] if st.session_state.params["model"] not in MODELS else "",
            placeholder="输入模型 ID，如: Tongyi-MAI/Z-Image-Turbo"
        )
        model = custom_model if custom_model.strip() else MODELS[0]
    else:
        model = model_option
    
    st.session_state.params["model"] = model
    
    # 尺寸选择
    size_category = st.selectbox(
        "尺寸类别",
        options=list(SIZE_PRESETS.keys()),
        index=1
    )
    
    sizes = SIZE_PRESETS[size_category]
    size_option = st.selectbox(
        "尺寸",
        options=sizes + ["自定义尺寸"],
        index=0 if st.session_state.params["size"] in sizes else len(sizes)
    )
    
    if size_option == "自定义尺寸":
        col1, col2 = st.columns(2)
        with col1:
            width = st.number_input(
                "宽度",
                min_value=64,
                max_value=2048,
                value=1024,
                step=16,
                help="图片宽度，必须是 16 的倍数"
            )
        with col2:
            height = st.number_input(
                "高度",
                min_value=64,
                max_value=2048,
                value=1024,
                step=16,
                help="图片高度，必须是 16 的倍数"
            )
        size = f"{int(width)}x{int(height)}"
        
        # 宽高互换
        if st.button("🔄 互换宽高"):
            st.session_state.params["size"] = f"{int(height)}x{int(width)}"
            st.rerun()
    else:
        size = size_option
    
    st.session_state.params["size"] = size
    
    st.divider()
    
    # 高级设置
    with st.expander("⚙️ 高级设置"):
        # Steps
        steps = st.slider(
            "Steps (步数)",
            min_value=10,
            max_value=50,
            value=st.session_state.params["steps"],
            step=1,
            help="生成迭代次数，值越高质量越好但速度越慢"
        )
        st.session_state.params["steps"] = steps
        
        # Guidance Scale
        guidance_scale = st.slider(
            "Guidance Scale (引导系数)",
            min_value=1.0,
            max_value=10.0,
            value=st.session_state.params["guidance_scale"],
            step=0.5,
            help="引导系数，值越高越贴近提示词"
        )
        st.session_state.params["guidance_scale"] = guidance_scale
        
        # Seed
        seed = st.number_input(
            "Seed (随机种子)",
            value=st.session_state.params["seed"],
            min_value=-1,
            max_value=4294967295,
            step=1,
            help="指定具体数字可复现结果，-1 表示随机"
        )
        st.session_state.params["seed"] = seed
    
    # 参数验证提示
    if not prompt.strip():
        st.warning("⚠️ 请输入提示词")
    
    return prompt.strip() != ""