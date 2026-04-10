"""
像素魏征动画 V3 - 终极美化版

特色：
- 更精致的64x64像素网格，256x256高清显示
- 飘动的长胡须动画（使用正弦波模拟飘动）
- 说话时显示漫画风格对话框
- 丰富的表情变化（挑眉、瞪眼、点头）
- 唐朝文官经典形象（乌纱帽、紫袍、玉带）
"""

import tkinter as tk
from tkinter import Toplevel, Canvas
from PIL import Image, ImageDraw, ImageTk, ImageFont
import math
import random
import time
from typing import Optional, Callable, List, Tuple


# 精美配色 - 唐代风格
PALETTE = {
    # 肤色层次
    'skin': '#FFE4D6',
    'skin_light': '#FFF5F0',
    'skin_mid': '#F5D0C0',
    'skin_shadow': '#E8C0B0',
    'skin_dark': '#D4A080',
    
    # 乌纱帽
    'hat': '#1A1A2E',
    'hat_light': '#2A2A4E',
    'hat_wing': '#151528',
    'hat_red': '#C41E3A',
    'hat_gold': '#FFD700',
    
    # 紫袍（三品以上）
    'robe': '#7B2D6B',
    'robe_light': '#9B4D8B',
    'robe_dark': '#5B1D4B',
    'robe_shadow': '#3D0D30',
    
    # 金色装饰
    'gold': '#D4AF37',
    'gold_light': '#FFD700',
    'gold_dark': '#B8941F',
    
    # 胡须（多层次白）
    'beard_1': '#FFFFFF',  # 高光
    'beard_2': '#F0F0F0',  # 主色
    'beard_3': '#E0E0E0',  # 阴影
    'beard_4': '#D0D0D0',  # 暗部
    
    # 笏板
    'board': '#E8D4B8',
    'board_light': '#F5E8D0',
    'board_dark': '#D4C0A0',
    
    # 五官
    'eye': '#1A1A1A',
    'eye_white': '#FFFFFF',
    'mouth': '#8B4513',
    'mouth_open': '#5C2D0E',
    'cheek': '#FFB6C1',
    'eyebrow': '#E8E8E8',
    
    # 轮廓
    'outline': '#0D0D0D',
    'outline_soft': '#3D3D3D',
}


class DeluxePixelSprite:
    """豪华版像素精灵"""
    
    def __init__(self, size: int = 160):
        self.size = size
        self.scale = max(2, size // 64)
        self.frames_idle: List[Image.Image] = []
        self.frames_talk: List[Image.Image] = []
        self.frames_beard_wave: List[Image.Image] = []
        
        self.time = 0  # 用于动画计算
        self._generate_frames()
    
    def _create_img(self) -> Image.Image:
        return Image.new('RGBA', (self.size, self.size), (0, 0, 0, 0))
    
    def _px(self, draw: ImageDraw.Draw, x: int, y: int, color: str):
        """绘制像素"""
        s = self.scale
        draw.rectangle([x*s, y*s, (x+1)*s-1, (y+1)*s-1], fill=color)
    
    def _rect(self, draw: ImageDraw.Draw, x: int, y: int, w: int, h: int, color: str):
        """绘制矩形"""
        s = self.scale
        draw.rectangle([x*s, y*s, (x+w)*s-1, (y+h)*s-1], fill=color)
    
    def _line(self, draw: ImageDraw.Draw, x1: int, y1: int, x2: int, y2: int, color: str):
        """绘制线条"""
        s = self.scale
        draw.line([x1*s, y1*s, x2*s, y2*s], fill=color, width=s)
    
    def _generate_frames(self):
        """生成所有动画帧"""
        # 空闲动画 - 多种表情
        idle_configs = [
            # (time_offset, expression, blink, beard_wave)
            (0, 'normal', False, 0),
            (0.2, 'normal', False, 1),
            (0.4, 'normal', False, 2),
            (0.6, 'normal', False, 1),
            (0.8, 'normal', False, 0),
            (1.0, 'normal', True, 0),   # 眨眼
            (1.2, 'normal', False, 0),
            (1.4, 'thinking', False, 0), # 思考（挑眉）
            (1.6, 'thinking', False, 1),
            (1.8, 'thinking', False, 0),
            (2.0, 'serious', False, 0),  # 严肃
            (2.2, 'serious', False, 1),
            (2.4, 'normal', False, 0),
            (2.6, 'normal', False, 0),
            (2.8, 'normal', True, 0),   # 眨眼
            (3.0, 'normal', False, 0),
        ]
        
        for t, expr, blink, beard_wave in idle_configs:
            img = self._draw_frame(expression=expr, blink=blink, 
                                  beard_wave=beard_wave, talking=False)
            self.frames_idle.append(img)
        
        # 说话动画 - 嘴型变化 + 胡须飘动
        talk_configs = [
            # (mouth_shape, beard_wave_intensity, expression)
            ('closed', 0, 'normal'),
            ('small', 1, 'normal'),
            ('medium', 2, 'serious'),
            ('large', 3, 'serious'),
            ('medium', 2, 'serious'),
            ('small', 1, 'normal'),
            ('closed', 0, 'normal'),
            ('small', 2, 'normal'),
            ('large', 3, 'serious'),
            ('medium', 2, 'serious'),
            ('small', 1, 'normal'),
            ('closed', 0, 'normal'),
        ]
        
        for mouth, beard, expr in talk_configs:
            img = self._draw_frame(expression=expr, mouth_shape=mouth,
                                  beard_wave=beard, talking=True)
            self.frames_talk.append(img)
    
    def _draw_frame(self, expression: str = 'normal', blink: bool = False,
                   mouth_shape: str = 'closed', beard_wave: int = 0,
                   talking: bool = False) -> Image.Image:
        """绘制单帧"""
        img = self._create_img()
        draw = ImageDraw.Draw(img)
        
        # 绘制身体
        self._draw_body(draw)
        
        # 绘制头部
        self._draw_head(draw, expression, blink)
        
        # 绘制帽子
        self._draw_hat(draw)
        
        # 绘制胡须（带飘动效果）
        self._draw_beard(draw, beard_wave, talking)
        
        # 绘制笏板
        self._draw_board(draw)
        
        return img
    
    def _draw_body(self, draw: ImageDraw.Draw):
        """绘制紫袍身体"""
        # 主袍体 - 梯形轮廓
        for y in range(28, 64):
            width = 24 - (y - 28) // 3
            x_start = 20 + (y - 28) // 3
            self._rect(draw, x_start, y, width * 2, 1, PALETTE['robe'])
        
        # 衣领
        self._rect(draw, 28, 28, 8, 3, PALETTE['robe_light'])
        self._rect(draw, 30, 28, 4, 1, PALETTE['gold'])
        
        # 腰带（玉带）
        self._rect(draw, 22, 36, 20, 4, PALETTE['gold'])
        self._rect(draw, 24, 37, 16, 2, PALETTE['gold_light'])
        
        # 衣襟装饰
        self._rect(draw, 31, 40, 2, 20, PALETTE['robe_light'])
        
        # 袖子
        self._rect(draw, 10, 30, 8, 20, PALETTE['robe_dark'])
        self._rect(draw, 46, 30, 8, 20, PALETTE['robe_dark'])
        
        # 袍子阴影
        self._rect(draw, 20, 58, 24, 4, PALETTE['robe_shadow'])
    
    def _draw_head(self, draw: ImageDraw.Draw, expression: str, blink: bool):
        """绘制头部"""
        # 脸型 - 椭圆
        for y in range(10, 26):
            width = 10 - abs(y - 18) // 2
            x_start = 22 + abs(y - 18) // 2
            self._rect(draw, x_start, y, width * 2, 1, PALETTE['skin'])
        
        # 脸颊阴影
        self._rect(draw, 24, 20, 16, 4, PALETTE['skin_shadow'])
        
        # 腮红
        self._px(draw, 26, 18, PALETTE['cheek'])
        self._px(draw, 37, 18, PALETTE['cheek'])
        
        # 眉毛（根据表情变化）
        if expression == 'thinking':
            # 挑眉 - 思考表情
            self._rect(draw, 24, 13, 6, 2, PALETTE['eyebrow'])
            self._rect(draw, 34, 12, 6, 2, PALETTE['eyebrow'])
        elif expression == 'serious':
            # 皱眉 - 严肃表情
            self._rect(draw, 24, 14, 6, 2, PALETTE['eyebrow'])
            self._rect(draw, 34, 14, 6, 2, PALETTE['eyebrow'])
        else:
            # 正常
            self._rect(draw, 24, 13, 6, 2, PALETTE['eyebrow'])
            self._rect(draw, 34, 13, 6, 2, PALETTE['eyebrow'])
        
        # 眼睛
        if blink:
            # 闭眼
            self._rect(draw, 25, 16, 5, 1, PALETTE['outline'])
            self._rect(draw, 34, 16, 5, 1, PALETTE['outline'])
        else:
            # 睁眼
            self._rect(draw, 25, 15, 5, 4, PALETTE['eye_white'])
            self._rect(draw, 34, 15, 5, 4, PALETTE['eye_white'])
            # 眼珠
            self._px(draw, 27, 16, PALETTE['eye'])
            self._px(draw, 36, 16, PALETTE['eye'])
            # 高光
            self._px(draw, 28, 15, PALETTE['eye_white'])
            self._px(draw, 37, 15, PALETTE['eye_white'])
        
        # 鼻子
        self._px(draw, 32, 19, PALETTE['skin_dark'])
        
        # 嘴巴（根据嘴型）
        if expression == 'serious':
            # 严肃 - 一字嘴
            self._rect(draw, 29, 22, 6, 1, PALETTE['mouth'])
        else:
            # 正常微笑
            self._px(draw, 29, 22, PALETTE['mouth'])
            self._px(draw, 30, 22, PALETTE['mouth'])
            self._px(draw, 31, 22, PALETTE['mouth'])
            self._px(draw, 32, 22, PALETTE['mouth'])
    
    def _draw_hat(self, draw: ImageDraw.Draw):
        """绘制乌纱帽"""
        # 帽顶 - 圆弧
        for y in range(4, 12):
            width = 14 - (y - 4) if y < 8 else 10
            x_start = 24 + (10 - width) // 2
            self._rect(draw, x_start, y, width * 2, 1, PALETTE['hat'])
        
        # 帽身
        self._rect(draw, 20, 10, 24, 4, PALETTE['hat'])
        
        # 帽翅（向两侧展开）
        self._rect(draw, 8, 11, 12, 3, PALETTE['hat_wing'])
        self._rect(draw, 44, 11, 12, 3, PALETTE['hat_wing'])
        
        # 红边装饰
        self._rect(draw, 20, 13, 24, 2, PALETTE['hat_red'])
        
        # 金色装饰点
        self._px(draw, 10, 12, PALETTE['hat_gold'])
        self._px(draw, 53, 12, PALETTE['hat_gold'])
        
        # 帽顶宝石
        self._rect(draw, 31, 3, 2, 1, PALETTE['hat_gold'])
    
    def _draw_beard(self, draw: ImageDraw.Draw, wave: int, talking: bool):
        """绘制飘动的胡须"""
        # 山羊胡（嘴下）
        self._rect(draw, 30, 24, 4, 3, PALETTE['beard_2'])
        
        # 长胡须 - 使用正弦波模拟飘动
        base_x = 32
        beard_length = 20
        
        for i in range(beard_length):
            y = 27 + i
            
            # 计算飘动偏移
            if talking and wave > 0:
                # 说话时飘动更剧烈
                offset = int(math.sin((i / 4) + wave) * (wave * 0.8))
            else:
                # 空闲时轻微飘动
                offset = int(math.sin(i / 6) * 0.5)
            
            x = base_x + offset
            
            # 胡须宽度随长度变细
            if i < 5:
                width = 4
                color = PALETTE['beard_1'] if i < 2 else PALETTE['beard_2']
            elif i < 12:
                width = 3
                color = PALETTE['beard_2'] if i % 2 == 0 else PALETTE['beard_3']
            else:
                width = 2
                color = PALETTE['beard_3'] if i % 2 == 0 else PALETTE['beard_4']
            
            self._rect(draw, x - width // 2, y, width, 1, color)
        
        # 胡须尖端分叉
        tip_y = 27 + beard_length
        tip_offset = int(math.sin((beard_length / 4) + wave) * wave) if talking else 0
        self._px(draw, 30 + tip_offset, tip_y, PALETTE['beard_4'])
        self._px(draw, 34 + tip_offset, tip_y, PALETTE['beard_4'])
    
    def _draw_board(self, draw: ImageDraw.Draw):
        """绘制笏板"""
        # 木板主体
        for y in range(26, 44):
            x = 46 + (y - 26) // 8
            self._rect(draw, x, y, 4, 1, PALETTE['board'])
        
        # 纹理
        self._rect(draw, 47, 28, 2, 14, PALETTE['board_light'])
        
        # 阴影
        self._rect(draw, 49, 28, 1, 14, PALETTE['board_dark'])


class SpeechBubble:
    """对话框类"""
    
    def __init__(self, parent: tk.Tk, x: int, y: int, width: int = 200, height: int = 80):
        self.parent = parent
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        self.window: Optional[Toplevel] = None
        self.text_var = tk.StringVar()
        
    def show(self, text: str, duration: float = 3.0):
        """显示对话框"""
        self.hide()
        
        self.window = Toplevel(self.parent)
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        self.window.attributes('-transparentcolor', '#F0F0F0')
        
        # 创建画布
        canvas = Canvas(self.window, width=self.width, height=self.height, 
                       bg='#F0F0F0', highlightthickness=0)
        canvas.pack()
        
        # 绘制对话框（圆角矩形 + 小尾巴）
        padding = 8
        bubble_color = 'white'
        border_color = '#333'
        
        # 主体气泡（使用圆角多边形模拟）
        r = 15  # 圆角半径
        x1, y1 = padding, padding
        x2, y2 = self.width - padding, self.height - padding - 10
        
        # 绘制圆角矩形轮廓
        points = [
            x1 + r, y1,           # 上边左
            x2 - r, y1,           # 上边右
            x2, y1,               # 右上 corner
            x2, y1 + r,           # 右边上
            x2, y2 - r,           # 右边下
            x2, y2,               # 右下 corner
            x2 - r, y2,           # 下边右
            x1 + r, y2,           # 下边左
            x1, y2,               # 左下 corner
            x1, y2 - r,           # 左边下
            x1, y1 + r,           # 左边上
            x1, y1,               # 左上 corner
        ]
        
        canvas.create_polygon(
            points,
            fill=bubble_color, outline=border_color, width=2,
            smooth=True  # 平滑边角
        )
        
        # 小尾巴（指向魏征）
        tail_x = self.width // 2
        tail_y = self.height - padding - 10
        canvas.create_polygon(
            tail_x - 10, tail_y,
            tail_x + 10, tail_y,
            tail_x, tail_y + 15,
            fill=bubble_color, outline=border_color, width=2
        )
        
        # 文字
        canvas.create_text(
            self.width // 2, self.height // 2 - 5,
            text=text, font=('Microsoft YaHei', 10),
            fill='#333', width=self.width - 30
        )
        
        # 定位
        self.window.geometry(f"{self.width}x{self.height}+{self.x}+{self.y}")
        
        # 自动关闭
        self.window.after(int(duration * 1000), self.hide)
    
    def hide(self):
        """隐藏对话框"""
        if self.window:
            self.window.destroy()
            self.window = None


class PixelWeizhengV3:
    """终极美化版像素魏征"""
    
    def __init__(self, size: int = 160, on_click: Optional[Callable] = None):
        self.size = size
        self.on_click = on_click
        self.sprite = DeluxePixelSprite(size)
        
        self.window: Optional[Toplevel] = None
        self.label: Optional[tk.Label] = None
        self.photo_images_idle: List[ImageTk.PhotoImage] = []
        self.photo_images_talk: List[ImageTk.PhotoImage] = []
        
        self.is_talking = False
        self.current_frame = 0
        self.animation_id: Optional[int] = None
        
        # 对话框
        self.bubble: Optional[SpeechBubble] = None
        
        # 动画速度
        self.idle_speed = 150
        self.talk_speed = 100
    
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
        
        window_size = self.size + 20
        self.window.geometry(f"{window_size}x{window_size}")
        
        # 无边框、置顶、透明背景
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        self.window.attributes('-transparentcolor', '#F0F0F0')
        
        # 定位到右下角
        self._position_bottom_right()
        
        # 创建标签
        self.label = tk.Label(self.window, bg='#F0F0F0')
        self.label.pack(expand=True)
        
        # 绑定事件
        self.label.bind('<Button-1>', self._on_click)
        self._bind_drag()
        
        # 准备图像
        self._prepare_images()
        
        # 开始动画
        self._animate()
    
    def _position_bottom_right(self):
        """定位到右下角"""
        self.window.update_idletasks()
        screen_w = self.window.winfo_screenwidth()
        screen_h = self.window.winfo_screenheight()
        
        window_size = self.size + 20
        x = screen_w - window_size - 30
        y = screen_h - window_size - 120
        
        self.window.geometry(f"+{x}+{y}")
        self.bubble_x = x - 180
        self.bubble_y = y - 60
    
    def _prepare_images(self):
        """准备图像"""
        for img in self.sprite.frames_idle:
            self.photo_images_idle.append(ImageTk.PhotoImage(img))
        for img in self.sprite.frames_talk:
            self.photo_images_talk.append(ImageTk.PhotoImage(img))
    
    def _bind_drag(self):
        """绑定拖拽"""
        self.drag_data = {"x": 0, "y": 0}
        
        def start(event):
            self.drag_data["x"] = event.x_root - self.window.winfo_x()
            self.drag_data["y"] = event.y_root - self.window.winfo_y()
        
        def drag(event):
            x = event.x_root - self.drag_data["x"]
            y = event.y_root - self.drag_data["y"]
            self.window.geometry(f"+{x}+{y}")
            # 更新对话框位置
            self.bubble_x = x - 180
            self.bubble_y = y - 60
        
        self.window.bind('<Button-3>', start)
        self.window.bind('<B3-Motion>', drag)
    
    def _on_click(self, event):
        """点击处理"""
        if self.on_click:
            self.on_click()
    
    def _animate(self):
        """动画循环"""
        if self.window is None:
            return
        
        # 更新帧
        if self.is_talking:
            frames = self.photo_images_talk
            speed = self.talk_speed
        else:
            frames = self.photo_images_idle
            speed = self.idle_speed
        
        if frames:
            self.current_frame = (self.current_frame + 1) % len(frames)
            self.label.config(image=frames[self.current_frame])
        
        # 继续动画
        self.animation_id = self.root.after(speed, self._animate)
    
    def talk(self, text: str = "陛下，臣有话说！", duration: float = 3.0):
        """说话动画 + 对话框"""
        self.is_talking = True
        
        # 显示对话框
        if self.bubble is None:
            self.bubble = SpeechBubble(self.root, self.bubble_x, self.bubble_y)
        self.bubble.show(text, duration)
        
        # 定时停止
        self.root.after(int(duration * 1000), self.stop_talking)
    
    def stop_talking(self):
        """停止说话"""
        self.is_talking = False
    
    def hide(self):
        """隐藏"""
        if self.bubble:
            self.bubble.hide()
        if self.window:
            if self.animation_id:
                self.root.after_cancel(self.animation_id)
            self.window.destroy()
            self.window = None


# 测试
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    
    weizheng = PixelWeizhengV3(size=160)
    weizheng.show(parent=root)
    weizheng.talk("陛下！臣有本奏！", duration=4.0)
    
    root.after(6000, lambda: (weizheng.hide(), root.quit()))
    root.mainloop()
