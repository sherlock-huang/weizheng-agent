"""
像素魏征动画 V4 - 无胡子大眼萌版

特色：
- 去掉胡子，更清爽的形象
- 超大眼睛，夸张表情
- 说话时显示对话框
- 右键退出功能
"""

import tkinter as tk
from tkinter import Toplevel, Canvas, Menu
from PIL import Image, ImageDraw, ImageTk
import math
from typing import Optional, Callable, List


# 配色方案
COLORS = {
    'skin': '#FFE4D6',
    'skin_light': '#FFF0E8',
    'skin_shadow': '#F0C0B0',
    
    'hat': '#1A1A2E',
    'hat_light': '#2A2A4E',
    'hat_red': '#C41E3A',
    'hat_gold': '#FFD700',
    
    'robe': '#7B2D6B',
    'robe_light': '#9B4D8B',
    'robe_dark': '#5B1D4B',
    'gold': '#D4AF37',
    
    'eye_white': '#FFFFFF',
    'eye_black': '#0D0D0D',
    'eye_shine': '#FFFFFF',
    
    'mouth': '#8B4513',
    'mouth_open': '#5C2D0E',
    'cheek': '#FFB6C1',
    'eyebrow': '#4A4A4A',
}


class CutePixelSprite:
    """可爱版像素精灵 - 大眼萌"""
    
    def __init__(self, size: int = 140):
        self.size = size
        self.scale = max(2, size // 48)
        
        self.frames_idle: List[Image.Image] = []
        self.frames_talk: List[Image.Image] = []
        
        self._generate_frames()
    
    def _create_img(self) -> Image.Image:
        return Image.new('RGBA', (self.size, self.size), (0, 0, 0, 0))
    
    def _px(self, draw: ImageDraw.Draw, x: int, y: int, color: str):
        s = self.scale
        draw.rectangle([x*s, y*s, (x+1)*s-1, (y+1)*s-1], fill=color)
    
    def _rect(self, draw: ImageDraw.Draw, x: int, y: int, w: int, h: int, color: str):
        s = self.scale
        draw.rectangle([x*s, y*s, (x+w)*s-1, (y+h)*s-1], fill=color)
    
    def _generate_frames(self):
        """生成动画帧"""
        # 空闲动画 - 多种表情
        idle_configs = [
            ('normal', False, False),    # 正常
            ('normal', False, True),     # 眨眼
            ('normal', False, False),    # 正常
            ('happy', False, False),     # 开心
            ('normal', False, False),    # 正常
            ('serious', False, False),   # 严肃
            ('normal', False, False),    # 正常
            ('surprise', False, False),  # 惊讶
        ]
        
        for expr, blink, wink in idle_configs:
            img = self._draw_frame(expression=expr, blink=blink, wink=wink, talking=False)
            self.frames_idle.append(img)
        
        # 说话动画
        talk_configs = [
            ('normal', 'closed'),
            ('normal', 'small'),
            ('normal', 'open'),
            ('normal', 'small'),
            ('normal', 'closed'),
            ('serious', 'open'),
            ('serious', 'small'),
            ('normal', 'closed'),
        ]
        
        for expr, mouth in talk_configs:
            img = self._draw_frame(expression=expr, mouth_shape=mouth, talking=True)
            self.frames_talk.append(img)
    
    def _draw_frame(self, expression: str = 'normal', blink: bool = False,
                   wink: bool = False, mouth_shape: str = 'closed',
                   talking: bool = False) -> Image.Image:
        """绘制单帧"""
        img = self._create_img()
        draw = ImageDraw.Draw(img)
        
        # 绘制身体
        self._draw_body(draw)
        
        # 绘制头部
        self._draw_head(draw, expression, blink, wink)
        
        # 绘制帽子
        self._draw_hat(draw)
        
        # 绘制嘴巴
        self._draw_mouth(draw, mouth_shape, expression)
        
        return img
    
    def _draw_body(self, draw: ImageDraw.Draw):
        """绘制身体"""
        # 紫袍主体
        self._rect(draw, 14, 28, 20, 18, COLORS['robe'])
        self._rect(draw, 12, 30, 6, 14, COLORS['robe_dark'])
        self._rect(draw, 30, 30, 6, 14, COLORS['robe_dark'])
        
        # 衣领
        self._rect(draw, 20, 28, 8, 3, COLORS['robe_light'])
        self._rect(draw, 22, 28, 4, 1, COLORS['gold'])
        
        # 腰带
        self._rect(draw, 16, 36, 16, 3, COLORS['gold'])
    
    def _draw_head(self, draw: ImageDraw.Draw, expression: str, blink: bool, wink: bool):
        """绘制大头和超大眼睛"""
        # 大头
        for y in range(10, 26):
            width = 12 - abs(y - 18) // 2
            x_start = 12 + abs(y - 18) // 2
            self._rect(draw, x_start, y, width * 2, 1, COLORS['skin'])
        
        # 腮红
        self._px(draw, 16, 20, COLORS['cheek'])
        self._px(draw, 31, 20, COLORS['cheek'])
        
        # 眉毛（根据表情）
        if expression == 'happy':
            # 弯眉
            self._px(draw, 17, 12, COLORS['eyebrow'])
            self._px(draw, 18, 11, COLORS['eyebrow'])
            self._px(draw, 19, 11, COLORS['eyebrow'])
            self._px(draw, 20, 12, COLORS['eyebrow'])
            
            self._px(draw, 27, 12, COLORS['eyebrow'])
            self._px(draw, 28, 11, COLORS['eyebrow'])
            self._px(draw, 29, 11, COLORS['eyebrow'])
            self._px(draw, 30, 12, COLORS['eyebrow'])
        elif expression == 'serious':
            # 皱眉
            self._rect(draw, 16, 13, 6, 2, COLORS['eyebrow'])
            self._rect(draw, 26, 13, 6, 2, COLORS['eyebrow'])
        elif expression == 'surprise':
            # 挑眉
            self._rect(draw, 16, 11, 6, 2, COLORS['eyebrow'])
            self._rect(draw, 26, 11, 6, 2, COLORS['eyebrow'])
        else:
            # 正常
            self._rect(draw, 16, 12, 6, 2, COLORS['eyebrow'])
            self._rect(draw, 26, 12, 6, 2, COLORS['eyebrow'])
        
        # 超大眼睛！
        if blink:
            # 闭眼 - 弧线
            for x in range(16, 22):
                self._px(draw, x, 17, COLORS['eye_black'])
            for x in range(26, 32):
                self._px(draw, x, 17, COLORS['eye_black'])
        elif wink:
            # 眨眼（一只眼）
            # 左眼闭
            for x in range(16, 22):
                self._px(draw, x, 17, COLORS['eye_black'])
            # 右眼睁开
            self._draw_big_eye(draw, 26, 16, open_wide=True)
        else:
            # 正常大眼睛
            eye_open = expression == 'surprise'
            self._draw_big_eye(draw, 17, 15, open_wide=eye_open)
            self._draw_big_eye(draw, 27, 15, open_wide=eye_open)
        
        # 鼻子（小巧）
        self._px(draw, 24, 21, COLORS['skin_shadow'])
    
    def _draw_big_eye(self, draw: ImageDraw.Draw, x: int, y: int, open_wide: bool = False):
        """绘制大眼睛 - 超级夸张版"""
        if open_wide:
            # 惊讶大眼 - 超大！
            # 眼白（8x8）
            self._rect(draw, x-1, y-1, 8, 8, COLORS['eye_white'])
            # 眼珠（4x5）
            self._rect(draw, x+1, y+1, 4, 5, COLORS['eye_black'])
            # 高光
            self._px(draw, x+2, y+2, COLORS['eye_shine'])
            self._px(draw, x+3, y+2, COLORS['eye_shine'])
            self._px(draw, x+2, y+3, COLORS['eye_shine'])
        else:
            # 正常大眼（7x7）
            # 眼白
            self._rect(draw, x-1, y, 7, 6, COLORS['eye_white'])
            # 眼珠（4x4）
            self._rect(draw, x+1, y+1, 4, 4, COLORS['eye_black'])
            # 高光
            self._px(draw, x+2, y+2, COLORS['eye_shine'])
            self._px(draw, x+3, y+2, COLORS['eye_shine'])
    
    def _draw_hat(self, draw: ImageDraw.Draw):
        """绘制帽子"""
        # 帽顶
        for y in range(4, 12):
            width = 14 - (y - 4) if y < 8 else 10
            x_start = 11 + (10 - width) // 2
            self._rect(draw, x_start, y, width * 2, 1, COLORS['hat'])
        
        # 帽翅
        self._rect(draw, 6, 10, 10, 3, COLORS['hat'])
        self._rect(draw, 32, 10, 10, 3, COLORS['hat'])
        
        # 红边
        self._rect(draw, 12, 12, 24, 2, COLORS['hat_red'])
        
        # 金装饰
        self._px(draw, 8, 11, COLORS['hat_gold'])
        self._px(draw, 39, 11, COLORS['hat_gold'])
    
    def _draw_mouth(self, draw: ImageDraw.Draw, shape: str, expression: str):
        """绘制嘴巴"""
        if shape == 'open':
            # 张嘴说话
            self._rect(draw, 21, 24, 6, 4, COLORS['mouth_open'])
        elif shape == 'small':
            # 微张
            self._rect(draw, 22, 25, 4, 2, COLORS['mouth'])
        else:
            # 闭嘴
            if expression == 'happy':
                # 微笑
                self._px(draw, 22, 25, COLORS['mouth'])
                self._px(draw, 23, 26, COLORS['mouth'])
                self._px(draw, 24, 26, COLORS['mouth'])
                self._px(draw, 25, 25, COLORS['mouth'])
            else:
                # 普通
                self._rect(draw, 22, 25, 4, 1, COLORS['mouth'])


class PixelWeizhengV4:
    """大眼萌版像素魏征"""
    
    def __init__(self, size: int = 140, on_click: Optional[Callable] = None,
                 on_exit: Optional[Callable] = None):
        self.size = size
        self.on_click = on_click
        self.on_exit = on_exit
        
        self.sprite = CutePixelSprite(size)
        self.window: Optional[Toplevel] = None
        self.label: Optional[tk.Label] = None
        
        self.photo_idle: List[ImageTk.PhotoImage] = []
        self.photo_talk: List[ImageTk.PhotoImage] = []
        
        self.is_talking = False
        self.current_frame = 0
        self.bubble_window = None
    
    def show(self, parent: Optional[tk.Tk] = None):
        """显示窗口"""
        if self.window is not None:
            return
        
        if parent is None:
            self.root = tk.Tk()
            self.root.withdraw()
        else:
            self.root = parent
        
        # 创建窗口
        self.window = Toplevel(self.root)
        self.window.title("魏征")
        
        window_size = self.size + 16
        self.window.geometry(f"{window_size}x{window_size}")
        
        # 无边框、置顶、透明背景
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        self.window.attributes('-transparentcolor', '#F0F0F0')
        
        # 定位右下角
        self._position_bottom_right()
        
        # 创建标签
        self.label = tk.Label(self.window, bg='#F0F0F0')
        self.label.pack(expand=True)
        
        # 绑定事件
        self.label.bind('<Button-1>', self._on_click)
        self._bind_drag()
        self._bind_menu()  # 右键菜单
        
        # 准备图像
        self._prepare_images()
        
        # 开始动画
        self._animate()
    
    def _position_bottom_right(self):
        """定位到右下角"""
        self.window.update_idletasks()
        screen_w = self.window.winfo_screenwidth()
        screen_h = self.window.winfo_screenheight()
        
        window_size = self.size + 16
        x = screen_w - window_size - 20
        y = screen_h - window_size - 80
        
        self.window.geometry(f"+{x}+{y}")
        
        # 保存对话框位置
        self.bubble_x = x - 160
        self.bubble_y = y - 70
    
    def _prepare_images(self):
        """准备图像"""
        for img in self.sprite.frames_idle:
            self.photo_idle.append(ImageTk.PhotoImage(img))
        for img in self.sprite.frames_talk:
            self.photo_talk.append(ImageTk.PhotoImage(img))
    
    def _bind_drag(self):
        """绑定左键拖拽"""
        self.drag_data = {"x": 0, "y": 0}
        
        def start(event):
            self.drag_data["x"] = event.x_root - self.window.winfo_x()
            self.drag_data["y"] = event.y_root - self.window.winfo_y()
        
        def drag(event):
            x = event.x_root - self.drag_data["x"]
            y = event.y_root - self.drag_data["y"]
            self.window.geometry(f"+{x}+{y}")
            self.bubble_x = x - 160
            self.bubble_y = y - 70
        
        self.window.bind('<Button-1>', start)
        self.window.bind('<B1-Motion>', drag)
    
    def _bind_menu(self):
        """绑定右键菜单"""
        menu = Menu(self.window, tearoff=0)
        menu.add_command(label="显示/隐藏", command=self._toggle_visibility)
        menu.add_separator()
        menu.add_command(label="退出", command=self._exit)
        
        def show_menu(event):
            menu.post(event.x_root, event.y_root)
        
        self.window.bind('<Button-3>', show_menu)
        self.label.bind('<Button-3>', show_menu)
    
    def _toggle_visibility(self):
        """切换可见性"""
        if self.window:
            if self.window.winfo_viewable():
                self.window.withdraw()
            else:
                self.window.deiconify()
    
    def _exit(self):
        """退出"""
        if self.on_exit:
            self.on_exit()
        self.hide()
        if hasattr(self, 'root') and self.root:
            self.root.quit()
    
    def _on_click(self, event):
        """左键点击"""
        if self.on_click:
            self.on_click()
    
    def _animate(self):
        """动画循环"""
        if self.window is None:
            return
        
        frames = self.photo_talk if self.is_talking else self.photo_idle
        speed = 80 if self.is_talking else 180
        
        if frames:
            self.current_frame = (self.current_frame + 1) % len(frames)
            self.label.config(image=frames[self.current_frame])
        
        self.root.after(speed, self._animate)
    
    def talk(self, text: str = "陛下！臣有话说！", duration: float = 3.0):
        """说话动画 + 对话框"""
        self.is_talking = True
        self._show_bubble(text)
        self.root.after(int(duration * 1000), self._stop_talking)
    
    def _stop_talking(self):
        """停止说话"""
        self.is_talking = False
        self._hide_bubble()
    
    def _show_bubble(self, text: str):
        """显示对话框"""
        self._hide_bubble()
        
        self.bubble_window = Toplevel(self.root)
        self.bubble_window.overrideredirect(True)
        self.bubble_window.attributes('-topmost', True)
        
        x, y = self.bubble_x, self.bubble_y
        self.bubble_window.geometry(f"150x70+{x}+{y}")
        
        # 气泡画布
        canvas = Canvas(self.bubble_window, width=150, height=70,
                       bg='#F0F0F0', highlightthickness=0)
        canvas.pack()
        
        # 圆角气泡
        canvas.create_polygon(
            8, 8, 142, 8, 142, 52, 90, 52, 80, 62, 70, 52, 8, 52,
            fill='white', outline='#333', width=2, smooth=True
        )
        
        # 文字
        canvas.create_text(75, 30, text=text, font=('Microsoft YaHei', 10, 'bold'),
                          fill='#333', width=130)
    
    def _hide_bubble(self):
        """隐藏对话框"""
        if self.bubble_window:
            self.bubble_window.destroy()
            self.bubble_window = None
    
    def hide(self):
        """隐藏窗口"""
        self._hide_bubble()
        if self.window:
            self.window.destroy()
            self.window = None


# 测试
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    
    weizheng = PixelWeizhengV4(size=140)
    weizheng.show(parent=root)
    weizheng.talk("陛下好！我是魏征！", duration=3.0)
    
    root.mainloop()
