"""
macOS风格UI组件
提供深色主题界面组件
"""

import tkinter as tk
from PIL import Image, ImageTk
from typing import List, Callable, Optional, Any
from io import BytesIO

try:
    # 尝试相对导入
    from .theme import DarkThemeManager
    from ..core.image_handler import ImageHandler
    from ..utils.i18n import get_text
except ImportError:
    # 回退到绝对导入
    from ui.theme import DarkThemeManager
    from core.image_handler import ImageHandler
    from utils.i18n import get_text


class MacOSCard(tk.Frame):
    """macOS风格卡片组件"""

    def __init__(self, parent: tk.Widget, title: str = "", **kwargs):
        super().__init__(parent, **kwargs)

        self.theme = DarkThemeManager
        self.configure(
            bg=self.theme.get_color('bg_secondary'),
            relief=tk.FLAT,
            bd=1,
            highlightbackground=self.theme.get_color('border'),
            highlightthickness=1
        )

        if title:
            self.title_label = self.theme.create_styled_label(
                self, title, style='subtitle'
            )
            self.title_label.configure(bg=self.theme.get_color('bg_secondary'))
            self.title_label.pack(anchor='w', padx=16, pady=(16, 8))

        # 内容区域
        self.content_frame = self.theme.create_styled_frame(
            self, style='secondary')
        self.content_frame.pack(
            fill=tk.BOTH, expand=True, padx=16, pady=(0, 16))


class MacOSButton(tk.Button):
    """macOS风格按钮组件"""

    def __init__(self, parent: tk.Widget, text: str, style: str = 'primary',
                 icon: str = "", **kwargs):
        self.theme = DarkThemeManager

        # 处理图标
        display_text = f"{icon} {text}" if icon else text

        # 先初始化基本属性
        super().__init__(
            parent,
            text=display_text,
            font=self.theme.get_font('button'),
            relief=tk.FLAT,
            bd=0,
            cursor='hand2',
            highlightthickness=0,
            **kwargs
        )

        # 应用样式
        self._apply_style(style)

        # 设置悬停效果
        self._setup_hover_effects()

    def _apply_style(self, style: str):
        """应用按钮样式"""
        styles = {
            'primary': {
                'bg': self.theme.get_color('accent'),
                'fg': '#ffffff',
                'activebackground': self.theme.get_color('active'),
                'activeforeground': '#ffffff',
                'highlightbackground': self.theme.get_color('accent'),
                'disabledforeground': '#888888',
            },
            'secondary': {
                'bg': self.theme.get_color('bg_tertiary'),
                'fg': self.theme.get_color('text_primary'),
                'activebackground': self.theme.get_color('border'),
                'activeforeground': self.theme.get_color('text_primary'),
                'highlightbackground': self.theme.get_color('bg_tertiary'),
                'disabledforeground': '#888888',
            },
            'success': {
                'bg': self.theme.get_color('success'),
                'fg': '#ffffff',
                'activebackground': '#3da58a',
                'activeforeground': '#ffffff',
                'highlightbackground': self.theme.get_color('success'),
                'disabledforeground': '#888888',
            },
            'danger': {
                'bg': self.theme.get_color('error'),
                'fg': '#ffffff',
                'activebackground': '#d73a49',
                'activeforeground': '#ffffff',
                'highlightbackground': self.theme.get_color('error'),
                'disabledforeground': '#888888',
            }
        }

        config = styles.get(style, styles['primary'])

        # 强制设置样式，覆盖系统默认
        self.configure(**config)

    def _setup_hover_effects(self):
        """设置悬停效果"""
        original_bg = self['bg']

        # 根据按钮样式设置不同的悬停颜色
        if original_bg == self.theme.get_color('accent'):  # primary按钮
            hover_bg = self.theme.get_color('active')
        elif original_bg == self.theme.get_color('success'):  # success按钮
            hover_bg = '#3da58a'
        elif original_bg == self.theme.get_color('error'):  # danger按钮
            hover_bg = '#d73a49'
        else:  # secondary按钮
            hover_bg = self.theme.get_color('border')

        def on_enter(event):
            self.configure(bg=hover_bg)

        def on_leave(event):
            self.configure(bg=original_bg)

        self.bind('<Enter>', on_enter)
        self.bind('<Leave>', on_leave)


class MacOSTextArea(tk.Frame):
    """macOS风格文本输入区域"""

    def __init__(self, parent: tk.Widget, placeholder: str = "", height: int = 6, **kwargs):
        super().__init__(parent, **kwargs)

        self.theme = DarkThemeManager
        self.placeholder = placeholder
        self.has_placeholder = True

        self.configure(
            bg=self.theme.get_color('bg_secondary'),
            highlightthickness=0,
            bd=0
        )

        # 创建文本框 - 使用更彻底的方法移除高亮
        self.text_widget = tk.Text(
            self,
            height=height,
            bg=self.theme.get_color('bg_secondary'),
            fg=self.theme.get_color('text_primary'),
            insertbackground=self.theme.get_color('accent'),
            selectbackground=self.theme.get_color('accent'),
            selectforeground='#ffffff',
            font=self.theme.get_font('body'),
            wrap=tk.WORD,
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0,
            highlightcolor=self.theme.get_color('bg_secondary'),
            highlightbackground=self.theme.get_color('bg_secondary'),
            borderwidth=0
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True)

        # 设置占位符
        if placeholder:
            self._set_placeholder()
            self.text_widget.bind('<FocusIn>', self._on_focus_in)
            self.text_widget.bind('<FocusOut>', self._on_focus_out)

    def _set_placeholder(self):
        """设置占位符文本"""
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(1.0, self.placeholder)
        self.text_widget.configure(fg=self.theme.get_color('text_secondary'))
        self.has_placeholder = True

    def _on_focus_in(self, event):
        """获得焦点时清除占位符"""
        if self.has_placeholder:
            self.text_widget.delete(1.0, tk.END)
            self.text_widget.configure(fg=self.theme.get_color('text_primary'))
            self.has_placeholder = False

    def _on_focus_out(self, event):
        """失去焦点时恢复占位符"""
        if not self.text_widget.get(1.0, tk.END).strip():
            self._set_placeholder()

    def get_text(self) -> str:
        """获取文本内容"""
        if self.has_placeholder:
            return ""
        return self.text_widget.get(1.0, tk.END).strip()

    def set_text(self, text: str):
        """设置文本内容"""
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(1.0, text)
        self.text_widget.configure(fg=self.theme.get_color('text_primary'))
        self.has_placeholder = False


class ImagePreviewCard(tk.Frame):
    """图片预览卡片组件"""

    def __init__(self, parent: tk.Widget, image_data: dict,
                 on_remove: Optional[Callable] = None, **kwargs):
        super().__init__(parent, **kwargs)

        self.theme = DarkThemeManager
        self.image_data = image_data
        self.on_remove = on_remove

        self.configure(
            bg=self.theme.get_color('bg_secondary'),
            relief=tk.FLAT,
            bd=1,
            highlightbackground=self.theme.get_color('border'),
            highlightthickness=1
        )

        # 创建主容器
        self.main_container = tk.Frame(
            self,
            bg=self.theme.get_color('bg_secondary')
        )
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        self._create_preview()

    def _create_preview(self):
        """创建图片预览"""
        try:
            # 获取图片对象
            img = None
            if 'image' in self.image_data and self.image_data['image'] is not None:
                # 直接使用PIL图片对象
                img = self.image_data['image']
            elif 'data' in self.image_data and self.image_data['data'] is not None:
                # 从字节数据创建图片对象
                img = Image.open(BytesIO(self.image_data['data']))
            else:
                raise ValueError("图片数据格式不正确")

            # 创建缩略图
            img_copy = img.copy()
            img_copy.thumbnail((120, 100), Image.Resampling.LANCZOS)

            # 转换为tkinter格式
            self.photo = ImageTk.PhotoImage(img_copy)

            # 创建图片容器（用于放置悬浮按钮）
            self.image_container = tk.Frame(
                self.main_container,
                bg=self.theme.get_color('bg_secondary')
            )
            self.image_container.pack()

            # 图片标签
            self.img_label = tk.Label(
                self.image_container,
                image=self.photo,
                bg=self.theme.get_color('bg_secondary'),
                cursor='hand2'
            )
            self.img_label.pack()

            # 创建悬浮删除按钮（初始隐藏）
            if self.on_remove:
                self.delete_btn = tk.Label(
                    self.image_container,
                    text="×",
                    font=('Arial', 16, 'bold'),
                    bg='#ff4444',
                    fg='white',
                    width=3,
                    height=1,
                    cursor='hand2',
                    relief=tk.FLAT
                )

                # 绑定点击事件
                self.delete_btn.bind('<Button-1>', lambda e: self.on_remove())

                # 初始隐藏删除按钮
                self.delete_btn.place_forget()

            # 绑定鼠标悬浮事件
            self._bind_hover_events()

        except Exception as e:
            # 错误显示
            error_label = self.theme.create_styled_label(
                self.main_container, f"{get_text('image_preview_failed')}\n{str(e)}", style='small'
            )
            error_label.configure(
                bg=self.theme.get_color('bg_secondary'),
                fg=self.theme.get_color('error'),
                justify=tk.CENTER
            )
            error_label.pack(padx=8, pady=8)
            print(f"图片预览失败: {e}")  # 添加调试信息

    def _bind_hover_events(self):
        """绑定鼠标悬浮事件"""
        if not hasattr(self, 'delete_btn'):
            return

        def on_enter(event):
            # 计算删除按钮的居中位置
            img_width = self.img_label.winfo_width()
            img_height = self.img_label.winfo_height()

            if img_width > 1 and img_height > 1:  # 确保组件已经渲染
                btn_x = (img_width - 30) // 2  # 按钮宽度约30
                btn_y = (img_height - 20) // 2  # 按钮高度约20

                self.delete_btn.place(x=btn_x, y=btn_y)

        def on_leave(event):
            # 检查鼠标是否真的离开了整个图片区域
            x, y = event.x_root, event.y_root
            widget_x = self.image_container.winfo_rootx()
            widget_y = self.image_container.winfo_rooty()
            widget_width = self.image_container.winfo_width()
            widget_height = self.image_container.winfo_height()

            # 如果鼠标不在图片容器范围内，隐藏删除按钮
            if not (widget_x <= x <= widget_x + widget_width and
                    widget_y <= y <= widget_y + widget_height):
                self.delete_btn.place_forget()

        # 为图片容器和图片标签绑定事件
        self.image_container.bind('<Enter>', on_enter)
        self.image_container.bind('<Leave>', on_leave)
        self.img_label.bind('<Enter>', on_enter)
        self.img_label.bind('<Leave>', on_leave)

        # 为删除按钮也绑定事件，防止按钮消失
        if hasattr(self, 'delete_btn'):
            self.delete_btn.bind('<Enter>', on_enter)
            self.delete_btn.bind('<Leave>', on_leave)


class ImageGallery(tk.Frame):
    """图片画廊组件"""

    def __init__(self, parent: tk.Widget, **kwargs):
        super().__init__(parent, **kwargs)

        self.theme = DarkThemeManager
        self.images = []
        self.on_image_remove = None

        self.configure(bg=self.theme.get_color('bg_primary'))

        # 创建滚动画布 - 进一步减少高度
        self.canvas = tk.Canvas(
            self,
            height=135,  # 进一步减少高度到120像素
            bg=self.theme.get_color('bg_secondary'),
            highlightbackground=self.theme.get_color('border'),
            highlightthickness=1
        )

        # 只创建水平滚动条
        self.scrollbar = tk.Scrollbar(
            self, orient="horizontal", command=self.canvas.xview,
            bg=self.theme.get_color('bg_secondary'),
            troughcolor=self.theme.get_color('bg_primary'),
            activebackground=self.theme.get_color('accent')
        )

        self.gallery_frame = tk.Frame(
            self.canvas,
            bg=self.theme.get_color('bg_secondary')
        )

        # 配置滚动
        self.gallery_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window(
            (0, 0), window=self.gallery_frame, anchor="nw"
        )
        self.canvas.configure(xscrollcommand=self.scrollbar.set)

        # 布局组件
        self.canvas.pack(side="top", fill="x")
        self.scrollbar.pack(side="bottom", fill="x")

        # 绑定鼠标滚轮事件（水平滚动）
        def _on_mousewheel(event):
            self.canvas.xview_scroll(int(-1*(event.delta/120)), "units")

        self.canvas.bind("<MouseWheel>", _on_mousewheel)  # Windows
        self.canvas.bind(
            "<Button-4>", lambda e: self.canvas.xview_scroll(-1, "units"))  # Linux
        self.canvas.bind(
            "<Button-5>", lambda e: self.canvas.xview_scroll(1, "units"))   # Linux

        # 初始显示
        self._update_display()

    def add_image(self, image_data: dict):
        """添加图片"""
        self.images.append(image_data)
        self._update_display()

    def remove_image(self, index: int):
        """移除图片"""
        if 0 <= index < len(self.images):
            self.images.pop(index)
            self._update_display()
            if self.on_image_remove:
                self.on_image_remove(index)

    def clear_images(self):
        """清空所有图片"""
        self.images.clear()
        self._update_display()

    def get_images(self) -> List[dict]:
        """获取所有图片数据"""
        return self.images.copy()

    def _update_display(self):
        """更新显示"""
        # 清除现有组件
        for widget in self.gallery_frame.winfo_children():
            widget.destroy()

        if not self.images:
            # 显示空状态
            empty_label = self.theme.create_styled_label(
                self.gallery_frame, get_text('no_images_selected'), style='small'
            )
            empty_label.configure(
                bg=self.theme.get_color('bg_secondary'),
                fg=self.theme.get_color('text_secondary')
            )
            empty_label.pack(pady=50)  # 调整垂直居中的间距

            # 隐藏滚动条
            self.scrollbar.pack_forget()
        else:
            # 水平排列图片
            for i, img_data in enumerate(self.images):
                preview_card = ImagePreviewCard(
                    self.gallery_frame,
                    img_data,
                    on_remove=lambda idx=i: self.remove_image(idx)
                )
                preview_card.pack(side=tk.LEFT, padx=8, pady=8)

            # 更新滚动区域
            self.gallery_frame.update_idletasks()
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

            # 检查是否需要滚动条
            self._check_scrollbar_needed()

    def _check_scrollbar_needed(self):
        """检查是否需要显示滚动条"""
        try:
            # 等待布局完成
            self.update_idletasks()

            # 获取内容宽度和画布宽度
            canvas_width = self.canvas.winfo_width()
            content_width = self.gallery_frame.winfo_reqwidth()

            # 只有当内容宽度超过画布宽度时才显示滚动条
            if content_width > canvas_width:
                self.scrollbar.pack(side="bottom", fill="x")
            else:
                self.scrollbar.pack_forget()

        except Exception as e:
            # 如果出错，默认显示滚动条
            self.scrollbar.pack(side="bottom", fill="x")


class MacOSWindow(tk.Tk):
    """macOS风格主窗口"""

    def __init__(self, title: str = "", **kwargs):
        super().__init__(**kwargs)

        # 设置窗口标题
        if not title:
            title = get_text('window_title')
        self.title(title)

        # 先隐藏窗口，避免闪烁
        self.withdraw()

        # 设置主题
        self.theme = DarkThemeManager
        self.configure(bg=self.theme.get_color('bg_primary'))

        # 设置窗口属性
        self.resizable(True, True)
        self.minsize(500, 550)  # 调整最小尺寸

        # 计算居中位置并设置窗口大小和位置
        self._center_window()

        # 显示窗口
        self.deiconify()

        # 设置窗口图标（如果有的话）
        try:
            # 这里可以设置窗口图标
            pass
        except Exception:
            pass

    def _center_window(self):
        """将窗口居中显示"""
        # 获取窗口尺寸
        window_width = 550
        window_height = 580  # 减少高度

        # 获取屏幕尺寸
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # 计算居中位置
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)

        # 确保窗口不会超出屏幕边界
        x = max(0, min(x, screen_width - window_width))
        y = max(0, min(y, screen_height - window_height))

        # 设置窗口位置和大小
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def create_main_container(self) -> tk.Frame:
        """创建主容器"""
        container = self.theme.create_styled_frame(self)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        return container
