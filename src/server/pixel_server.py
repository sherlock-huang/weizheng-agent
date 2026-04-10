"""
像素魏征服务端

独立运行的服务端，提供：
1. 像素魏征 GUI（屏幕右下角）
2. HTTP API（供 CLI 和 OpenClaw 调用）
3. 说话动画控制

使用方法:
    python -m src.server
    或
    python src/server/pixel_server.py

HTTP API:
    POST /api/talk         - 开始说话动画
    POST /api/stop         - 停止说话动画  
    GET  /api/status       - 获取状态
"""

import tkinter as tk
from tkinter import Toplevel, Canvas
from PIL import Image, ImageTk
import threading
import http.server
import socketserver
import json
import sys
import os
import ctypes
import ctypes.wintypes
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.ui.pixel_weizheng_v4 import CutePixelSprite

# Win32 常量
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
WS_EX_APPWINDOW = 0x00040000
LWA_COLORKEY = 0x00000001
LWA_ALPHA = 0x00000002
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001
SWP_NOZORDER = 0x0004
SWP_FRAMECHANGED = 0x0020
HWND_TOP = 0
SM_REMOTESESSION = 0x1000

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32


def is_rdp_session() -> bool:
    """检测当前是否在 RDP 会话中运行"""
    return os.environ.get("SESSIONNAME", "").startswith("RDP") or \
           kernel32.GetSystemMetrics(SM_REMOTESESSION) != 0


def fix_window_for_rdp(hwnd: int):
    """
    修复 RDP 中窗口不可见问题（简单方案：不透明窗口）。
    已废弃，请使用 fix_window_for_rdp_colorkey。
    """
    pass


def fix_window_for_rdp_colorkey(hwnd: int, color_key: int = 0xF0F0F0):
    """
    修复 RDP 中窗口不可见问题。
    
    方案：使用 LWA_COLORKEY（色键透明），让指定颜色完全透明。
    LWA_COLORKEY 在 RDP 中可正常工作（不像 LWA_ALPHA）。
    
    参数:
        hwnd: 窗口句柄
        color_key: 透明色（RGB格式，默认 0xF0F0F0 = #F0F0F0）
    """
    # 获取当前扩展样式
    ex_style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    
    # 确保有 WS_EX_LAYERED 标志
    if not (ex_style & WS_EX_LAYERED):
        ex_style |= WS_EX_LAYERED
        user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex_style)
    
    # 使用 SetLayeredWindowAttributes 设置 LWA_COLORKEY
    # 注意：bAlpha 参数在 LWA_COLORKEY 模式下被忽略，设为 255
    user32.SetLayeredWindowAttributes(hwnd, color_key, 255, LWA_COLORKEY)
    
    # 强制窗口管理器重新评估样式变更
    user32.SetWindowPos(
        hwnd, HWND_TOP,
        0, 0, 0, 0,
        SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED
    )
    
    # 强制重绘
    user32.ShowWindow(hwnd, 5)  # SW_SHOW
    user32.RedrawWindow(hwnd, None, None, 0x0001 | 0x0100)  # RDW_INVALIDATE | RDW_UPDATENOW


class PixelWeizhengServer:
    """
    像素魏征服务端
    
    独立运行的服务端，提供 GUI 和 HTTP API
    """
    
    def __init__(self, http_port: int = 7788, pixel_size: int = 140):
        self.http_port = http_port
        self.size = pixel_size
        
        # GUI 相关
        self.sprite = CutePixelSprite(self.size)
        self.window: Optional[Toplevel] = None
        self.main_frame: Optional[tk.Frame] = None
        self.pixel_frame: Optional[tk.Frame] = None
        self.label: Optional[tk.Label] = None
        self.photo_idle: list = []
        self.photo_talk: list = []
        self.is_talking = False
        self.current_frame = 0
        
        # 气泡相关（集成在窗口内）
        self.bubble_frame: Optional[tk.Frame] = None
        self.bubble_canvas: Optional[tk.Canvas] = None
        self.bubble_text_id: Optional[int] = None
        self.bubble_dots: list = []
        
        # 轮播相关
        self.messages = []  # 多句话列表
        self.current_msg_index = 0
        self.msg_rotation_timer = None
        self.msg_display_duration = 3000  # 每句话显示3秒
        
        # HTTP 服务器
        self.http_server = None
        self.server_thread = None
        
        # 状态
        self.status = {
            "is_running": False,
            "is_talking": False,
            "talk_count": 0,
            "last_talk_time": None,
            "last_message": "",
        }
        
        # RDP 检测
        self.is_rdp = is_rdp_session()
        
    def start(self):
        """启动服务端"""
        mode_str = "RDP 模式" if self.is_rdp else "本地模式"
        print(f"\n{'='*60}")
        print("魏征像素服务端启动中...")
        print(f"检测模式: {mode_str}")
        print(f"{'='*60}\n")
        
        # 创建主窗口
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.title("魏征像素服务端")
        
        # 创建像素窗口
        self._create_pixel_window()
        
        # 准备图像
        self._prepare_images()
        
        # 启动动画
        self._animate()
        
        # 启动 HTTP 服务器
        self._start_http_server()
        
        # 确保窗口显示（RDP环境需要）
        self.root.update_idletasks()
        self.window.update_idletasks()
        
        self.status["is_running"] = True
        
        print(f"{'='*60}")
        print("[OK] 像素魏征已显示在屏幕右下角")
        print(f"[OK] HTTP API 监听端口: {self.http_port}")
        print(f"{'='*60}")
        print("\nAPI 端点:")
        print(f"  POST http://localhost:{self.http_port}/api/talk")
        print(f"  POST http://localhost:{self.http_port}/api/stop")
        print(f"  GET  http://localhost:{self.http_port}/api/status")
        print(f"\n按 Ctrl+C 停止服务器")
        print(f"{'='*60}\n")
        
        # 运行主循环
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """停止服务端"""
        print("\n正在停止服务端...")
        self.status["is_running"] = False
        
        if self.http_server:
            self.http_server.shutdown()
        
        if self.window:
            self.window.destroy()
        
        self.root.quit()
        print("服务端已停止")
    
    def _create_pixel_window(self):
        """创建像素魏征窗口（气泡在上方）"""
        self.window = Toplevel(self.root)
        self.window.title("魏征")
        
        # 窗口尺寸：气泡区（上方）+ 像素区
        pixel_size = self.size + 16
        bubble_h = 80  # 气泡高度
        window_w = pixel_size
        window_h = pixel_size + bubble_h + 10  # 总高度
        
        self.window.geometry(f"{window_w}x{window_h}")
        
        # 无边框、置顶、透明背景
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        self.window.attributes('-transparentcolor', '#F0F0F0')
        
        # 定位到右下角（往上偏移，为气泡留出空间）
        self.window.update_idletasks()
        screen_w = self.window.winfo_screenwidth()
        screen_h = self.window.winfo_screenheight()
        x = screen_w - window_w - 20
        y = screen_h - window_h - 50  # 往上一点，确保气泡可见
        self.window.geometry(f"+{x}+{y}")
        
        # 创建主容器（透明背景）
        self.main_frame = tk.Frame(self.window, bg='#F0F0F0')
        self.main_frame.pack(fill='both', expand=True)
        
        # 上方：气泡文字区（初始隐藏）
        self.bubble_frame = tk.Frame(self.main_frame, bg='#F0F0F0', 
                                     width=window_w, height=bubble_h)
        self.bubble_frame.pack(side='top', fill='x', pady=(0, 5))
        self.bubble_frame.pack_propagate(False)
        
        # 气泡 Canvas
        self.bubble_canvas = tk.Canvas(self.bubble_frame, bg='#F0F0F0', 
                                       width=window_w, height=bubble_h,
                                       highlightthickness=0)
        self.bubble_canvas.pack(fill='both', expand=True)
        
        # 气泡形状（白色圆角矩形 + 下箭头指向魏征）
        padding = 10
        arrow_h = 10
        bubble_w = window_w - 20
        bubble_x = 10
        
        # 绘制气泡（下箭头指向魏征）
        self.bubble_id = self.bubble_canvas.create_polygon(
            bubble_x, padding,                           # 左上
            bubble_x + bubble_w, padding,                # 右上
            bubble_x + bubble_w, bubble_h - padding - arrow_h,  # 右下（箭头上）
            bubble_x + bubble_w//2 + 8, bubble_h - padding - arrow_h,  # 箭头右
            bubble_x + bubble_w//2, bubble_h - padding,   # 箭头尖（下）
            bubble_x + bubble_w//2 - 8, bubble_h - padding - arrow_h,  # 箭头左
            bubble_x, bubble_h - padding - arrow_h,       # 左下（箭头上）
            fill='white', outline='#333', width=2, smooth=True
        )
        
        # 文字显示区
        self.bubble_text_id = self.bubble_canvas.create_text(
            window_w // 2, bubble_h // 2 - 5,
            text="",
            font=('Microsoft YaHei', 10, 'bold'),
            fill='#333',
            width=bubble_w - padding * 2,
            anchor='center'
        )
        
        # 进度点（气泡底部）
        self.bubble_dots = []
        
        # 下方：像素动画区
        self.pixel_frame = tk.Frame(self.main_frame, bg='#F0F0F0', 
                                    width=window_w, height=pixel_size)
        self.pixel_frame.pack(side='bottom', fill='both')
        self.pixel_frame.pack_propagate(False)
        
        self.label = tk.Label(self.pixel_frame, bg='#F0F0F0')
        self.label.place(relx=0.5, rely=0.5, anchor='center')
        
        # 初始隐藏气泡
        self.bubble_frame.pack_forget()
        
        # 显示窗口
        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()
        
        # RDP 模式下使用色键透明
        if self.is_rdp:
            self.window.update()
            hwnd = user32.GetParent(self.window.winfo_id())
            if hwnd == 0:
                hwnd = self.window.winfo_id()
            fix_window_for_rdp_colorkey(hwnd, 0xF0F0F0)
            print("[GUI] RDP 模式：已应用 LWA_COLORKEY 透明")
        
        # 绑定事件
        self._bind_events()
    
    def _bind_events(self):
        """绑定事件"""
        # 右键菜单
        menu = tk.Menu(self.window, tearoff=0)
        menu.add_command(label="状态", command=self._show_status)
        menu.add_separator()
        menu.add_command(label="退出", command=self.stop)
        
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
        
        self.window.bind('<Button-1>', start_drag)
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
    
    def talk(self, message: str = "陛下！臣有话说！", duration: float = None, 
             messages: list = None):
        """
        开始说话动画，支持多句话轮播
        
        Args:
            message: 显示在气泡中的文字（单条或第一条）
            duration: 已废弃，保留兼容
            messages: 多句话列表，会轮播显示
        """
        self.is_talking = True
        self.status["is_talking"] = True
        self.status["talk_count"] += 1
        self.status["last_talk_time"] = datetime.now().isoformat()
        
        # 处理多句话
        if messages and isinstance(messages, list):
            self.messages = messages
        elif message:
            # 自动分割长文本为多句（每句30字左右）
            self.messages = self._split_message(message)
        else:
            self.messages = ["陛下！臣有话说！"]
        
        self.current_msg_index = 0
        self.status["last_message"] = self.messages[0] if self.messages else ""
        
        # 显示第一句话
        self._show_current_message()
        
        # 启动轮播
        self._start_message_rotation()
        
        print(f"[魏征] 开始说话，共 {len(self.messages)} 句")
        for i, msg in enumerate(self.messages[:3]):
            print(f"  [{i+1}] {msg[:40]}...")
        if len(self.messages) > 3:
            print(f"  ... 还有 {len(self.messages)-3} 句")
    
    def _split_message(self, text: str, max_len: int = 30) -> list:
        """将长文本分割为多句话"""
        # 先按标点符号分割
        import re
        sentences = re.split(r'([。！？.!?;；\n])', text)
        
        result = []
        current = ""
        for i in range(0, len(sentences), 2):
            sentence = sentences[i]
            punct = sentences[i+1] if i+1 < len(sentences) else ""
            full = sentence + punct
            
            if len(current) + len(full) < max_len:
                current += full
            else:
                if current:
                    result.append(current.strip())
                current = full
        
        if current:
            result.append(current.strip())
        
        # 如果还是没有分割（没有标点），强制分割
        if not result:
            for i in range(0, len(text), max_len):
                result.append(text[i:i+max_len])
        
        return result if result else [text]
    
    def _show_current_message(self):
        """显示当前轮播的消息"""
        if self.current_msg_index < len(self.messages):
            msg = self.messages[self.current_msg_index]
            self._show_bubble(msg)
            self.status["last_message"] = msg
    
    def _start_message_rotation(self):
        """开始消息轮播"""
        if self.msg_rotation_timer:
            self.root.after_cancel(self.msg_rotation_timer)
        
        def rotate():
            if not self.is_talking:
                return
            
            self.current_msg_index = (self.current_msg_index + 1) % len(self.messages)
            self._show_current_message()
            
            # 继续下一句
            self.msg_rotation_timer = self.root.after(self.msg_display_duration, rotate)
        
        # 设置定时器轮播下一句
        if len(self.messages) > 1:
            self.msg_rotation_timer = self.root.after(self.msg_display_duration, rotate)
    
    def stop_talking(self):
        """停止说话动画（由外部调用，Agent 输出完成后调用）"""
        self.is_talking = False
        self.status["is_talking"] = False
        
        # 取消轮播定时器
        if self.msg_rotation_timer:
            self.root.after_cancel(self.msg_rotation_timer)
            self.msg_rotation_timer = None
        
        self.messages = []
        self.current_msg_index = 0
        self._hide_bubble()
        print("[魏征] 停止说话（Agent 输出完成）")
    
    def _show_bubble(self, text: str):
        """显示气泡 - 在魏征上方"""
        # 显示气泡框架
        self.bubble_frame.pack(side='top', fill='x', pady=(0, 5))
        
        # 更新文字
        display_text = text[:40] + "..." if len(text) > 40 else text
        self.bubble_canvas.itemconfig(self.bubble_text_id, text=display_text)
        
        # 绘制进度点
        self._draw_progress_dots()
        
        # 更新窗口
        self.window.update()
    
    def _draw_progress_dots(self):
        """绘制轮播进度点（气泡底部）"""
        # 清除旧点
        for dot_id in self.bubble_dots:
            self.bubble_canvas.delete(dot_id)
        self.bubble_dots = []
        
        if len(self.messages) <= 1:
            return
        
        # 绘制新点
        window_w = self.size + 16
        dot_y = 65  # 气泡底部位置
        dot_spacing = 12
        total_width = (len(self.messages) - 1) * dot_spacing
        start_x = window_w / 2  # 居中
        
        for i in range(len(self.messages)):
            x = start_x + (i - len(self.messages)/2 + 0.5) * dot_spacing
            color = '#FF6B6B' if i == self.current_msg_index else '#CCC'
            dot_id = self.bubble_canvas.create_oval(
                x-3, dot_y-3, x+3, dot_y+3, 
                fill=color, outline=''
            )
            self.bubble_dots.append(dot_id)
    
    def _hide_bubble(self):
        """隐藏气泡"""
        self.bubble_frame.pack_forget()
        self.window.update()
    
    def _start_http_server(self):
        """启动 HTTP 服务器"""
        class Handler(http.server.BaseHTTPRequestHandler):
            server_instance = self
            
            def do_POST(self):
                """处理 POST 请求"""
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length).decode('utf-8')
                
                try:
                    data = json.loads(body) if body else {}
                except:
                    data = {}
                
                path = self.path
                
                if path == '/api/talk':
                    # 开始说话 - 支持多句话轮播
                    msg = data.get('message', '陛下！臣有话说！')
                    messages = data.get('messages')  # 多句话列表
                    duration = data.get('duration')  # 已废弃，保留兼容
                    
                    # 在主线程执行 GUI 操作
                    self.server_instance.root.after(0, 
                        lambda: self.server_instance.talk(msg, duration, messages))
                    
                    msg_count = len(messages) if messages else (
                        len(self.server_instance._split_message(msg)) if msg else 1
                    )
                    
                    self._send_json({
                        "success": True,
                        "message": "说话动画已启动",
                        "data": {
                            "message": msg, 
                            "messages": messages,
                            "message_count": msg_count
                        }
                    })
                
                elif path == '/api/stop':
                    # 停止说话
                    self.server_instance.root.after(0, 
                        self.server_instance.stop_talking)
                    
                    self._send_json({
                        "success": True,
                        "message": "说话动画已停止"
                    })
                
                else:
                    self._send_json({"success": False, "error": "未知路径"}, 404)
            
            def do_GET(self):
                """处理 GET 请求"""
                path = self.path
                
                if path == '/api/status':
                    self._send_json({
                        "success": True,
                        "data": self.server_instance.status
                    })
                
                elif path == '/':
                    self._send_json({
                        "service": "魏征像素服务端",
                        "version": "1.0",
                        "endpoints": {
                            "POST /api/talk": "开始说话动画",
                            "POST /api/stop": "停止说话动画",
                            "GET  /api/status": "获取状态"
                        }
                    })
                
                else:
                    self._send_json({"success": False, "error": "未知路径"}, 404)
            
            def _send_json(self, data, status=200):
                """发送 JSON 响应"""
                self.send_response(status)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
            
            def log_message(self, format, *args):
                """自定义日志"""
                # 只记录重要请求
                if '/api/' in self.path:
                    print(f"[HTTP] {self.address_string()} - {format % args}")
        
        Handler.server_instance = self
        
        # 创建服务器
        self.http_server = socketserver.TCPServer(('', self.http_port), Handler)
        
        # 在后台线程运行
        self.server_thread = threading.Thread(target=self.http_server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
    
    def _show_status(self):
        """显示状态窗口"""
        import tkinter.messagebox as msgbox
        
        status_text = f"""魏征像素服务端状态

运行状态: {'运行中' if self.status['is_running'] else '已停止'}
说话状态: {'正在说话' if self.status['is_talking'] else '空闲'}
说话次数: {self.status['talk_count']}

HTTP 端口: {self.http_port}
最后说话: {self.status['last_talk_time'] or '无'}

API 测试:
curl -X POST http://localhost:{self.http_port}/api/talk \\
  -H "Content-Type: application/json" \\
  -d '{{"message":"陛下好！"}}'
"""
        msgbox.showinfo("状态", status_text)


def run_server(port: int = 7788):
    """便捷函数：运行服务端"""
    server = PixelWeizhengServer(http_port=port)
    server.start()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='魏征像素服务端')
    parser.add_argument('--port', type=int, default=7788, help='HTTP 端口 (默认: 7788)')
    parser.add_argument('--size', type=int, default=140, help='像素大小 (默认: 140)')
    args = parser.parse_args()
    
    server = PixelWeizhengServer(http_port=args.port, pixel_size=args.size)
    server.start()
