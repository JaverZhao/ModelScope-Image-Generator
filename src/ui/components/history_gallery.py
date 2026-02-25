"""
历史生图区界面组件
"""
import streamlit as st
import os
from datetime import datetime
from src.utils.logger import get_logger

logger = get_logger("history-gallery")


def render_history_gallery():
    """渲染历史生图区"""
    st.subheader("🖼️ 历史记录")
    
    history_manager = st.session_state.history_manager
    
    # 获取记录
    records = history_manager.get_records(page=1, page_size=50)
    
    if not records:
        st.info("暂无历史记录，开始生成您的第一张图片吧！")
        return
    
    # 筛选
    with st.expander("🔍 筛选"):
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.selectbox(
                "状态筛选",
                options=["全部", "pending", "processing", "succeed", "failed"],
                index=0
            )
        with col2:
            keyword = st.text_input("搜索关键词", placeholder="搜索提示词...")
        
        if st.button("应用筛选"):
            st.rerun()
    
    # 过滤记录
    filtered_records = records
    if status_filter != "全部":
        filtered_records = [r for r in filtered_records if r["status"] == status_filter]
    if keyword:
        filtered_records = [r for r in filtered_records if keyword.lower() in r["prompt"].lower()]
    
    if not filtered_records:
        st.info("没有匹配的记录")
        return
    
    # 显示记录
    cols_per_row = 4
    for i in range(0, len(filtered_records), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            if i + j < len(filtered_records):
                record = filtered_records[i + j]
                _render_image_card(col, record)
    
    # 分页
    if len(records) >= 50:
        st.info("仅显示最近 50 条记录，完整记录请查看历史文件")


def _render_image_card(col, record: dict):
    """渲染图片卡片"""
    thumbnail_path = record.get("thumbnail_path", "")
    prompt = record.get("prompt", "")
    created_at = record.get("created_at", "")
    status = record.get("status", "")
    record_id = record.get("id", "")
    
    # 格式化时间
    if created_at:
        try:
            dt = datetime.fromisoformat(created_at)
            time_str = dt.strftime("%Y-%m-%d %H:%M")
        except:
            time_str = created_at
    else:
        time_str = ""
    
    # 状态颜色
    status_colors = {
        "pending": "🟡",
        "processing": "🔵",
        "succeed": "🟢",
        "failed": "🔴",
    }
    status_icon = status_colors.get(status, "⚪")
    
    with col:
        # 缩略图
        if thumbnail_path and os.path.exists(thumbnail_path):
            st.image(thumbnail_path, use_container_width=True)
        else:
            st.markdown(f'<div style="background:#f0f0f0;height:200px;display:flex;align-items:center;justify-content:center;border-radius:8px;">{status_icon}</div>', unsafe_allow_html=True)
        
        # 信息
        prompt_preview = prompt[:30] + "..." if len(prompt) > 30 else prompt
        
        st.markdown(f"""
        <div style="font-size:0.85rem;margin-top:0.5rem;">
            <strong>{status_icon} {prompt_preview}</strong><br>
            <span style="color:#666;">{time_str}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # 操作按钮
        if status == "succeed":
            if st.button("查看详情", key=f"view_{record_id}", width="stretch", type="primary"):
                _show_image_detail(record)
        
        if st.button("删除", key=f"del_{record_id}", width="stretch", type="primary"):
            history_manager = st.session_state.history_manager
            if history_manager.delete_record(record_id):
                st.success("删除成功")
                st.rerun()


def _show_image_detail(record: dict):
    """显示图片详情弹窗"""
    with st.expander(f"图片详情 - {record['prompt'][:20]}...", expanded=True):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 大图
            original_path = record.get("original_path", "")
            if original_path and os.path.exists(original_path):
                st.image(original_path, use_container_width=True)
            else:
                st.info("图片文件不存在")
        
        with col2:
            # 信息
            st.markdown("### 📋 详细信息")
            st.write(f"**模型**: {record.get('model', '')}")
            st.write(f"**尺寸**: {record.get('size', '')}")
            st.write(f"**步数**: {record.get('steps', '')}")
            st.write(f"**引导系数**: {record.get('guidance_scale', '')}")
            st.write(f"**种子**: {record.get('seed', '')}")
            
            st.divider()
            
            st.markdown("### ✍️ 提示词")
            st.text_area("Prompt", record.get("prompt", ""), height=100, disabled=True, label_visibility="collapsed")
            
            if record.get("negative_prompt"):
                st.text_area("Negative Prompt", record.get("negative_prompt", ""), height=80, disabled=True, label_visibility="collapsed")
            
            st.divider()
            
            # 操作
            original_path = record.get("original_path", "")
            if original_path and os.path.exists(original_path):
                with open(original_path, "rb") as f:
                    st.download_button(
                        "📥 下载原图",
                        f,
                        file_name=f"image_{record['id']}.jpg",
                        mime="image/jpeg",
                        width="content"
                    )
            
            if st.button("🔄 复用参数", key=f"reuse_{record['id']}", width="stretch", type="primary"):
                st.session_state.params.update({
                    "prompt": record.get("prompt", ""),
                    "negative_prompt": record.get("negative_prompt", ""),
                    "model": record.get("model", ""),
                    "size": record.get("size", ""),
                    "steps": record.get("steps", 20),
                    "guidance_scale": record.get("guidance_scale", 3.0),
                    "seed": record.get("seed", -1),
                })
                st.success("参数已复用到左侧输入框")
                st.rerun()