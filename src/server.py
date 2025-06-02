"""
MCP 反馈收集器服务器
"""

from mcp.types import TextContent
from mcp.server.fastmcp.utilities.types import Image as MCPImage
from mcp.server.fastmcp import FastMCP
import os
import sys
import atexit
from typing import List

# 设置Python IO编码为UTF-8，确保中文字符正确处理
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')

# 处理模块导入路径
if __name__ == "__main__":
    # 当作为模块运行时 (python -m src.server)
    # 添加src目录到Python路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
else:
    # 当作为包的一部分导入时
    pass


try:
    # 尝试相对导入（当作为包的一部分时）
    from .ui.feedback_dialog import ModernFeedbackDialog, SimpleImagePickerDialog
    from .core.image_handler import ImageHandler
    from .utils.gui_utils import validate_gui_environment
    from .utils.i18n import get_text
except ImportError:
    # 回退到绝对导入（当作为模块运行时）
    from ui.feedback_dialog import ModernFeedbackDialog, SimpleImagePickerDialog
    from core.image_handler import ImageHandler
    from utils.gui_utils import validate_gui_environment
    from utils.i18n import get_text

# 创建MCP服务器 - 使用旧版本API
mcp = FastMCP(
    "反馈收集器",
    dependencies=["pillow", "tkinter"]
)

# 配置超时时间（秒）
# 优先使用环境变量配置，如果没有则使用默认值600秒（10分钟）
DEFAULT_DIALOG_TIMEOUT = 600  # 10分钟
DIALOG_TIMEOUT = int(os.getenv("MCP_DIALOG_TIMEOUT", DEFAULT_DIALOG_TIMEOUT))

# 全局对话框实例（重用窗口）
_feedback_dialog = None
_image_picker_dialog = None


def _get_feedback_dialog():
    """获取或创建反馈对话框实例"""
    global _feedback_dialog
    if _feedback_dialog is None:
        _feedback_dialog = ModernFeedbackDialog(DIALOG_TIMEOUT)
    return _feedback_dialog


def _get_image_picker_dialog():
    """获取或创建图片选择对话框实例"""
    global _image_picker_dialog
    if _image_picker_dialog is None:
        _image_picker_dialog = SimpleImagePickerDialog()
    return _image_picker_dialog


def _cleanup_dialogs():
    """清理对话框资源"""
    global _feedback_dialog, _image_picker_dialog

    try:
        if _feedback_dialog:
            _feedback_dialog.destroy()
            _feedback_dialog = None
    except Exception as e:
        print(f"[ERROR] 清理反馈对话框失败: {e}", file=sys.stderr)

    try:
        if _image_picker_dialog:
            # SimpleImagePickerDialog 不需要特殊清理
            _image_picker_dialog = None
    except Exception as e:
        print(f"[ERROR] 清理图片选择对话框失败: {e}", file=sys.stderr)


# 注册程序退出时的清理函数
atexit.register(_cleanup_dialogs)


@mcp.tool()
def collect_feedback() -> List:
    """
    收集用户反馈的交互式工具。
    显示反馈收集界面，用户可以提供文字和/或图片反馈。

    Returns:
        包含用户反馈内容的列表，可能包含文本和图片
    """
    try:
        print(
            f"[DEBUG] {get_text('debug_collecting_feedback', DIALOG_TIMEOUT)}", file=sys.stderr)

        # 验证GUI环境
        is_valid, message = validate_gui_environment()
        if not is_valid:
            print(
                f"[ERROR] {get_text('env_validation_failed', message)}", file=sys.stderr)
            raise Exception(message)

        print(f"[DEBUG] {get_text('debug_gui_validated')}", file=sys.stderr)

        # 获取对话框实例（重用窗口）
        dialog = _get_feedback_dialog()

        # 使用配置文件中的超时时间
        dialog.timeout_seconds = DIALOG_TIMEOUT

        # 显示对话框
        result = dialog.show_dialog()

        if result is None:
            print(
                f"[ERROR] {get_text('timeout_error', DIALOG_TIMEOUT)}", file=sys.stderr)
            raise Exception(get_text('timeout_error', DIALOG_TIMEOUT))

        if not result['success']:
            print(
                f"[ERROR] {get_text('feedback_submit_failed', result.get('message', '未知错误'))}", file=sys.stderr)
            raise Exception(result.get(
                'message', get_text('feedback_cancelled')))

        print(f"[DEBUG] {get_text('debug_feedback_success')}", file=sys.stderr)

        # 构建返回内容列表
        feedback_items = []

        # 添加文字反馈
        if result['has_text']:
            feedback_items.append(TextContent(
                type="text",
                text=get_text('user_text_feedback', result['text_feedback'])
            ))

        # 添加图片反馈
        if result['has_images']:
            for i, image_data in enumerate(result['images']):
                if image_data:
                    feedback_items.append(
                        MCPImage(data=image_data, format='png'))

        print(
            f"[DEBUG] {get_text('debug_feedback_items', len(feedback_items))}", file=sys.stderr)
        return feedback_items

    except Exception as e:
        # 确保异常不会导致MCP服务器崩溃
        error_msg = str(e)
        print(
            f"[ERROR] {get_text('collect_feedback_error', error_msg)}", file=sys.stderr)
        raise Exception(get_text('feedback_collection_failed', error_msg))


def main():
    """主入口函数"""
    try:
        print(get_text('server_starting'), file=sys.stderr)

        # 验证环境
        is_valid, message = validate_gui_environment()
        if not is_valid:
            print(get_text('env_validation_failed', message), file=sys.stderr)
            sys.exit(1)

        print(get_text('env_validation_passed'), file=sys.stderr)

        # 启动服务器 - 使用旧版本API
        mcp.run()

    except KeyboardInterrupt:
        print(f"\n{get_text('server_stopped')}", file=sys.stderr)
        # 清理资源
        _cleanup_dialogs()
    except Exception as e:
        print(get_text('server_start_failed', e), file=sys.stderr)
        import traceback
        traceback.print_exc()
        # 清理资源
        _cleanup_dialogs()
        sys.exit(1)


if __name__ == "__main__":
    main()
