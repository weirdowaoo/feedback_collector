"""
GUI工具函数
提供GUI环境验证、窗口管理等实用功能
"""

import tkinter as tk
import sys
import platform
from typing import Tuple, Optional, List

try:
    # 尝试相对导入
    from ..ui.theme import DarkThemeManager
except ImportError:
    # 回退到绝对导入
    from ui.theme import DarkThemeManager


def check_gui_available() -> bool:
    """检查GUI环境是否可用"""
    try:
        # 尝试创建一个测试窗口
        test_root = tk.Tk()
        test_root.withdraw()  # 隐藏窗口
        test_root.destroy()
        return True
    except Exception:
        return False


def get_system_info() -> dict:
    """获取系统信息"""
    return {
        'platform': platform.system(),
        'platform_version': platform.version(),
        'python_version': sys.version,
        'gui_available': check_gui_available()
    }


def is_macos() -> bool:
    """检查是否为macOS系统"""
    return platform.system() == 'Darwin'


def is_windows() -> bool:
    """检查是否为Windows系统"""
    return platform.system() == 'Windows'


def is_linux() -> bool:
    """检查是否为Linux系统"""
    return platform.system() == 'Linux'


def center_window(window: tk.Tk, width: int, height: int) -> None:
    """将窗口居中显示"""
    try:
        # 尝试使用tk的内置方法
        window.eval('tk::PlaceWindow . center')
    except:
        # 手动计算居中位置
        try:
            window.update_idletasks()
            screen_width = window.winfo_screenwidth()
            screen_height = window.winfo_screenheight()

            x = (screen_width // 2) - (width // 2)
            y = (screen_height // 2) - (height // 2)

            window.geometry(f"{width}x{height}+{x}+{y}")
        except Exception as e:
            print(f"窗口居中失败: {e}")


def setup_window_icon(window: tk.Tk, icon_path: Optional[str] = None) -> None:
    """设置窗口图标"""
    try:
        if icon_path:
            window.iconbitmap(icon_path)
        else:
            # 清除默认图标
            window.iconbitmap(default="")
    except Exception as e:
        print(f"设置窗口图标失败: {e}")


def bind_escape_to_close(window: tk.Tk, callback=None) -> None:
    """绑定ESC键关闭窗口"""
    def on_escape(event):
        if callback:
            callback()
        else:
            window.destroy()

    window.bind('<Escape>', on_escape)


def setup_window_properties(window: tk.Tk, title: str, width: int, height: int,
                            resizable: bool = True, topmost: bool = False) -> None:
    """设置窗口基本属性"""
    try:
        window.title(title)
        window.geometry(f"{width}x{height}")
        window.resizable(resizable, resizable)

        if topmost:
            window.attributes('-topmost', True)

        # 设置最小尺寸
        min_width = min(width, 400)
        min_height = min(height, 300)
        window.minsize(min_width, min_height)

        # 居中显示
        center_window(window, width, height)

    except Exception as e:
        print(f"设置窗口属性失败: {e}")


def create_tooltip(widget: tk.Widget, text: str) -> None:
    """为组件创建工具提示"""
    def on_enter(event):
        tooltip = tk.Toplevel()
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")

        label = tk.Label(
            tooltip,
            text=text,
            background="#ffffe0",
            relief=tk.SOLID,
            borderwidth=1,
            font=("Arial", 9)
        )
        label.pack()

        widget.tooltip = tooltip

    def on_leave(event):
        if hasattr(widget, 'tooltip'):
            widget.tooltip.destroy()
            del widget.tooltip

    widget.bind('<Enter>', on_enter)
    widget.bind('<Leave>', on_leave)


def safe_destroy(widget: tk.Widget) -> None:
    """安全销毁组件"""
    try:
        if widget and widget.winfo_exists():
            widget.destroy()
    except Exception as e:
        print(f"销毁组件失败: {e}")


def get_screen_size() -> tuple[int, int]:
    """获取屏幕尺寸"""
    try:
        root = tk.Tk()
        root.withdraw()
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        root.destroy()
        return width, height
    except Exception:
        return 1920, 1080  # 默认尺寸


def validate_gui_environment() -> Tuple[bool, str]:
    """验证GUI环境"""
    try:
        if not check_gui_available():
            return False, "GUI环境不可用，请确保在支持图形界面的环境中运行"

        # 检查显示器
        screen_width, screen_height = get_screen_size()
        if screen_width < 800 or screen_height < 600:
            return False, f"屏幕分辨率过低: {screen_width}x{screen_height}，建议至少800x600"

        return True, "GUI环境验证通过"

    except Exception as e:
        return False, f"GUI环境验证失败: {str(e)}"


def setup_macos_style(window: tk.Tk) -> None:
    """设置macOS风格"""
    if is_macos():
        try:
            # macOS特定设置
            window.tk.call('tk', 'scaling', 1.0)

            # 尝试设置原生外观
            try:
                window.tk.call('set', '::tk::mac::CGAntialiasLimit', 0)
            except:
                pass

        except Exception as e:
            print(f"设置macOS风格失败: {e}")


def handle_dpi_scaling(window: tk.Tk) -> float:
    """处理DPI缩放"""
    try:
        # 获取DPI缩放比例
        dpi = window.winfo_fpixels('1i')
        scale_factor = dpi / 72.0  # 72 DPI是标准

        if scale_factor > 1.0:
            # 调整字体大小
            window.option_add('*Font', f'Arial {int(12 * scale_factor)}')

        return scale_factor

    except Exception as e:
        print(f"处理DPI缩放失败: {e}")
        return 1.0


class WindowManager:
    """窗口管理器"""

    def __init__(self):
        self.windows = []

    def register_window(self, window: tk.Tk) -> None:
        """注册窗口"""
        self.windows.append(window)

    def unregister_window(self, window: tk.Tk) -> None:
        """注销窗口"""
        try:
            if window in self.windows:
                self.windows.remove(window)
        except ValueError:
            pass  # 窗口不在列表中，忽略

    def close_all_windows(self) -> None:
        """关闭所有窗口"""
        for window in self.windows:
            safe_destroy(window)
        self.windows.clear()

    def get_window_count(self) -> int:
        """获取窗口数量"""
        # 清理已销毁的窗口
        self.windows = [w for w in self.windows if w.winfo_exists()]
        return len(self.windows)


# 全局窗口管理器实例
window_manager = WindowManager()
