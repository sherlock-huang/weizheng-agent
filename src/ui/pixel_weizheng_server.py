"""
像素魏征动画服务器

提供 HTTP API 供外部（如 Kimi Code）触发说话动画
"""

import tkinter as tk
from tkinter import Toplevel, Canvas
from PIL import Image, ImageTk
import threading
import http.server
import socketserver
import json
import urllib.parse
from typing import Optional, Dict, Any
from pathlib import Path

# 导入像素精灵
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.ui.pixel_weizheng_v4 import CutePixelSprite


class PixelWeizhengServer:
    """
    带 HTTP 服务器的像素魏征
    
    Kimi Code 可以通过 HTTP 请求触发说话动画
    """
    
    def __init__(self, http_port: int = 8765, size: int = 140):
        self.http_port = http_port
        self.size = size
        self.sprite = CutePixelSprite(size)
        
        self.window: Optional[Toplevel] = None
        self.label: Optional[tk.Label] = None
        self.photo_idle: list = []
        self.photo_talk: list = []
        
        self.is_talking = False
        self.current_frame = 0
        self.bubble_window = None
        
        # HTTP 服务器
        self.http_server = None
        self.server_thread = None
        
        # 状态
        self.last_message = ""
        self.talk_count = 0
        
    def start(self):
        """启动 GUI 和 HTTP 服务器"""
        # 创建主窗口
        self.root = tk.Tk()
        self.root.withdraw()
        
        # 创建像素魏征窗口
        self._create_window()
        
        # 准备图像
        self._prepare_images()
        
        # 启动动画
        self._animate()
        
        # 启动 HTTP 服务器（在后台线程）
        self._start_http_server()
        
        print(f"\n{'='*60}")
        print("像素魏征服务器已启动！")
        print(f"{'='*60}")
        print(f"HTTP API: http://localhost:{self.http_port}")
        print(f"\n触发说话动画:")
        print(f'  curl http://localhost:{self.http_port}/talk?msg=你好')
        print(f"\n或者在 Kimi Code 中说: '魏征，你怎么看？'")
        print(f"{'='*60}\n")
        
        # 运行主循环
        self.root.mainloop()
    
    def _create_window(self):
        """创建窗口"""
        self.window = Toplevel(self.root)
        self.window.title("魏征")
        
        window_size = self.size + 16
        self.window.geometry(f"{window_size}x{window_size}")
        
        # 无边框、置顶、透明
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        self.window.attributes('-transparentcolor', '#F0F0F0')
        
        # 定位右下角
        self.window.update_idletasks()
        screen_w = self.window.winfo_screenwidth()
        screen_h = self.window.winfo_screenheight()
        x = screen_w - window_size - 20
        y = screen_h - window_size - 100
        self.window.geometry(f"+{x}+{y}")
        
        # 保存气泡位置
        self.bubble_x = x - 150
        self.bubble_y = y - 70
        
        # 创建标签
        self.label = tk.Label(self.window, bg='#F0F0F0')
        self.label.pack(expand=True)
        
        # 绑定事件
        self._bind_events()
    
    def _bind_events(self):
        """绑定事件"""
        # 左键点击 - 手动触发
        self.label.bind('<Button-1>', lambda e: self.talk("手动触发"))
        
        # 右键菜单
        menu = tk.Menu(self.window, tearoff=0)
        menu.add_command(label="说话", command=lambda: self.talk("陛下好！"))
        menu.add_separator()
        menu.add_command(label="API 地址", command=self._show_api_info)
        menu.add_separator()
        menu.add_command(label="退出", command=self._exit)
        
        def show_menu(event):
            menu.post(event.x_root, event.y_root)
        
        self.window.bind('<Button-3>', show_menu)
        self.label.bind('<Button-3>', show_menu)
        
        # 拖拽
        self.drag_data = {"x": 0, "y": 0}
        
        def start_drag(event):
            self.drag_data["x"] = event.x_root - self.window.winfo_x()
            self.drag_data["y"] = event.y_root - self.window.winfo_y()
        
        def do_drag(event):
            x = event.x_root - self.drag_data["x"]
            y = event.y_root - self.drag_data["y"]
            self.window.geometry(f"+{x}+{y}")
            self.bubble_x = x - 150
            self.bubble_y = y - 70
        
        self.window.bind('<Button-1>', start_drag, add='+')
        self.window.bind('<B1-Motion>', do_drag)
    
    def _prepare_images(self):
        """准备图像"""
        for img in self.sprite.frames_idle:
            self.photo_idle.append(ImageTk.PhotoImage(img))
        for img in self.sprite.frames_talk:
            self.photo_talk.append(ImageTk.PhotoImage(img))
    
    def _animate(self):
        """动画循环"""
        if not self.window:
            return
        
        frames = self.photo_talk if self.is_talking else self.photo_idle
        speed = 80 if self.is_talking else 180
        
        if frames:
            self.current_frame = (self.current_frame + 1) % len(frames)
            self.label.config(image=frames[self.current_frame])
        
        self.root.after(speed, self._animate)
    
    def talk(self, message: str = "陛下！臣有话说！", duration: int = 3):
        """
        触发说话动画
        
        这是核心方法，会被 HTTP 请求调用
        """
        self.is_talking = True
        self.last_message = message
        self.talk_count += 1
        
        # 显示气泡
        self._show_bubble(message)
        
        # 定时停止
        self.root.after(duration * 1000, self._stop_talking)
        
        print(f"[魏征] 说话动画触发: {message[:30]}... (第{self.talk_count}次)")
    
    def _stop_talking(self):
        """停止说话"""
        self.is_talking = False
        self._hide_bubble()
    
    def _show_bubble(self, text: str):
        """显示气泡"""
        self._hide_bubble()
        
        self.bubble_window = Toplevel(self.root)
        self.bubble_window.overrideredirect(True)
        self.bubble_window.attributes('-topmost', True)
        self.bubble_window.geometry(f"150x70+{self.bubble_x}+{self.bubble_y}")
        
        canvas = tk.Canvas(self.bubble_window, width=150, height=70,
                          bg='#F0F0F0', highlightthickness=0)
        canvas.pack()
        
        # 气泡形状
        canvas.create_polygon(
            8, 8, 142, 8, 142, 52, 90, 52, 80, 62, 70, 52, 8, 52,
            fill='white', outline='#333', width=2, smooth=True
        )
        
        # 文字
        canvas.create_text(75, 30, text=text[:20], 
                          font=('Microsoft YaHei', 10, 'bold'),
                          fill='#333', width=130)
    
    def _hide_bubble(self):
        """隐藏气泡"""
        if self.bubble_window:
            self.bubble_window.destroy()
            self.bubble_window = None
    
    def _start_http_server(self):
        """启动 HTTP 服务器"""
        class Handler(http.server.BaseHTTPRequestHandler):
            server_instance = self
            
            def do_GET(self):
                """处理 GET 请求"""
                parsed = urllib.parse.urlparse(self.path)
                path = parsed.path
                query = urllib.parse.parse_qs(parsed.query)
                
                if path == '/talk':
                    # 触发说话动画
                    msg = query.get('msg', ['陛下！臣有话说！'])[0]
                    duration = int(query.get('duration', ['3'])[0])
                    
                    # 在主线程执行 GUI 操作
                    self.server_instance.root.after(0, 
                        lambda: self.server_instance.talk(msg, duration))
                    
                    self._send_json({
                        "status": "success",
                        "message": "说话动画已触发",
                        "data": {"msg": msg, "duration": duration}
                    })
                
                elif path == '/status':
                    # 获取状态
                    self._send_json({
                        "status": "success",
                        "data": {
                            "talk_count": self.server_instance.talk_count,
                            "is_talking": self.server_instance.is_talking,
                            "last_message": self.server_instance.last_message
                        }
                    })
                
                elif path == '/':
                    # 首页
                    self._send_json({
                        "service": "像素魏征服务器",
                        "version": "1.0",
                        "endpoints": {
                            "/talk": "触发说话动画 (参数: msg, duration)",
                            "/status": "获取状态"
                        }
                    })
                
                else:
                    self._send_json({"error": "未知路径"}, 404)
            
            def _send_json(self, data, status=200):
                """发送 JSON 响应"""
                self.send_response(status)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
            
            def log_message(self, format, *args):
                """抑制日志输出"""
                pass
        
        Handler.server_instance = self
        
        # 创建服务器
        self.http_server = socketserver.TCPServer(('', self.http_port), Handler)
        
        # 在后台线程运行
        self.server_thread = threading.Thread(target=self.http_server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
    
    def _show_api_info(self):
        """显示 API 信息"""
        import tkinter.messagebox as msgbox
        info = f"""HTTP API 地址:

http://localhost:{self.http_port}/talk?msg=你好

触发说话动画:
• 浏览器访问上面的链接
• 或在 Kimi Code 中调用
• 或使用 curl 命令"""
        msgbox.showinfo("API 信息", info)
    
    def _exit(self):
        """退出"""
        if self.http_server:
            self.http_server.shutdown()
        self.root.quit()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='像素魏征服务器')
    parser.add_argument('--port', type=int, default=8765, help='HTTP 端口 (默认: 8765)')
    parser.add_argument('--size', type=int, default=140, help='像素大小 (默认: 140)')
    args = parser.parse_args()
    
    server = PixelWeizhengServer(http_port=args.port, size=args.size)
    server.start()


if __name__ == '__main__':
    main()
