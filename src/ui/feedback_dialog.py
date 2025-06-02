"""
反馈收集对话框
采用深色主题和macOS风格设计
"""

import tkinter as tk
from tkinter import messagebox
from typing import Optional, Dict, Any

try:
    # 尝试相对导入
    from .theme import DarkThemeManager
    from .components import MacOSCard, MacOSTextArea, ImageGallery
    from .custom_button import CustomButton
    from ..core.feedback_collector import FeedbackCollector
    from ..core.image_handler import ImageHandler
    from ..utils.gui_utils import (
        validate_gui_environment,
        setup_macos_style,
        bind_escape_to_close,
        window_manager
    )
    from ..utils.i18n import get_text
except ImportError:
    # 回退到绝对导入
    from ui.theme import DarkThemeManager
    from ui.components import MacOSCard, MacOSTextArea, ImageGallery
    from ui.custom_button import CustomButton
    from core.feedback_collector import FeedbackCollector
    from core.image_handler import ImageHandler
    from utils.gui_utils import (
        validate_gui_environment,
        setup_macos_style,
        bind_escape_to_close,
        window_manager
    )
    from utils.i18n import get_text


class ModernFeedbackDialog:
    """反馈收集对话框"""

    def __init__(self, timeout_seconds: int = 600):
        self.timeout_seconds = timeout_seconds
        self.feedback_collector = FeedbackCollector(timeout_seconds)
        self.theme = DarkThemeManager

        # UI组件
        self.window: Optional[tk.Tk] = None
        self.text_area: Optional[MacOSTextArea] = None
        self.image_gallery: Optional[ImageGallery] = None

        # 状态
        self.result = None
        self.is_hidden = False
        self.timeout_job = None

        # 创建窗口（但不显示）
        self._create_window_once()

    def show_dialog(self) -> Optional[Dict[str, Any]]:
        """显示对话框并返回结果"""
        try:
            # 验证GUI环境
            is_valid, message = validate_gui_environment()
            if not is_valid:
                raise Exception(message)

            # 重置状态
            self._reset_dialog_state()

            # 显示窗口
            self._show_window()

            # 设置超时
            if self.timeout_seconds > 0:
                self.timeout_job = self.window.after(
                    self.timeout_seconds * 1000, self._on_timeout)

            # 运行主循环直到窗口被隐藏
            while not self.is_hidden and self.window.winfo_exists():
                try:
                    self.window.update()
                except tk.TclError:
                    break

            # 取消超时任务
            if self.timeout_job:
                self.window.after_cancel(self.timeout_job)
                self.timeout_job = None

            return self.result

        except Exception as e:
            error_msg = get_text('gui_error', str(e))
            print(error_msg)
            return {
                'success': False,
                'message': error_msg
            }

    def _create_window_once(self):
        """一次性创建窗口（不显示）"""
        if self.window is not None:
            return

        # 创建主窗口
        self.window = tk.Tk()
        self.window.title(get_text('window_title'))

        # 先隐藏窗口
        self.window.withdraw()

        # 设置窗口属性
        self.window.resizable(True, True)
        self.window.minsize(500, 550)

        # 设置主题
        theme = DarkThemeManager
        self.window.configure(bg=theme.get_color('bg_primary'))

        window_manager.register_window(self.window)

        # 设置macOS风格
        setup_macos_style(self.window)

        # 绑定关闭事件
        self.window.protocol("WM_DELETE_WINDOW", self._on_cancel)
        bind_escape_to_close(self.window, self._on_cancel)

        # 绑定快捷键 Command+Enter 提交反馈
        self.window.bind('<Command-Return>', lambda e: self._on_submit())
        self.window.bind('<Control-Return>',
                         lambda e: self._on_submit())  # 兼容其他系统

        # 创建主容器
        main_container = tk.Frame(
            self.window,
            bg=theme.get_color('bg_primary')
        )
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 创建界面
        self._create_ui(main_container)

        # 设置窗口大小和居中位置
        self._setup_window_geometry()

    def _setup_window_geometry(self):
        """设置窗口几何属性"""
        # 更新窗口以计算实际尺寸
        self.window.update_idletasks()

        # 设置窗口大小和居中位置
        window_width = 550
        window_height = 580
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)

        # 确保窗口不会超出屏幕边界
        x = max(0, min(x, screen_width - window_width))
        y = max(0, min(y, screen_height - window_height))

        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def _show_window(self):
        """显示窗口"""
        if self.window:
            self.is_hidden = False
            self.window.deiconify()
            self.window.lift()
            self.window.focus_force()

            # 确保窗口在前台
            self.window.attributes('-topmost', True)
            self.window.after(
                100, lambda: self.window.attributes('-topmost', False))

    def _hide_window(self):
        """隐藏窗口"""
        if self.window and not self.is_hidden:
            self.is_hidden = True
            self.window.withdraw()

    def _reset_dialog_state(self):
        """重置对话框状态"""
        self.result = None
        self.is_hidden = False

        # 重置反馈收集器
        self.feedback_collector.reset()

        # 重置UI状态
        if self.text_area:
            self.text_area.set_text("")

        if self.image_gallery:
            self.image_gallery.clear_images()

    def _create_ui(self, parent: tk.Widget):
        """创建用户界面"""
        # 创建主内容区域
        content_frame = self.theme.create_styled_frame(parent)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(
            0, self.theme.get_size('spacing_v')))

        # 文字反馈区域
        self._create_text_feedback_section(content_frame)

        # 图片反馈区域
        self._create_image_feedback_section(content_frame)

        # 操作按钮区域（固定在底部）
        self._create_action_buttons(parent)

        # 提示信息
        self._create_info_section(parent)

    def _create_text_feedback_section(self, parent: tk.Widget):
        """创建文字反馈区域"""
        # 文字反馈卡片
        text_card = MacOSCard(parent, get_text('text_feedback_title'))
        text_card.pack(fill=tk.X, pady=(
            0, self.theme.get_size('spacing_v')))

        # 文本输入区域 - 减少高度
        self.text_area = MacOSTextArea(
            text_card.content_frame,
            placeholder=get_text('text_placeholder'),
            height=5  # 减少高度到5行
        )
        self.text_area.pack(fill=tk.X, expand=False)

        # 为文本框绑定快捷键
        self.text_area.text_widget.bind(
            '<Command-Return>', lambda e: self._on_submit())
        self.text_area.text_widget.bind(
            '<Control-Return>', lambda e: self._on_submit())

    def _create_image_feedback_section(self, parent: tk.Widget):
        """创建图片反馈区域"""
        # 图片反馈卡片
        image_card = MacOSCard(parent, get_text('image_feedback_title'))
        image_card.pack(fill=tk.X, pady=(0, self.theme.get_size('spacing_v')))

        # 图片操作按钮
        button_frame = self.theme.create_styled_frame(image_card.content_frame)
        button_frame.pack(fill=tk.X, pady=(
            0, self.theme.get_size('spacing_h')))

        # 选择文件按钮
        select_btn = CustomButton(
            button_frame, get_text('select_image_button'), style='primary',
            command=self._select_images, width=100, height=32
        )
        select_btn.pack(side=tk.LEFT, padx=(
            0, self.theme.get_size('spacing_h')))

        # 粘贴按钮
        paste_btn = CustomButton(
            button_frame, get_text('paste_image_button'), style='secondary',
            command=self._paste_image, width=100, height=32
        )
        paste_btn.pack(side=tk.LEFT, padx=(
            0, self.theme.get_size('spacing_h')))

        # 清除按钮
        clear_btn = CustomButton(
            button_frame, get_text('clear_images_button'), style='danger',
            command=self._clear_images, width=100, height=32
        )
        clear_btn.pack(side=tk.LEFT)

        # 图片画廊
        self.image_gallery = ImageGallery(image_card.content_frame)
        self.image_gallery.pack(fill=tk.X, pady=(
            self.theme.get_size('spacing_h'), 0))

        # 设置图片移除回调
        self.image_gallery.on_image_remove = self._on_image_removed

    def _create_action_buttons(self, parent: tk.Widget):
        """创建操作按钮"""
        button_frame = self.theme.create_styled_frame(parent)
        button_frame.pack(fill=tk.X, pady=(
            self.theme.get_size('spacing_v'), 0))

        # 创建居中容器
        center_frame = self.theme.create_styled_frame(button_frame)
        center_frame.pack(expand=True)

        # 提交按钮
        submit_btn = CustomButton(
            center_frame, get_text('submit_button'), style='primary',
            command=self._on_submit, width=120, height=36
        )
        submit_btn.pack(side=tk.LEFT, padx=(
            0, self.theme.get_size('spacing_h')))

        # 取消按钮
        cancel_btn = CustomButton(
            center_frame, get_text('cancel_button'), style='secondary',
            command=self._on_cancel, width=120, height=36
        )
        cancel_btn.pack(side=tk.LEFT)

    def _create_info_section(self, parent: tk.Widget):
        """创建提示信息区域"""
        info_frame = self.theme.create_styled_frame(parent)
        info_frame.pack(fill=tk.X, pady=(
            self.theme.get_size('spacing_v'), 0))

        # 快捷键提示 - 居中对齐，小字体
        shortcut_label = self.theme.create_styled_label(
            info_frame, get_text('shortcut_info'), style='small'
        )
        shortcut_label.pack(anchor='center')  # 改为居中对齐

        # 超时提示 - 居中对齐，小字体
        if self.timeout_seconds > 0:
            timeout_minutes = self.timeout_seconds // 60
            timeout_label = self.theme.create_styled_label(
                info_frame, get_text('timeout_info', timeout_minutes), style='small'
            )
            timeout_label.pack(anchor='center')  # 改为居中对齐

    def _select_images(self):
        """选择图片文件"""
        try:
            images = self.feedback_collector.select_images()
            if images:
                for image_data in images:
                    self.image_gallery.add_image(image_data)
        except Exception as e:
            messagebox.showerror(get_text('confirm_title'), str(e))

    def _paste_image(self):
        """从剪贴板粘贴图片"""
        try:
            image_data = self.feedback_collector.paste_image_from_clipboard()
            if image_data:
                self.image_gallery.add_image(image_data)
            else:
                messagebox.showwarning(
                    get_text('confirm_title'), get_text('paste_failed'))
        except Exception as e:
            messagebox.showerror(get_text('confirm_title'), str(e))

    def _clear_images(self):
        """清除所有图片"""
        if self.image_gallery.get_images():
            if messagebox.askyesno(get_text('confirm_title'), get_text('confirm_clear_images')):
                self.image_gallery.clear_images()

    def _on_image_removed(self, index: int):
        """图片被移除时的回调"""
        # 图片已经在ImageGallery中被移除，这里不需要额外处理
        # 如果将来需要添加额外的处理逻辑（如日志记录、统计等），可以在此处添加
        pass

    def _on_submit(self):
        """提交反馈"""
        try:
            # 获取文字反馈
            text_feedback = self.text_area.get_text().strip()

            # 获取图片反馈
            images = self.image_gallery.get_images()

            # 检查是否有反馈内容
            if not text_feedback and not images:
                messagebox.showwarning(
                    get_text('confirm_title'), get_text('no_feedback_error'))
                return

            # 构建结果
            self.result = {
                'success': True,
                'has_text': bool(text_feedback),
                'text_feedback': text_feedback,
                'has_images': bool(images),
                'images': [img.get('data') for img in images],
                'message': get_text('submit_success')
            }

            # 隐藏对话框
            self._hide_window()

        except Exception as e:
            messagebox.showerror(get_text('confirm_title'), str(e))

    def _on_cancel(self):
        """取消操作"""
        try:
            # 检查是否有内容
            has_text = bool(
                self.text_area and self.text_area.get_text().strip())
            has_images = bool(
                self.image_gallery and self.image_gallery.get_images())

            if has_text or has_images:
                if not messagebox.askyesno(get_text('confirm_title'), get_text('confirm_cancel')):
                    return

            self.result = {
                'success': False,
                'message': get_text('operation_cancelled')
            }

            # 隐藏对话框
            self._hide_window()

        except Exception as e:
            print(f"[ERROR] _on_cancel 异常: {e}")

    def _on_timeout(self):
        """超时处理"""
        self.result = {
            'success': False,
            'message': get_text('timeout_error', self.timeout_seconds)
        }
        # 隐藏对话框
        self._hide_window()

    def destroy(self):
        """销毁对话框（仅在程序结束时调用）"""
        if self.window:
            try:
                # 取消超时任务
                if self.timeout_job:
                    self.window.after_cancel(self.timeout_job)
                    self.timeout_job = None

                # 注销窗口
                window_manager.unregister_window(self.window)

                # 销毁窗口
                self.window.destroy()
                self.window = None

            except Exception as e:
                print(f"销毁对话框时出错: {e}")


class SimpleImagePickerDialog:
    """简单的图片选择对话框"""

    def __init__(self):
        self.window = None
        self.result = None

    def show_dialog(self) -> Optional[bytes]:
        """显示对话框并返回选择的图片数据"""
        try:
            # 验证GUI环境
            is_valid, message = validate_gui_environment()
            if not is_valid:
                raise Exception(message)

            # 创建窗口
            self._create_window()

            # 运行主循环
            self.window.mainloop()

            return self.result

        except Exception as e:
            print(f"图片选择对话框错误: {e}")
            return None

    def _create_window(self):
        """创建窗口"""
        self.window = tk.Toplevel()
        self.window.title(get_text('image_picker_title'))
        self.window.geometry("400x200")
        self.window.resizable(False, False)

        # 设置窗口居中
        self.window.transient()
        self.window.grab_set()

        # 设置主题
        theme = DarkThemeManager
        self.window.configure(bg=theme.get_color('bg_primary'))

        # 绑定关闭事件
        self.window.protocol("WM_DELETE_WINDOW", self._on_cancel)

        # 创建界面
        self._create_ui()

        # 居中显示
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.window.winfo_screenheight() // 2) - (200 // 2)
        self.window.geometry(f"400x200+{x}+{y}")

    def _create_ui(self):
        """创建用户界面"""
        theme = DarkThemeManager

        # 主容器
        main_frame = theme.create_styled_frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 标题
        title_label = theme.create_styled_label(
            main_frame, get_text('image_picker_title'), style='title'
        )
        title_label.pack(pady=(0, 20))

        # 说明文字
        info_label = theme.create_styled_label(
            main_frame, get_text('image_picker_info'), style='body'
        )
        info_label.pack(pady=(0, 20))

        # 按钮区域
        button_frame = theme.create_styled_frame(main_frame)
        button_frame.pack(fill=tk.X)

        # 选择文件按钮
        select_btn = CustomButton(
            button_frame, get_text('select_file_button'), style='primary',
            command=self._select_file, width=150, height=36
        )
        select_btn.pack(side=tk.LEFT, padx=(0, 10))

        # 粘贴剪贴板按钮
        paste_btn = CustomButton(
            button_frame, get_text('paste_clipboard_button'), style='secondary',
            command=self._paste_clipboard, width=150, height=36
        )
        paste_btn.pack(side=tk.LEFT)

    def _select_file(self):
        """选择文件"""
        try:
            from tkinter import filedialog
            file_path = filedialog.askopenfilename(
                title=get_text('select_image_button'),
                filetypes=[
                    ("图片文件", "*.png *.jpg *.jpeg *.gif *.bmp"),
                    ("所有文件", "*.*")
                ]
            )
            if file_path:
                self.result = ImageHandler.load_image_as_bytes(file_path)
                self._close_window()
        except Exception as e:
            messagebox.showerror(get_text('confirm_title'), str(e))

    def _paste_clipboard(self):
        """粘贴剪贴板"""
        try:
            image_data = ImageHandler.get_clipboard_image()
            if image_data:
                self.result = image_data
                self._close_window()
            else:
                messagebox.showwarning(
                    get_text('confirm_title'), get_text('paste_failed'))
        except Exception as e:
            messagebox.showerror(get_text('confirm_title'), str(e))

    def _on_cancel(self):
        """取消操作"""
        self.result = None
        self._close_window()

    def _close_window(self):
        """关闭窗口"""
        if self.window:
            self.window.quit()
            self.window.destroy()
