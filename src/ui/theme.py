"""
深色主题管理器
提供与Cursor Default Dark Modern主题一致的颜色配置
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any


class DarkThemeManager:
    """深色主题管理器"""

    # Cursor风格深色主题颜色配置 - 优化对比度
    COLORS = {
        'bg_primary': '#1e1e1e',      # 主背景
        'bg_secondary': '#2d2d30',    # 卡片背景
        'bg_tertiary': '#3e3e42',     # 三级背景
        'accent': '#007acc',          # 强调色（蓝色）
        'text_primary': '#ffffff',    # 主要文字 - 最高对比度
        'text_secondary': '#d4d4d4',  # 次要文字 - 提高对比度
        'border': '#464647',          # 边框
        'success': '#4ec9b0',         # 成功色
        'warning': '#ffcc02',         # 警告色
        'error': '#f44747',           # 错误色
        'hover': '#005a9e',           # 悬停色 - 提高对比度
        'active': '#1177bb',          # 激活色
    }

    # 字体配置
    FONTS = {
        'title': ('SF Pro Display', 18, 'bold'),
        'subtitle': ('SF Pro Display', 14, 'normal'),
        'body': ('SF Pro Text', 14, 'normal'),
        'button': ('SF Pro Text', 12, 'normal'),
        'small': ('SF Pro Text', 10, 'normal'),
    }

    # 尺寸配置 - 优化布局
    SIZES = {
        'window_width': 550,
        'window_height': 580,         # 进一步减少窗口高度到580
        'padding': 20,
        'spacing_v': 10,              # 进一步减少垂直间距
        'spacing_h': 12,
        'border_radius': 8,
        'button_radius': 6,
        'input_radius': 4,
    }

    @classmethod
    def get_color(cls, color_name: str) -> str:
        """获取颜色值"""
        return cls.COLORS.get(color_name, '#ffffff')

    @classmethod
    def get_font(cls, font_name: str) -> tuple:
        """获取字体配置"""
        return cls.FONTS.get(font_name, ('Arial', 12, 'normal'))

    @classmethod
    def get_size(cls, size_name: str) -> int:
        """获取尺寸配置"""
        return cls.SIZES.get(size_name, 0)

    @classmethod
    def apply_to_widget(cls, widget: tk.Widget, style_config: Dict[str, Any]) -> None:
        """将主题样式应用到组件"""
        try:
            for key, value in style_config.items():
                if hasattr(widget, 'configure'):
                    widget.configure(**{key: value})
        except Exception as e:
            print(f"应用主题样式失败: {e}")

    @classmethod
    def create_styled_button(cls, parent: tk.Widget, text: str,
                             command=None, style: str = 'primary') -> tk.Button:
        """创建样式化按钮"""
        style_configs = {
            'primary': {
                'bg': cls.COLORS['accent'],
                'fg': '#ffffff',
                'activebackground': cls.COLORS['active'],
                'activeforeground': '#ffffff',
            },
            'secondary': {
                'bg': cls.COLORS['bg_tertiary'],
                'fg': cls.COLORS['text_primary'],
                'activebackground': cls.COLORS['border'],
                'activeforeground': cls.COLORS['text_primary'],
            },
            'success': {
                'bg': cls.COLORS['success'],
                'fg': '#ffffff',
                'activebackground': '#3da58a',
                'activeforeground': '#ffffff',
            },
            'danger': {
                'bg': cls.COLORS['error'],
                'fg': '#ffffff',
                'activebackground': '#d73a49',
                'activeforeground': '#ffffff',
            }
        }

        config = style_configs.get(style, style_configs['primary'])

        button = tk.Button(
            parent,
            text=text,
            command=command,
            font=cls.FONTS['button'],
            relief=tk.FLAT,
            bd=0,
            cursor='hand2',
            **config
        )

        return button

    @classmethod
    def create_styled_frame(cls, parent: tk.Widget, style: str = 'primary') -> tk.Frame:
        """创建样式化框架"""
        bg_color = cls.COLORS['bg_secondary'] if style == 'secondary' else cls.COLORS['bg_primary']

        frame = tk.Frame(
            parent,
            bg=bg_color,
            relief=tk.FLAT,
            bd=0
        )

        return frame

    @classmethod
    def create_styled_label(cls, parent: tk.Widget, text: str,
                            style: str = 'body') -> tk.Label:
        """创建样式化标签"""
        font_config = cls.FONTS.get(style, cls.FONTS['body'])

        label = tk.Label(
            parent,
            text=text,
            font=font_config,
            bg=cls.COLORS['bg_primary'],
            fg=cls.COLORS['text_primary'],
            anchor='w'
        )

        return label

    @classmethod
    def create_styled_text(cls, parent: tk.Widget, **kwargs) -> tk.Text:
        """创建样式化文本框"""
        default_config = {
            'bg': cls.COLORS['bg_secondary'],
            'fg': cls.COLORS['text_primary'],
            'insertbackground': cls.COLORS['accent'],
            'selectbackground': cls.COLORS['accent'],
            'selectforeground': '#ffffff',
            'relief': tk.FLAT,
            'bd': 0,
            'font': cls.FONTS['body'],
            'wrap': tk.WORD,
            'highlightthickness': 0,
            'highlightcolor': cls.COLORS['bg_secondary'],
            'highlightbackground': cls.COLORS['bg_secondary'],
        }

        # 合并用户配置
        config = {**default_config, **kwargs}

        text_widget = tk.Text(parent, **config)

        return text_widget
