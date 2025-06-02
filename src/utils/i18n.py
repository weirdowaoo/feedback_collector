"""
国际化支持模块
支持中英文切换，通过环境变量LANGUAGE控制
"""

import os
import sys
from typing import Dict, Any

# 默认语言
DEFAULT_LANGUAGE = 'CN'

# 当前语言设置
CURRENT_LANGUAGE = os.getenv('LANGUAGE', DEFAULT_LANGUAGE).upper()

# 语言包
TRANSLATIONS = {
    'CN': {
        # 窗口标题
        'window_title': '💬 反馈收集器',
        'image_picker_title': '🖼️ 选择图片',

        # 卡片标题
        'text_feedback_title': '📝 文字反馈',
        'image_feedback_title': '🖼️ 图片反馈',

        # 按钮文本
        'submit_button': '提交反馈',
        'cancel_button': '取消',
        'select_image_button': '选择图片',
        'paste_image_button': '粘贴图片',
        'clear_images_button': '清除图片',
        'select_file_button': '选择文件',
        'paste_clipboard_button': '粘贴剪贴板',

        # 占位符文本
        'text_placeholder': '请在此输入您的反馈、建议或问题...',

        # 提示信息
        'shortcut_info': '⌨️ 快捷键：⌘+Enter（Ctrl+Enter）提交反馈，ESC 取消',
        'timeout_info': '⏰ 对话框将在 {} 分钟后自动关闭',
        'image_picker_info': '选择图片文件或从剪贴板粘贴图片',

        # 错误和状态消息
        'no_feedback_error': '请输入文字反馈或添加图片',
        'submit_success': '反馈提交成功！',
        'operation_cancelled': '操作已取消',
        'timeout_error': '操作超时（{}秒），请重试',
        'gui_error': '创建反馈对话框失败: {}',
        'image_select_cancelled': '未选择图片或操作被取消',
        'image_select_failed': '图片选择失败: {}',
        'image_info_failed': '获取图片信息失败: {}',
        'paste_failed': '粘贴失败，剪贴板中没有图片数据',
        'file_not_found': '文件不存在: {}',
        'invalid_image': '无效的图片文件: {}',

        # 确认对话框
        'confirm_title': '确认',
        'confirm_cancel': '确定要取消吗？已输入的内容将丢失。',
        'confirm_clear_images': '确定要清除所有图片吗？',

        # 服务器消息
        'server_starting': '启动MCP反馈收集器服务器...',
        'server_stopped': '服务器已停止',
        'server_start_failed': '服务器启动失败: {}',
        'env_validation_failed': '环境验证失败: {}',
        'env_validation_passed': '环境验证通过，服务器启动中...',
        'feedback_submit_failed': '反馈提交失败: {}',
        'feedback_cancelled': '用户取消了反馈提交',
        'collect_feedback_error': 'collect_feedback错误: {}',
        'feedback_collection_failed': '反馈收集失败: {}',
        'pick_image_error': 'pick_image错误: {}',
        'user_text_feedback': '用户文字反馈：{}',

        # 调试信息
        'debug_collecting_feedback': '开始收集反馈，超时时间: {}秒',
        'debug_gui_validated': 'GUI环境验证通过',
        'debug_feedback_success': '反馈收集成功',
        'debug_feedback_items': '返回 {} 个反馈项',
        'debug_selecting_image': '开始选择图片',
        'debug_image_success': '图片选择成功',
        'debug_getting_image_info': '获取图片信息: {}',
        'debug_image_info_success': '图片信息获取成功',

        # 图片相关
        'image_remove_tooltip': '点击删除图片',
        'image_preview': '图片预览',
        'images_count': '已添加 {} 张图片',
        'image_preview_failed': '预览失败',
        'no_images_selected': '未选择图片',
    },

    'EN': {
        # Window titles
        'window_title': '💬 Feedback Collector',
        'image_picker_title': '🖼️ Select Image',

        # Card titles
        'text_feedback_title': '📝 Text Feedback',
        'image_feedback_title': '🖼️ Image Feedback',

        # Button text
        'submit_button': 'Submit Feedback',
        'cancel_button': 'Cancel',
        'select_image_button': 'Select Image',
        'paste_image_button': 'Paste Image',
        'clear_images_button': 'Clear Images',
        'select_file_button': 'Select File',
        'paste_clipboard_button': 'Paste Clipboard',

        # Placeholder text
        'text_placeholder': 'Please enter your feedback, suggestions or questions here...',

        # Info messages
        'shortcut_info': '⌨️ Shortcuts: ⌘+Enter (Ctrl+Enter) to submit, ESC to cancel',
        'timeout_info': '⏰ Dialog will close automatically in {} minutes',
        'image_picker_info': 'Select image file or paste from clipboard',

        # Error and status messages
        'no_feedback_error': 'Please enter text feedback or add images',
        'submit_success': 'Feedback submitted successfully!',
        'operation_cancelled': 'Operation cancelled',
        'timeout_error': 'Operation timeout ({}s), please try again',
        'gui_error': 'Failed to create feedback dialog: {}',
        'image_select_cancelled': 'No image selected or operation cancelled',
        'image_select_failed': 'Image selection failed: {}',
        'image_info_failed': 'Failed to get image info: {}',
        'paste_failed': 'Paste failed, no image data in clipboard',
        'file_not_found': 'File not found: {}',
        'invalid_image': 'Invalid image file: {}',

        # Confirmation dialogs
        'confirm_title': 'Confirm',
        'confirm_cancel': 'Are you sure you want to cancel? All entered content will be lost.',
        'confirm_clear_images': 'Are you sure you want to clear all images?',

        # Server messages
        'server_starting': 'Starting MCP Feedback Collector Server...',
        'server_stopped': 'Server stopped',
        'server_start_failed': 'Server startup failed: {}',
        'env_validation_failed': 'Environment validation failed: {}',
        'env_validation_passed': 'Environment validation passed, starting server...',
        'feedback_submit_failed': 'Feedback submission failed: {}',
        'feedback_cancelled': 'User cancelled feedback submission',
        'collect_feedback_error': 'collect_feedback error: {}',
        'feedback_collection_failed': 'Feedback collection failed: {}',
        'pick_image_error': 'pick_image error: {}',
        'user_text_feedback': 'User text feedback: {}',

        # Debug info
        'debug_collecting_feedback': 'Starting feedback collection, timeout: {}s',
        'debug_gui_validated': 'GUI environment validation passed',
        'debug_feedback_success': 'Feedback collection successful',
        'debug_feedback_items': 'Returning {} feedback items',
        'debug_selecting_image': 'Starting image selection',
        'debug_image_success': 'Image selection successful',
        'debug_getting_image_info': 'Getting image info: {}',
        'debug_image_info_success': 'Image info retrieval successful',

        # Image related
        'image_remove_tooltip': 'Click to remove image',
        'image_preview': 'Image Preview',
        'images_count': '{} images added',
        'image_preview_failed': 'Preview failed',
        'no_images_selected': 'No images selected',
    }
}


def get_text(key: str, *args) -> str:
    """
    获取指定键的本地化文本

    Args:
        key: 文本键
        *args: 格式化参数

    Returns:
        本地化后的文本
    """
    # 获取当前语言的翻译
    current_translations = TRANSLATIONS.get(
        CURRENT_LANGUAGE, TRANSLATIONS[DEFAULT_LANGUAGE])

    # 获取文本，如果不存在则使用默认语言
    text = current_translations.get(key)
    if text is None:
        text = TRANSLATIONS[DEFAULT_LANGUAGE].get(key, key)

    # 格式化文本
    if args:
        try:
            return text.format(*args)
        except (IndexError, ValueError):
            return text

    return text


def set_language(language: str):
    """
    设置当前语言

    Args:
        language: 语言代码 ('CN' 或 'EN')
    """
    global CURRENT_LANGUAGE
    language = language.upper()
    if language in TRANSLATIONS:
        CURRENT_LANGUAGE = language
        # 同时更新环境变量
        os.environ['LANGUAGE'] = language


def get_current_language() -> str:
    """获取当前语言"""
    return CURRENT_LANGUAGE


def get_available_languages() -> list:
    """获取可用的语言列表"""
    return list(TRANSLATIONS.keys())


# 初始化时打印当前语言设置
if __name__ != "__main__":
    print(f"[I18N] Current language: {CURRENT_LANGUAGE}", file=sys.stderr)
