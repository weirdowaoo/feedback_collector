"""
自定义按钮组件 - 使用Canvas绘制避免系统样式干扰
"""

import tkinter as tk
from tkinter import font

try:
    from .theme import DarkThemeManager
except ImportError:
    from ui.theme import DarkThemeManager


class CustomButton(tk.Canvas):
    """完全自定义的按钮组件，使用Canvas绘制"""

    def __init__(self, parent, text="", style="primary", command=None,
                 width=120, height=40, **kwargs):
        super().__init__(parent, width=width, height=height,
                         highlightthickness=0, bd=0, **kwargs)

        self.theme = DarkThemeManager
        self.text = text
        self.style = style
        self.command = command
        self.width = width
        self.height = height

        # 状态
        self.is_pressed = False
        self.is_hovered = False

        # 获取样式配置
        self.colors = self._get_colors()

        # 设置背景
        self.configure(bg=parent.cget('bg') if hasattr(
            parent, 'cget') else '#1e1e1e')

        # 绑定事件
        self.bind("<Button-1>", self._on_click)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

        # 初始绘制
        self._draw()

    def _get_colors(self):
        """获取按钮颜色配置"""
        color_schemes = {
            'primary': {
                'bg': '#007acc',
                'fg': '#ffffff',
                'hover_bg': '#005a9e',
                'pressed_bg': '#004578'
            },
            'secondary': {
                'bg': '#3e3e42',
                'fg': '#ffffff',
                'hover_bg': '#4a4a4f',
                'pressed_bg': '#2e2e32'
            },
            'success': {
                'bg': '#34C759',
                'fg': '#ffffff',
                'hover_bg': '#28A745',
                'pressed_bg': '#1E7E34'
            },
            'danger': {
                'bg': '#FF3B30',
                'fg': '#ffffff',
                'hover_bg': '#D70015',
                'pressed_bg': '#B50012'
            }
        }
        return color_schemes.get(self.style, color_schemes['primary'])

    def _draw(self):
        """绘制按钮"""
        self.delete("all")

        # 确定当前颜色
        if self.is_pressed:
            bg_color = self.colors['pressed_bg']
        elif self.is_hovered:
            bg_color = self.colors['hover_bg']
        else:
            bg_color = self.colors['bg']

        fg_color = self.colors['fg']

        # 绘制圆角矩形背景
        self._draw_rounded_rect(2, 2, self.width-2, self.height-2,
                                radius=6, fill=bg_color)

        # 绘制文字
        text_font = font.Font(family="SF Pro Display",
                              size=13, weight="normal")
        self.create_text(self.width//2, self.height//2,
                         text=self.text, fill=fg_color,
                         font=text_font, anchor="center")

    def _draw_rounded_rect(self, x1, y1, x2, y2, radius=10, **kwargs):
        """绘制圆角矩形"""
        points = []

        # 计算圆角点
        for x, y in [(x1, y1 + radius), (x1, y1), (x1 + radius, y1),
                     (x2 - radius, y1), (x2, y1), (x2, y1 + radius),
                     (x2, y2 - radius), (x2, y2), (x2 - radius, y2),
                     (x1 + radius, y2), (x1, y2), (x1, y2 - radius)]:
            points.extend([x, y])

        return self.create_polygon(points, smooth=True, **kwargs)

    def _on_click(self, event):
        """点击事件"""
        self.is_pressed = True
        self._draw()

    def _on_release(self, event):
        """释放事件"""
        self.is_pressed = False
        self._draw()
        if self.command:
            self.command()

    def _on_enter(self, event):
        """鼠标进入"""
        self.is_hovered = True
        self.configure(cursor="hand2")
        self._draw()

    def _on_leave(self, event):
        """鼠标离开"""
        self.is_hovered = False
        self.is_pressed = False
        self.configure(cursor="")
        self._draw()

    def configure_command(self, command):
        """设置命令"""
        self.command = command
