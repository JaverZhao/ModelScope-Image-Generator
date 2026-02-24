"""
ModelScope Image Generator - 主入口
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ui.app import main

if __name__ == "__main__":
    main()