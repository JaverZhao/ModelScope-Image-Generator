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
    
    # 显示选中的图片详情（全屏弹窗）
    if st.session_state.get("selected_record_id"):
        selected_record = next((r for r in records if r["id"] == st.session_state.selected_record_id), None)
        if selected_record:
            _show_image_detail(selected_record)
            # 防止刷新后仍然显示弹窗
            st.session_state.selected_record_id = None


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
                st.session_state.selected_record_id = record_id
        
        if st.button("删除", key=f"del_{record_id}", width="stretch", type="primary"):
            history_manager = st.session_state.history_manager
            if history_manager.delete_record(record_id):
                st.success("删除成功")
                st.rerun()


def _show_image_detail(record: dict):
    """显示图片详情弹窗（简化版，使用原生布局）"""
    # 简单的 CSS 样式
    st.markdown("""
        <style>
        .detail-panel {
            background-color: #f5f5f5;
            padding: 1rem;
            border-radius: 10px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # 使用 expander 显示详情
    with st.expander(f"📷 {record.get('prompt', '')[:30]}...", expanded=True):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 显示原图
            original_path = record.get("original_path", "")
            if original_path and os.path.exists(original_path):
                st.image(original_path, use_container_width=True)
            else:
                st.info("图片文件不存在")
        
        with col2:
            # 信息面板
            st.markdown('<div class="detail-panel">', unsafe_allow_html=True)
            
            st.markdown(f"**Prompt:**")
            st.text(record.get("prompt", ""))
            
            st.markdown(f"**Negative Prompt:**")
            st.text(record.get("negative_prompt", "") or "无")
            
            st.markdown(f"**模型:**")
            st.text(record.get("model", ""))
            
            st.markdown(f"**尺寸:**")
            st.text(record.get("size", ""))
            
            st.markdown(f"**步数:**")
            st.text(record.get("steps", ""))
            
            st.markdown(f"**引导系数:**")
            st.text(record.get("guidance_scale", ""))
            
            st.markdown(f"**种子:**")
            st.text(record.get("seed", ""))
            
            st.markdown(f"**生成时间:**")
            created_at = record.get("created_at", "")
            if created_at:
                dt = datetime.fromisoformat(created_at)
                st.text(dt.strftime("%Y-%m-%d %H:%M:%S"))
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.divider()
            
            # 操作按钮
            if original_path and os.path.exists(original_path):
                with open(original_path, "rb") as f:
                    st.download_button(
                        "📥 下载原图",
                        f,
                        file_name=f"image_{record['id']}.jpg",
                        mime="image/jpeg",
                        width="stretch",
                        type="primary"
                    )
            
            if st.button("🔄 复用参数", key=f"reuse_full_{record['id']}", width="stretch", type="primary"):
                st.session_state.params.update({
                    "prompt": record.get("prompt", ""),
                    "negative_prompt": record.get("negative_prompt", ""),
                    "model": record.get("model", ""),
                    "size": record.get("size", ""),
                    "steps": record.get("steps", 20),
                    "guidance_scale": record.get("guidance_scale", 3.0),
                    "seed": record.get("seed", -1),
                })
                st.success("✅ 参数已复用")
                st.session_state.selected_record_id = None
                st.rerun()
            
            if st.button("❌ 关闭", key=f"close_full_{record['id']}", width="stretch", type="primary"):
                st.session_state.selected_record_id = None
                st.rerun()