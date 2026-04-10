"""
无头模式服务器（用于测试）

在没有显示器的环境（如 RDP）下运行，只提供 HTTP API，不显示 GUI。

用法:
    python -m src.server.headless_server
"""

import http.server
import socketserver
import json
import threading
import time
from datetime import datetime
from typing import Dict, Any


class HeadlessServer:
    """无头模式服务器 - 仅 HTTP API，无 GUI"""
    
    def __init__(self, port: int = 7788):
        self.port = port
        self.status = {
            "is_running": False,
            "is_talking": False,
            "talk_count": 0,
            "last_talk_time": None,
            "last_message": "",
        }
        self.http_server = None
        self.talk_timer = None
        
        # 轮播相关
        self.messages = []
        self.current_msg_index = 0
        self.rotation_timer = None
        
    def start(self):
        """启动服务器"""
        print(f"\n{'='*60}")
        print("魏征无头模式服务端启动中...")
        print(f"{'='*60}\n")
        print("[WARNING] 无头模式 - 不显示像素动画")
        print("          用于测试 API 功能\n")
        
        # 创建 HTTP 处理器
        handler = self._create_handler()
        
        # 启动 HTTP 服务器
        self.http_server = socketserver.TCPServer(("", self.port), handler)
        self.http_server.server_instance = self
        
        self.status["is_running"] = True
        
        print(f"{'='*60}")
        print(f"[OK] HTTP API 监听端口: {self.port}")
        print(f"{'='*60}")
        print("\nAPI 端点:")
        print(f"  POST http://localhost:{self.port}/api/talk")
        print(f"  POST http://localhost:{self.port}/api/stop")
        print(f"  GET  http://localhost:{self.port}/api/status")
        print(f"\n按 Ctrl+C 停止服务器")
        print(f"{'='*60}\n")
        
        try:
            self.http_server.serve_forever()
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """停止服务器"""
        print("\n正在停止服务端...")
        self.status["is_running"] = False
        if self.http_server:
            self.http_server.shutdown()
        print("已停止")
    
    def start_talk(self, message: str = "", duration: float = None, messages: list = None):
        """开始说话（模拟）- 支持多句话轮播"""
        import re
        
        self.status["is_talking"] = True
        self.status["talk_count"] += 1
        self.status["last_talk_time"] = datetime.now().isoformat()
        
        # 处理多句话
        if messages and isinstance(messages, list):
            self.messages = messages
        elif message:
            # 分割长文本
            self.messages = self._split_message(message)
        else:
            self.messages = ["陛下！臣有话说！"]
        
        self.current_msg_index = 0
        self.status["last_message"] = self.messages[0] if self.messages else ""
        
        # 打印第一句话
        print(f"[TALK] {self.status['last_message'][:50]}...")
        print(f"       共 {len(self.messages)} 句，轮播中（需调用 stop 停止）")
        
        # 取消之前的定时器
        if self.rotation_timer:
            self.rotation_timer.cancel()
        
        # 启动轮播（每3秒一句）
        if len(self.messages) > 1:
            self._schedule_next_message()
        
        return {
            "success": True, 
            "message": "开始说话动画（轮播模式）", 
            "mode": "headless",
            "message_count": len(self.messages)
        }
    
    def _split_message(self, text: str, max_len: int = 30) -> list:
        """分割长文本"""
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
        
        return result if result else [text]
    
    def _schedule_next_message(self):
        """调度下一句"""
        def rotate():
            if not self.status["is_talking"]:
                return
            self.current_msg_index = (self.current_msg_index + 1) % len(self.messages)
            msg = self.messages[self.current_msg_index]
            self.status["last_message"] = msg
            print(f"[TALK] [{self.current_msg_index+1}/{len(self.messages)}] {msg[:50]}...")
            self._schedule_next_message()
        
        self.rotation_timer = threading.Timer(3.0, rotate)
        self.rotation_timer.start()
    
    def stop_talk(self):
        """停止说话（由外部调用，Agent 输出完成后调用）"""
        if self.rotation_timer:
            self.rotation_timer.cancel()
            self.rotation_timer = None
        
        was_talking = self.status["is_talking"]
        self.status["is_talking"] = False
        self.messages = []
        self.current_msg_index = 0
        
        if was_talking:
            print("[STOP] 说话动画已停止（Agent 输出完成）")
        
        return {"success": True, "message": "动画已停止"}
    
    def get_status(self):
        """获取状态"""
        return {"success": True, "data": self.status}
    
    def _create_handler(self):
        """创建 HTTP 处理器类"""
        instance = self
        
        class RequestHandler(http.server.BaseHTTPRequestHandler):
            server_instance = instance
            
            def log_message(self, format, *args):
                # 简化日志输出
                pass
            
            def do_GET(self):
                if self.path == "/api/status":
                    self._send_json(self.server_instance.get_status())
                else:
                    self._send_json({"error": "Not found"}, 404)
            
            def do_POST(self):
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length).decode('utf-8')
                
                try:
                    data = json.loads(body) if body else {}
                except:
                    data = {}
                
                if self.path == "/api/talk":
                    message = data.get("message", "")
                    messages = data.get("messages")
                    duration = data.get("duration")
                    result = self.server_instance.start_talk(message, duration, messages)
                    self._send_json(result)
                
                elif self.path == "/api/stop":
                    result = self.server_instance.stop_talk()
                    self._send_json(result)
                
                else:
                    self._send_json({"error": "Not found"}, 404)
            
            def _send_json(self, data: Dict[str, Any], status_code: int = 200):
                self.send_response(status_code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
        
        return RequestHandler


def main():
    """主函数"""
    import argparse
    parser = argparse.ArgumentParser(description='魏征无头模式服务端')
    parser.add_argument('--port', '-p', type=int, default=7788, help='HTTP 端口')
    args = parser.parse_args()
    
    server = HeadlessServer(port=args.port)
    server.start()


if __name__ == '__main__':
    main()
