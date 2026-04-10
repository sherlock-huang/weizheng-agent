#!/usr/bin/env python3
"""
魏征像素服务器 - 系统托盘版本

启动后显示在系统托盘，右键可以：
- 显示/隐藏魏征
- 查看状态
- 停止服务器
"""

import sys
import threading
import tkinter as tk
from tkinter import messagebox
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """主函数"""
    # 先尝试导入 pystray，如果没有则提示安装
    try:
        import pystray
        from PIL import Image
        HAS_TRAY = True
    except ImportError:
        HAS_TRAY = False
        print("[提示] 未安装 pystray，使用简单后台模式")
        print("安装命令: pip install pystray pillow")
    
    if not HAS_TRAY:
        # 简单后台模式：直接启动服务器
        from src.server.pixel_server import PixelWeizhengServer
        
        print("="*60)
        print("魏征像素服务器（后台模式）")
        print("="*60)
        print()
        print("服务器启动中...")
        print("按 Ctrl+C 停止")
        print()
        
        server = PixelWeizhengServer(http_port=7788)
        try:
            server.start()
        except KeyboardInterrupt:
            print("\n服务器已停止")
        return
    
    # 系统托盘模式
    # 先启动服务器（在后台线程）
    from src.server.pixel_server import PixelWeizhengServer
    
    server = PixelWeizhengServer(http_port=7788)
    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()
    
    # 创建托盘图标
    import pystray
    from PIL import Image, ImageDraw
    
    def create_icon():
        """创建托盘图标"""
        # 创建一个简单的图标
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), color='white')
        dc = ImageDraw.Draw(image)
        
        # 画一个简单的像素魏征
        dc.rectangle([16, 8, 48, 24], fill='#333')  # 帽子
        dc.rectangle([20, 24, 44, 48], fill='#FFB6C1')  # 脸
        dc.rectangle([16, 48, 48, 56], fill='#8B4513')  # 身体
        
        return image
    
    def on_show(icon, item):
        """显示魏征"""
        if server.window:
            server.window.deiconify()
            server.window.lift()
    
    def on_hide(icon, item):
        """隐藏魏征"""
        if server.window:
            server.window.withdraw()
    
    def on_status(icon, item):
        """查看状态"""
        status = f"""服务器状态:
运行: {server.status['is_running']}
说话: {server.status['is_talking']}
说话次数: {server.status['talk_count']}
最后消息: {server.status['last_message'] or '无'}
"""
        print(status)
    
    def on_exit(icon, item):
        """退出"""
        icon.stop()
        server.stop()
        sys.exit(0)
    
    # 创建托盘菜单
    menu = pystray.Menu(
        pystray.MenuItem("显示魏征", on_show),
        pystray.MenuItem("隐藏魏征", on_hide),
        pystray.MenuItem("查看状态", on_status),
        pystray.MenuItem("退出", on_exit),
    )
    
    icon = pystray.Icon("weizheng", create_icon(), "魏征 Agent", menu)
    
    print("="*60)
    print("魏征像素服务器已启动")
    print("="*60)
    print("服务器在后台运行")
    print("系统托盘图标已创建")
    print()
    
    icon.run()

if __name__ == '__main__':
    main()
