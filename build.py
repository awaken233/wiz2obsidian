#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
使用 PyInstaller 打包 wiz2obsidian 应用程序
"""

import os
import subprocess
import platform
import sys

def main():
    print("开始打包 wiz2obsidian 应用...")
    
    # 检查 PyInstaller 是否已安装
    try:
        import PyInstaller
        print(f"检测到 PyInstaller 版本: {PyInstaller.__version__}")
    except ImportError:
        print("未检测到 PyInstaller，请先运行: pip install pyinstaller")
        return
    
    # 获取系统平台
    system = platform.system().lower()
    print(f"当前系统: {system}")
    
    # 构建命令
    cmd = ["pyinstaller", "--clean", "wiz2obsidian.spec"]
    
    # 执行命令
    print("执行打包命令...")
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    if result.returncode == 0:
        print("\n打包成功!")
        dist_path = os.path.join(os.getcwd(), "dist")
        print(f"可执行文件位于: {dist_path}")
    else:
        print("\n打包失败!")
        print("错误信息:")
        print(result.stderr)
    
if __name__ == "__main__":
    main() 