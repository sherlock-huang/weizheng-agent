"""
像素魏征动画

一个可爱的像素风格魏征角色，显示在屏幕右下角
说话时会播放动画
"""

import tkinter as tk
from tkinter import Toplevel
from PIL import Image, ImageDraw, ImageTk
import threading
import time
import random
from typing import Optional, Callable


# 像素颜色定义
COLORS = {
    'skin': '#F5D0C5',      # 肤色
    'skin_dark': '#E5B5A5', # 阴影肤色
    'hat': '#2C3E50',       # 官帽颜色
    'hat_red': '#C0392B',   # 官帽红边
    'robe': '#8E44AD',      # 紫袍（唐朝三品以上官员）
    'robe_dark': '#6C3483', # 紫袍阴影
    'beard': '#FFFFFF',     # 白胡须
    'eye': '#000000',       # 眼睛
    'mouth': '#8B4513',     # 嘴巴
    'board': '#D4AC6E',     # 笏板
    'board_dark': '#B8956A',# 笏板阴影
    'outline': '#1A1A1A',   # 轮廓
}


class PixelSprite:
    """像素精灵类 - 生成魏征的像素图"""
    
    def __init__(self, size: int = 120):
        self.size = size
        self.scale = size // 40  # 基础像素大小
        self.frames = []
        self.talking_frames = []
        self._generate_sprites()
    
    def _create_base_image(self) -> Image.Image:
        """创建基础图像"""
        img = Image.new('RGBA', (self.size, self.size), (0, 0, 0, 0))
        return img
    
    def _draw_pixel(self, draw: ImageDraw.Draw, x: int, y: int, color: str, size: int = None):
        """绘制一个像素块"""
        if size is None:
            size = self.scale
        draw.rectangle([x*size, y*size, (x+1)*size-1, (y+1)*size-1], fill=color, outline=COLORS['outline'])
    
    def _draw_rect(self, draw: ImageDraw.Draw, x: int, y: int, w: int, h: int, color: str):
        """绘制矩形区域"""
        size = self.scale
        draw.rectangle([x*size, y*size, (x+w)*size-1, (y+h)*size-1], fill=color, outline=COLORS['outline'])
    
    def _generate_sprites(self):
        """生成所有精灵帧"""
        # 空闲动画帧（轻微呼吸效果）
        for frame_idx in range(4):
            offset_y = [0, 1, 0, -1][frame_idx]  # 上下浮动
            img = self._draw_weizheng(offset_y=offset_y, mouth_open=False, blink=False)
            self.frames.append(img)
        
        # 眨眼帧
        img_blink = self._draw_weizheng(offset_y=0, mouth_open=False, blink=True)
        self.frames.insert(2, img_blink)
        
        # 说话动画帧（嘴巴动）
        for mouth_open in [False, True, False, True]:
            for _ in range(2):  # 每帧重复2次
                img = self._draw_weizheng(offset_y=0, mouth_open=mouth_open, blink=False)
                self.talking_frames.append(img)
    
    def _draw_weizheng(self, offset_y: int = 0, mouth_open: bool = False, blink: bool = False) -> Image.Image:
        """
        绘制魏征像素图
        
        布局 (40x40像素网格，scale倍放大):
        - 头部区域: y=2-18
        - 身体区域: y=18-38
        """
        img = self._create_base_image()
        draw = ImageDraw.Draw(img)
        
        s = self.scale
        oy = offset_y  # Y轴偏移
        
        # === 绘制身体（紫袍）===
        # 长袍主体
        self._draw_rect(draw, 8, 20+oy, 24, 18, COLORS['robe'])
        # 长袍阴影
        self._draw_rect(draw, 8, 30+oy, 8, 8, COLORS['robe_dark'])
        self._draw_rect(draw, 24, 30+oy, 8, 8, COLORS['robe_dark'])
        # 衣领
        self._draw_rect(draw, 16, 20+oy, 8, 4, COLORS['robe_dark'])
        
        # === 绘制笏板（手持的木板）===
        # 笏板在身体右侧
        self._draw_rect(draw, 26, 18+oy, 4, 12, COLORS['board'])
        self._draw_pixel(draw, 27, 19+oy, COLORS['board_dark'])
        self._draw_pixel(draw, 27, 20+oy, COLORS['board_dark'])
        
        # === 绘制头部 ===
        # 脸型
        self._draw_rect(draw, 12, 8+oy, 16, 12, COLORS['skin'])
        # 脸部阴影
        self._draw_pixel(draw, 13, 15+oy, COLORS['skin_dark'])
        self._draw_pixel(draw, 26, 15+oy, COLORS['skin_dark'])
        
        # === 绘制官帽 ===
        # 帽子主体
        self._draw_rect(draw, 10, 4+oy, 20, 6, COLORS['hat'])
        # 帽子红边
        self._draw_rect(draw, 10, 9+oy, 20, 2, COLORS['hat_red'])
        # 帽子顶部装饰
        self._draw_pixel(draw, 19, 3+oy, COLORS['hat_red'])
        self._draw_pixel(draw, 20, 3+oy, COLORS['hat_red'])
        # 帽子两侧翅
        self._draw_rect(draw, 6, 6+oy, 4, 2, COLORS['hat'])
        self._draw_rect(draw, 30, 6+oy, 4, 2, COLORS['hat'])
        
        # === 绘制五官 ===
        # 眼睛
        if blink:
            # 闭眼
            self._draw_pixel(draw, 15, 13+oy, COLORS['outline'])
            self._draw_pixel(draw, 16, 13+oy, COLORS['outline'])
            self._draw_pixel(draw, 23, 13+oy, COLORS['outline'])
            self._draw_pixel(draw, 24, 13+oy, COLORS['outline'])
        else:
            # 睁眼
            self._draw_pixel(draw, 15, 12+oy, COLORS['eye'])
            self._draw_pixel(draw, 16, 12+oy, COLORS['eye'])
            self._draw_pixel(draw, 23, 12+oy, COLORS['eye'])
            self._draw_pixel(draw, 24, 12+oy, COLORS['eye'])
            # 眉毛
            self._draw_pixel(draw, 15, 10+oy, COLORS['outline'])
            self._draw_pixel(draw, 24, 10+oy, COLORS['outline'])
        
        # 嘴巴
        if mouth_open:
            # 张嘴（说话中）
            self._draw_rect(draw, 18, 16+oy, 4, 2, COLORS['mouth'])
        else:
            # 闭嘴
            self._draw_pixel(draw, 18, 17+oy, COLORS['mouth'])
            self._draw_pixel(draw, 19, 17+oy, COLORS['mouth'])
            self._draw_pixel(draw, 20, 17+oy, COLORS['mouth'])
            self._draw_pixel(draw, 21, 17+oy, COLORS['mouth'])
        
        # === 绘制胡须 ===
        # 山羊胡
        self._draw_pixel(draw, 19, 18+oy, COLORS['beard'])
        self._draw_pixel(draw, 20, 18+oy, COLORS['beard'])
        self._draw_pixel(draw, 19, 19+oy, COLORS['beard'])
        self._draw_pixel(draw, 20, 19+oy, COLORS['beard'])
        # 长胡须
        for i in range(4):
            self._draw_pixel(draw, 19, 20+oy+i, COLORS['beard'])
            self._draw_pixel(draw, 20, 20+oy+i, COLORS['beard'])
        # 胡须尖端
        self._draw_pixel(draw, 18, 23+oy, COLORS['beard'])
        self._draw_pixel(draw, 21, 23+oy, COLORS['beard'])
        
        # === 袖子 ===
        # 左袖
        self._draw_rect(draw, 6, 22+oy, 4, 8, COLORS['robe'])
        self._draw_rect(draw, 6, 26+oy, 4, 2, COLORS['robe_dark'])
        # 右袖（手持笏板）
        self._draw_rect(draw, 30, 22+oy, 4, 8, COLORS['robe'])
        self._draw_rect(draw, 30, 26+oy, 4, 2, COLORS['robe_dark'])
        
        return img


class PixelWeizheng:
    """
    像素魏征动画窗口
    
    显示在屏幕右下角的小窗口，播放魏征像素动画
    """
    
    def __init__(self, size: int = 120, on_click: Optional[Callable] = None):
        """
        初始化像素魏征
        
        Args:
            size: 像素图大小（默认120x120）
            on_click: 点击回调函数
        """
        self.size = size
        self.on_click = on_click
        self.sprite = PixelSprite(size)
        
        self.window: Optional[Toplevel] = None
        self.label: Optional[tk.Label] = None
        self.photo_images: list = []  # 保持对PhotoImage的引用
        
        self.is_talking = False
        self.current_frame = 0
        self.animation_running = False
        self.animation_thread: Optional[threading.Thread] = None
        
        # 动画速度
        self.idle_speed = 0.3  # 空闲动画速度（秒）
        self.talk_speed = 0.15  # 说话动画速度（秒）
    
    def show(self, parent: Optional[tk.Tk] = None):
        """显示魏征窗口"""
        import sys
        print(f"[PixelWeizheng] show() called", file=sys.stderr)
        
        if self.window is not None:
            print(f"[PixelWeizheng] 窗口已存在，跳过", file=sys.stderr)
            return
        
        if parent is None:
            print(f"[PixelWeizheng] 创建新的Tk根窗口", file=sys.stderr)
            self.root = tk.Tk()
            self.root.withdraw()  # 隐藏主窗口
        else:
            print(f"[PixelWeizheng] 使用提供的父窗口", file=sys.stderr)
            self.root = parent
        
        try:
            # 创建顶层窗口
            print(f"[PixelWeizheng] 创建Toplevel窗口", file=sys.stderr)
            self.window = Toplevel(self.root)
            self.window.title("魏征")
            
            # 设置窗口大小
            window_size = self.size + 20  # 加一些边距
            self.window.geometry(f"{window_size}x{window_size}")
            print(f"[PixelWeizheng] 窗口大小: {window_size}x{window_size}", file=sys.stderr)
            
            # 无边框、置顶
            self.window.overrideredirect(True)
            self.window.attributes('-topmost', True)
            self.window.attributes('-transparentcolor', 'white')  # 白色透明
            print(f"[PixelWeizheng] 窗口属性设置完成", file=sys.stderr)
            
            # 定位到右下角
            self._position_bottom_right()
            
            # 创建标签显示图片
            self.label = tk.Label(self.window, bg='white')
            self.label.pack(expand=True)
            print(f"[PixelWeizheng] 标签创建完成", file=sys.stderr)
            
            # 绑定点击事件
            self.label.bind('<Button-1>', self._on_click)
            self.window.bind('<Button-1>', self._on_click)
            
            # 绑定拖拽移动
            self._bind_drag()
            
            # 预转换所有帧
            print(f"[PixelWeizheng] 准备图像...", file=sys.stderr)
            self._prepare_images()
            
            # 开始动画
            print(f"[PixelWeizheng] 启动动画", file=sys.stderr)
            self.start_animation()
            
            print(f"[PixelWeizheng] 窗口创建完成", file=sys.stderr)
            
        except Exception as e:
            print(f"[PixelWeizheng] 错误: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            raise
    
    def _position_bottom_right(self):
        """将窗口定位到屏幕右下角"""
        import sys
        self.window.update_idletasks()
        
        # 获取屏幕尺寸
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        print(f"[PixelWeizheng] 屏幕尺寸: {screen_width}x{screen_height}", file=sys.stderr)
        
        # 计算位置（右下角，留一些边距）
        window_size = self.size + 20
        x = screen_width - window_size - 20
        y = screen_height - window_size - 100  # 留一些空间给任务栏
        
        print(f"[PixelWeizheng] 窗口位置: ({x}, {y})", file=sys.stderr)
        self.window.geometry(f"+{x}+{y}")
        self.window.update()  # 强制更新
    
    def _prepare_images(self):
        """预转换所有PIL图像为PhotoImage"""
        # 空闲帧
        for img in self.sprite.frames:
            photo = ImageTk.PhotoImage(img)
            self.photo_images.append(photo)
        
        # 说话帧
        self.talk_photo_images = []
        for img in self.sprite.talking_frames:
            photo = ImageTk.PhotoImage(img)
            self.talk_photo_images.append(photo)
    
    def _bind_drag(self):
        """绑定拖拽移动功能"""
        self.drag_data = {"x": 0, "y": 0}
        
        def on_drag_start(event):
            self.drag_data["x"] = event.x_root - self.window.winfo_x()
            self.drag_data["y"] = event.y_root - self.window.winfo_y()
        
        def on_drag(event):
            x = event.x_root - self.drag_data["x"]
            y = event.y_root - self.drag_data["y"]
            self.window.geometry(f"+{x}+{y}")
        
        self.window.bind('<Button-3>', on_drag_start)  # 右键拖拽
        self.window.bind('<B3-Motion>', on_drag)
    
    def _on_click(self, event):
        """点击回调"""
        if self.on_click:
            self.on_click()
    
    def start_animation(self):
        """开始动画循环"""
        if self.animation_running:
            return
        
        self.animation_running = True
        self.animation_thread = threading.Thread(target=self._animation_loop, daemon=True)
        self.animation_thread.start()
    
    def stop_animation(self):
        """停止动画"""
        self.animation_running = False
        if self.animation_thread:
            self.animation_thread.join(timeout=1.0)
    
    def _animation_loop(self):
        """动画循环（在后台线程运行）"""
        while self.animation_running:
            try:
                # 在主线程更新UI
                self.root.after(0, self._update_frame)
                
                # 控制动画速度
                if self.is_talking:
                    time.sleep(self.talk_speed)
                else:
                    time.sleep(self.idle_speed)
                    
            except Exception:
                break
    
    def _update_frame(self):
        """更新当前帧（在主线程调用）"""
        if self.window is None or self.label is None:
            return
        
        try:
            if self.is_talking:
                # 说话动画
                frames = self.talk_photo_images
                self.current_frame = (self.current_frame + 1) % len(frames)
            else:
                # 空闲动画
                frames = self.photo_images
                # 随机眨眼
                if random.random() < 0.05:  # 5%概率眨眼
                    self.current_frame = 2  # 眨眼帧
                else:
                    self.current_frame = (self.current_frame + 1) % len(frames)
                    if self.current_frame == 2:  # 跳过眨眼帧（除非随机触发）
                        self.current_frame = 3
            
            # 更新图片
            if frames:
                self.label.config(image=frames[self.current_frame])
        except Exception:
            pass
    
    def talk(self, duration: float = 3.0):
        """
        开始说话动画
        
        Args:
            duration: 说话持续时间（秒）
        """
        self.is_talking = True
        # 在指定时间后停止说话
        if self.window:
            self.window.after(int(duration * 1000), self.stop_talking)
    
    def stop_talking(self):
        """停止说话动画"""
        self.is_talking = False
    
    def hide(self):
        """隐藏窗口"""
        if self.window:
            self.stop_animation()
            self.window.destroy()
            self.window = None
    
    def set_opacity(self, opacity: float):
        """设置窗口透明度 (0.0-1.0)"""
        if self.window:
            self.window.attributes('-alpha', opacity)


def show_weizheng_animation(duration: float = 3.0, on_click: Optional[Callable] = None):
    """
    便捷函数：显示魏征动画并自动开始说话
    
    Args:
        duration: 说话持续时间
        on_click: 点击回调
    
    Returns:
        PixelWeizheng实例
    """
    root = tk.Tk()
    root.withdraw()
    
    weizheng = PixelWeizheng(size=120, on_click=on_click)
    weizheng.show(parent=root)
    weizheng.talk(duration=duration)
    
    # 设置自动关闭
    def auto_close():
        weizheng.hide()
        root.quit()
    
    root.after(int((duration + 1) * 1000), auto_close)
    
    # 运行事件循环
    root.mainloop()
    
    return weizheng


# 测试代码
if __name__ == "__main__":
    print("启动像素魏征测试...")
    print("点击魏征关闭窗口")
    
    root = tk.Tk()
    root.withdraw()
    
    def on_click():
        print("魏征被点击了！")
        root.quit()
    
    weizheng = PixelWeizheng(size=120, on_click=on_click)
    weizheng.show(parent=root)
    weizheng.talk(duration=5.0)
    
    # 5秒后自动停止说话
    root.after(5000, weizheng.stop_talking)
    
    root.mainloop()
