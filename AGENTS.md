# ModelScope Image Generator 项目上下文

## 项目概述

**ModelScope Image Generator (MS-Gen)** 是一款基于魔搭 (ModelScope) API 的轻量级 AI 绘图工具，提供图形化界面解决开发者或设计师在使用魔搭 API 时缺乏 GUI 的痛点。

### 核心特性
- API Key 配置与验证
- 多种 AI 绘图模型支持
- 生图参数可视化调整（步数、引导系数、种子等）
- 历史记录管理与图片预览
- 按日期组织图片存储

## 技术栈

| 类别 | 技术 |
|------|------|
| 语言 | Python 3.8+ |
| 前端框架 | Streamlit |
| HTTP 客户端 | requests |
| 图像处理 | Pillow (PIL) |
| 数据持久化 | JSON 文件 |
| 环境变量 | python-dotenv |

## 项目结构

```
MS_Image_Generater/
├── main.py                    # 应用入口
├── config.json                # 用户配置文件（API Key、默认参数等）
├── .env                       # 环境变量文件
├── requirements.txt           # Python 依赖
├── data/
│   ├── images/               # 生成的图片（按日期分目录）
│   ├── history/              # 历史记录 JSON
│   └── cache/                # 缓存目录
├── logs/                     # 日志文件
└── src/
    ├── api/                  # API 层
    │   ├── modelscope_client.py   # ModelScope API 客户端
    │   └── exceptions.py          # 自定义异常类
    ├── config/               # 配置
    │   └── settings.py           # 全局常量配置
    ├── core/                 # 核心业务逻辑
    │   ├── config_manager.py     # 配置管理器
    │   ├── history_manager.py    # 历史记录管理器
    │   └── generation_service.py # 生图服务控制器
    ├── ui/                   # Streamlit UI 层
    │   ├── app.py               # 主应用入口
    │   └── components/          # UI 组件
    │       ├── sidebar.py           # 左侧栏容器
    │       ├── main_area.py         # 主区域容器
    │       ├── generation_params.py # 生图参数组件
    │       ├── generate_button.py   # 生图按钮组件
    │       ├── history_gallery.py   # 历史画廊组件
    │       ├── api_config.py        # API 配置组件
    │       └── feedback.py          # 反馈组件
    └── utils/                # 工具类
        ├── logger.py            # 日志工具
        ├── image_processor.py   # 图片处理器
        └── image_downloader.py  # 图片下载器
```

## 构建与运行

### 环境准备

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 配置

1. 复制配置模板：
   ```bash
   copy config.json.example config.json
   copy .env.example .env
   ```

2. 配置 API Key：
   - 方式一：编辑 `.env` 文件，设置 `MODELSCOPE_API_KEY=your_key`
   - 方式二：在应用 UI 底部的 "API 配置" 区域输入并保存

### 运行应用

```bash
streamlit run main.py
```

或直接运行：

```bash
python main.py
```

## 开发规范

### 代码风格
- 使用 **中文注释** 和 **中文日志**
- 遵循 PEP 8 规范
- 每个模块使用独立 Logger：`logger = get_logger("module-name")`

### 架构模式
- **分层架构**：API 层 → 服务层 → UI 层
- **组件化 UI**：每个 UI 组件独立文件，在 `src/ui/components/` 下
- **状态管理**：使用 Streamlit 的 `st.session_state` 管理会话状态

### 异常处理
项目定义了专用异常类（`src/api/exceptions.py`）：
- `APIKeyInvalidError` - API Key 无效
- `QuotaExceededError` - 余额不足
- `ContentViolationError` - 内容违规
- `TaskFailedError` - 任务失败
- `NetworkError` - 网络错误
- `TimeoutError` - 请求超时

### 命名约定
- 模块文件：小写下划线 (`generation_service.py`)
- 类名：大驼峰 (`GenerationService`)
- 函数/方法：小写下划线 (`generate_image()`)
- 私有方法：下划线前缀 (`_load_records()`)

## API 配置

| 配置项 | 值 |
|--------|-----|
| API Base URL | `https://api-inference.modelscope.cn/` |
| 默认模型 | `Tongyi-MAI/Z-Image-Turbo` |
| 默认尺寸 | `1024x1024` |
| 默认步数 | 20 |
| 默认引导系数 | 3.0 |
| 轮询间隔 | 5 秒 |
| 超时时间 | 300 秒 |

## 关键文件说明

### `src/ui/app.py`
- 主应用入口，定义页面配置和主布局
- 初始化 Session State（config_manager, history_manager, params 等）
- 使用双列布局：左侧参数控制，右侧历史画廊

### `src/core/generation_service.py`
- 生图流程控制器，协调 API 调用、历史记录、图片处理
- 核心方法：`generate_image()` 执行完整生图流程

### `src/api/modelscope_client.py`
- ModelScope API 客户端封装
- 支持异步任务提交和状态轮询

### `src/core/history_manager.py`
- 历史记录管理，JSON 文件持久化
- 支持创建、更新、删除、搜索记录

## 测试

项目目前测试框架在 `tests/` 目录，运行测试：

```bash
pytest tests/
```

## 注意事项

1. **API Key 安全**：API Key 使用 base64 简单编码存储，不是真正的加密
2. **图片存储**：图片按日期 (`YYYY-MM-DD`) 自动创建子目录
3. **历史记录上限**：默认最多保留 1000 条记录
4. **缩略图尺寸**：256x256 像素
