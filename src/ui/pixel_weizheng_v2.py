"""
像素魏征动画 V2 - 美化版

更精致的像素艺术风格：
- 更细腻的像素绘制（64x64基础网格）
- 丰富的配色和光影
- 更流畅的动画（16帧空闲 + 12帧说话）
- 唐朝官员的经典形象
"""

import tkinter as tk
from tkinter import Toplevel
from PIL import Image, ImageDraw, ImageTk, ImageFilter
import threading
import time
import random
import math
from typing import Optional, Callable, List, Tuple


# 精美配色方案 - 唐朝风格
PALETTE = {
    # 肤色
    'skin_base': '#FFE4D6',
    'skin_light': '#FFF0E8',
    'skin_shadow': '#E8C4B8',
    'skin_dark': '#D4A894',
    
    # 官帽 - 乌纱帽
    'hat_black': '#1A1A2E',
    'hat_dark': '#0F0F1A',
    'hat_highlight': '#2D2D44',
    'hat_wing': '#16213E',
    'hat_red': '#C41E3A',
    'hat_gold': '#D4AF37',
    
    # 紫袍 - 唐朝三品以上
    'robe_purple': '#6B2D5C',
    'robe_light': '#8B3D7C',
    'robe_dark': '#4A1D3C',
    'robe_highlight': '#A64D8C',
    'robe_shadow': '#3D1530',
    
    # 金饰
    'gold_light': '#FFD700',
    'gold': '#D4AF37',
    'gold_dark': '#B8941F',
    
    # 胡须
    'beard_white': '#F5F5F5',
    'beard_shadow': '#E0E0E0',
    'beard_dark': '#C0C0C0',
    
    # 笏板
    'board': '#DEB887',
    'board_light': '#F5DEB3',
    'board_dark': '#C19A6B',
    
    # 五官
    'eye_black': '#0D0D0D',
    'eye_white': '#FFFFFF',
    'mouth': '#8B4513',
    'mouth_open': '#5C2D0E',
    'cheek': '#FFB6C1',
    
    # 轮廓
    'outline': '#1A1A1A',
    'outline_light': '#3D3D3D',
}


class EnhancedPixelSprite:
    """增强版像素精灵"""
    
    def __init__(self, size: int = 128):
        self.size = size
        self.scale = size // 64  # 64x64基础网格
        self.frames: List[Image.Image] = []
        self.talking_frames: List[Image.Image] = []
        self._generate_all_frames()
    
    def _create_image(self) -> Image.Image:
        """创建透明背景图像"""
        return Image.new('RGBA', (self.size, self.size), (0, 0, 0, 0))
    
    def _draw_pixel(self, draw: ImageDraw.Draw, x: int, y: int, 
                   color: str, size: int = None, outline: bool = False):
        """绘制像素块"""
        if size is None:
            size = self.scale
        
        x1, y1 = x * size, y * size
        x2, y2 = (x + 1) * size - 1, (y + 1) * size - 1
        
        draw.rectangle([x1, y1, x2, y2], fill=color)
        
        if outline:
            draw.rectangle([x1, y1, x2, y2], outline=PALETTE['outline'], width=1)
    
    def _draw_rect(self, draw: ImageDraw.Draw, x: int, y: int, 
                  w: int, h: int, color: str, outline: bool = False):
        """绘制矩形区域"""
        size = self.scale
        x1, y1 = x * size, y * size
        x2, y2 = (x + w) * size - 1, (y + h) * size - 1
        
        draw.rectangle([x1, y1, x2, y2], fill=color)
        
        if outline:
            draw.rectangle([x1, y1, x2, y2], outline=PALETTE['outline'], width=1)
    
    def _draw_circle(self, draw: ImageDraw.Draw, cx: int, cy: int, 
                    r: int, color: str):
        """绘制圆形/椭圆"""
        size = self.scale
        x1 = (cx - r) * size
        y1 = (cy - r) * size
        x2 = (cx + r) * size - 1
        y2 = (cy + r) * size - 1
        draw.ellipse([x1, y1, x2, y2], fill=color)
    
    def _generate_all_frames(self):
        """生成所有动画帧"""
        # 空闲动画 - 更丰富的动作
        # 0-3: 正常呼吸
        # 4-7: 点头
        # 8-11: 眨眼
        # 12-15: 捋胡须
        
        idle_poses = [
            (0, 0, False, False, 0),    # 正常
            (0, 1, False, False, 0),    # 下沉
            (0, 0, False, False, 0),    # 正常
            (0, -1, False, False, 0),   # 上浮
            (0, 0, True, False, 0),     # 点头开始
            (0, 1, True, False, 0),     # 点头
            (0, 0, False, False, 0),    # 恢复
            (0, 0, False, False, 0),    # 停顿
            (0, 0, False, True, 0),     # 眨眼
            (0, 0, False, False, 0),    # 睁眼
            (0, 0, False, False, 1),    # 捋胡须
            (0, 0, False, False, 0),    # 恢复
            (0, 0, False, False, 0),    # 正常
            (0, 0, False, False, 0),    # 正常
            (0, 0, False, False, 0),    # 正常
            (0, 0, False, False, 0),    # 正常
        ]
        
        for offset_x, offset_y, nodding, blink, beard_pose in idle_poses:
            img = self._draw_frame(offset_x, offset_y, False, blink, nodding, beard_pose)
            self.frames.append(img)
        
        # 说话动画 - 更丰富的口型
        talk_poses = [
            (0, 0, False, False, False),   # 闭嘴
            (0, 0, True, False, False),    # 微张
            (0, 0, True, False, False),    # 微张
            (0, 0, False, False, False),   # 闭嘴
            (0, 0, True, False, True),     # 大张
            (0, 0, True, False, True),     # 大张
            (0, 0, False, False, False),   # 闭嘴
            (0, 0, True, False, False),    # 微张
            (0, 0, True, False, True),     # 大张
            (0, 0, True, False, False),    # 微张
            (0, 0, False, False, False),   # 闭嘴
            (0, 0, True, False, False),    # 微张
        ]
        
        for offset_x, offset_y, mouth_open, blink, wide_open in talk_poses:
            img = self._draw_frame(offset_x, offset_y, mouth_open, blink, False, 0, wide_open)
            self.talking_frames.append(img)
    
    def _draw_frame(self, offset_x: int = 0, offset_y: int = 0,
                   mouth_open: bool = False, blink: bool = False,
                   nodding: bool = False, beard_pose: int = 0,
                   wide_open: bool = False) -> Image.Image:
        """
        绘制单帧
        
        布局 (64x64网格):
        - 帽子: y=4-14
        - 脸部: y=12-28
        - 身体: y=26-62
        """
        img = self._create_image()
        draw = ImageDraw.Draw(img)
        
        ox, oy = offset_x, offset_y  # 偏移量
        
        # ========== 绘制身体（紫袍）==========
        # 主袍
        self._draw_robe(draw, ox, oy)
        
        # ========== 绘制头部 ==========
        self._draw_head(draw, ox, oy, blink, nodding)
        
        # ========== 绘制帽子 ==========
        self._draw_hat(draw, ox, oy, nodding)
        
        # ========== 绘制面部五官 ==========
        self._draw_face(draw, ox, oy, mouth_open, blink, wide_open)
        
        # ========== 绘制胡须 ==========
        self._draw_beard(draw, ox, oy, beard_pose)
        
        # ========== 绘制笏板 ==========
        self._draw_board(draw, ox, oy)
        
        # 应用轻微的高斯模糊使边缘更柔和（可选）
        # img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        return img
    
    def _draw_robe(self, draw: ImageDraw.Draw, ox: int, oy: int):
        """绘制紫袍身体"""
        # 主袍体
        self._draw_rect(draw, 16+ox, 32+oy, 32, 30, PALETTE['robe_purple'], True)
        
        # 衣领
        self._draw_rect(draw, 26+ox, 30+oy, 12, 4, PALETTE['robe_light'])
        self._draw_rect(draw, 28+ox, 30+oy, 8, 2, PALETTE['gold'])
        
        # 衣襟装饰
        self._draw_rect(draw, 30+ox, 36+oy, 4, 24, PALETTE['robe_highlight'])
        
        # 腰带
        self._draw_rect(draw, 18+ox, 42+oy, 28, 4, PALETTE['gold'])
        self._draw_rect(draw, 20+ox, 43+oy, 24, 2, PALETTE['gold_light'])
        
        # 袖子
        self._draw_rect(draw, 8+ox, 34+oy, 10, 16, PALETTE['robe_purple'], True)
        self._draw_rect(draw, 46+ox, 34+oy, 10, 16, PALETTE['robe_purple'], True)
        
        # 袍子阴影
        self._draw_rect(draw, 16+ox, 58+oy, 32, 4, PALETTE['robe_shadow'])
    
    def _draw_head(self, draw: ImageDraw.Draw, ox: int, oy: int, blink: bool, nodding: bool):
        """绘制头部"""
        # 脸型 - 椭圆
        head_y = 16 + oy
        if nodding:
            head_y += 2
        
        # 脸部主体
        self._draw_rect(draw, 22+ox, head_y, 20, 16, PALETTE['skin_base'])
        
        # 脸颊阴影
        self._draw_rect(draw, 22+ox, head_y+12, 20, 4, PALETTE['skin_shadow'])
        
        # 腮红
        self._draw_pixel(draw, 24+ox, head_y+10, PALETTE['cheek'])
        self._draw_pixel(draw, 38+ox, head_y+10, PALETTE['cheek'])
    
    def _draw_hat(self, draw: ImageDraw.Draw, ox: int, oy: int, nodding: bool):
        """绘制乌纱帽"""
        hat_y = 6 + oy
        if nodding:
            hat_y += 1
        
        # 帽子主体 - 圆顶
        self._draw_rect(draw, 18+ox, hat_y, 28, 10, PALETTE['hat_black'], True)
        
        # 帽子高光
        self._draw_rect(draw, 20+ox, hat_y+2, 6, 2, PALETTE['hat_highlight'])
        
        # 帽子红边
        self._draw_rect(draw, 18+ox, hat_y+8, 28, 3, PALETTE['hat_red'])
        
        # 帽翅（两侧展开）
        self._draw_rect(draw, 6+ox, hat_y+6, 12, 3, PALETTE['hat_wing'], True)
        self._draw_rect(draw, 46+ox, hat_y+6, 12, 3, PALETTE['hat_wing'], True)
        
        # 帽翅装饰
        self._draw_pixel(draw, 8+ox, hat_y+7, PALETTE['gold'])
        self._draw_pixel(draw, 56+ox, hat_y+7, PALETTE['gold'])
        
        # 帽子顶部宝石
        self._draw_pixel(draw, 31+ox, hat_y-1, PALETTE['gold'])
        self._draw_pixel(draw, 32+ox, hat_y-1, PALETTE['gold'])
    
    def _draw_face(self, draw: ImageDraw.Draw, ox: int, oy: int, 
                  mouth_open: bool, blink: bool, wide_open: bool):
        """绘制面部五官"""
        face_y = 20 + oy
        
        # 眉毛 - 白色长眉（仙风道骨）
        self._draw_rect(draw, 23+ox, face_y-1, 6, 2, PALETTE['beard_white'])
        self._draw_rect(draw, 35+ox, face_y-1, 6, 2, PALETTE['beard_white'])
        
        # 眼睛
        if blink:
            # 闭眼 - 一条线
            self._draw_rect(draw, 24+ox, face_y+2, 5, 1, PALETTE['outline'])
            self._draw_rect(draw, 35+ox, face_y+2, 5, 1, PALETTE['outline'])
        else:
            # 睁眼
            self._draw_rect(draw, 24+ox, face_y+1, 5, 4, PALETTE['eye_white'])
            self._draw_rect(draw, 35+ox, face_y+1, 5, 4, PALETTE['eye_white'])
            # 眼珠
            self._draw_pixel(draw, 26+ox, face_y+2, PALETTE['eye_black'])
            self._draw_pixel(draw, 37+ox, face_y+2, PALETTE['eye_black'])
        
        # 鼻子
        self._draw_pixel(draw, 31+ox, face_y+5, PALETTE['skin_dark'])
        
        # 嘴巴
        if mouth_open:
            if wide_open:
                # 大张
                self._draw_rect(draw, 28+ox, face_y+8, 8, 4, PALETTE['mouth_open'])
            else:
                # 微张
                self._draw_rect(draw, 29+ox, face_y+8, 6, 2, PALETTE['mouth'])
        else:
            # 闭嘴 - 严肃表情
            self._draw_rect(draw, 28+ox, face_y+9, 8, 1, PALETTE['mouth'])
    
    def _draw_beard(self, draw: ImageDraw.Draw, ox: int, oy: int, pose: int):
        """绘制胡须"""
        beard_y = 30 + oy
        
        # 山羊胡
        self._draw_rect(draw, 30+ox, beard_y, 4, 3, PALETTE['beard_white'])
        
        # 长胡须 - 根据姿势变化
        if pose == 0:
            # 正常垂直
            for i in range(8):
                self._draw_rect(draw, 30+ox, beard_y+3+i, 4, 1, PALETTE['beard_white'])
        else:
            # 捋胡须 - 向一侧偏
            for i in range(8):
                offset = min(i // 2, 2)
                self._draw_rect(draw, 30+ox+offset, beard_y+3+i, 4, 1, PALETTE['beard_white'])
        
        # 胡须尖端分叉
        self._draw_pixel(draw, 29+ox, beard_y+10, PALETTE['beard_shadow'])
        self._draw_pixel(draw, 34+ox, beard_y+10, PALETTE['beard_shadow'])
    
    def _draw_board(self, draw: ImageDraw.Draw, ox: int, oy: int):
        """绘制笏板"""
        # 手持的木板，在身体右侧
        board_x = 44 + ox
        board_y = 28 + oy
        
        # 笏板主体
        self._draw_rect(draw, board_x, board_y, 5, 18, PALETTE['board'], True)
        
        # 纹理
        self._draw_rect(draw, board_x+1, board_y+2, 3, 14, PALETTE['board_light'])
        
        # 阴影
        self._draw_rect(draw, board_x+3, board_y+2, 2, 14, PALETTE['board_dark'])


class PixelWeizhengV2:
    """美化版像素魏征"""
    
    def __init__(self, size: int = 128, on_click: Optional[Callable] = None):
        self.size = size
        self.on_click = on_click
        self.sprite = EnhancedPixelSprite(size)
        
        self.window: Optional[Toplevel] = None
        self.label: Optional[tk.Label] = None
        self.photo_images: List[ImageTk.PhotoImage] = []
        self.talk_photo_images: List[ImageTk.PhotoImage] = []
        
        self.is_talking = False
        self.current_frame = 0
        self.animation_running = False
        
        self.idle_speed = 0.15  # 更快的空闲动画
        self.talk_speed = 0.08  # 更快的说话动画
    
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
        
        # 定位到右下角
        self._position_bottom_right()
        
        # 创建画布
        self.label = tk.Label(self.window, bg='#F0F0F0')
        self.label.pack(expand=True)
        
        # 绑定事件
        self.label.bind('<Button-1>', self._on_click)
        self._bind_drag()
        
        # 准备图像
        self._prepare_images()
        
        # 开始动画
        self._start_animation()
    
    def _position_bottom_right(self):
        """定位到右下角"""
        self.window.update_idletasks()
        screen_w = self.window.winfo_screenwidth()
        screen_h = self.window.winfo_screenheight()
        
        window_size = self.size + 16
        x = screen_w - window_size - 20
        y = screen_h - window_size - 100
        
        self.window.geometry(f"+{x}+{y}")
    
    def _prepare_images(self):
        """转换图像"""
        for img in self.sprite.frames:
            self.photo_images.append(ImageTk.PhotoImage(img))
        for img in self.sprite.talking_frames:
            self.talk_photo_images.append(ImageTk.PhotoImage(img))
    
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
        
        self.window.bind('<Button-3>', start)
        self.window.bind('<B3-Motion>', drag)
    
    def _on_click(self, event):
        if self.on_click:
            self.on_click()
    
    def _start_animation(self):
        """启动动画"""
        if self.animation_running:
            return
        self.animation_running = True
        self._animate_loop()
    
    def _animate_loop(self):
        """动画循环"""
        if not self.animation_running:
            return
        
        try:
            self._update_frame()
            speed = int(self.talk_speed * 1000) if self.is_talking else int(self.idle_speed * 1000)
            self.root.after(speed, self._animate_loop)
        except:
            pass
    
    def _update_frame(self):
        """更新帧"""
        if self.window is None or self.label is None:
            return
        
        if self.is_talking:
            frames = self.talk_photo_images
            self.current_frame = (self.current_frame + 1) % len(frames)
        else:
            frames = self.photo_images
            self.current_frame = (self.current_frame + 1) % len(frames)
        
        if frames:
            self.label.config(image=frames[self.current_frame])
    
    def talk(self, duration: float = 3.0):
        """说话动画"""
        self.is_talking = True
        if self.window:
            self.window.after(int(duration * 1000), self.stop_talking)
    
    def stop_talking(self):
        self.is_talking = False
    
    def hide(self):
        if self.window:
            self.animation_running = False
            self.window.destroy()
            self.window = None


# 测试
if __name__ == "__main__":
    print("启动美化版像素魏征测试...")
    
    root = tk.Tk()
    root.withdraw()
    
    weizheng = PixelWeizhengV2(size=128)
    weizheng.show(parent=root)
    weizheng.talk(duration=5.0)
    
    root.after(6000, lambda: (weizheng.hide(), root.quit()))
    root.mainloop()
