"""
反馈收集器核心模块
处理反馈数据的收集、验证和提交
"""

from typing import Dict, List, Any, Optional, Tuple
import threading
import queue

try:
    # 尝试相对导入
    from .image_handler import ImageHandler
    from ..utils.i18n import get_text
except ImportError:
    # 回退到绝对导入
    from core.image_handler import ImageHandler
    from utils.i18n import get_text


class FeedbackData:
    """反馈数据模型"""

    def __init__(self):
        self.text_feedback: Optional[str] = None
        self.images: List[Dict[str, Any]] = []
        self.has_text: bool = False
        self.has_images: bool = False

    def add_text_feedback(self, text: str):
        """添加文字反馈"""
        if text and text.strip():
            self.text_feedback = text.strip()
            self.has_text = True

    def add_image(self, image_data: Dict[str, Any]):
        """添加图片"""
        if image_data:
            self.images.append(image_data)
            self.has_images = True

    def remove_image(self, index: int):
        """移除图片"""
        if 0 <= index < len(self.images):
            self.images.pop(index)
            self.has_images = len(self.images) > 0

    def clear_images(self):
        """清空所有图片"""
        self.images.clear()
        self.has_images = False

    def is_valid(self) -> bool:
        """检查反馈数据是否有效"""
        return self.has_text or self.has_images

    def get_image_count(self) -> int:
        """获取图片数量"""
        return len(self.images)

    def get_image_sources(self) -> List[str]:
        """获取图片来源列表"""
        return [img.get('source', '未知来源') for img in self.images]

    def get_image_data_list(self) -> List[bytes]:
        """获取图片数据列表"""
        return [img.get('data') for img in self.images if img.get('data')]

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'success': True,
            'text_feedback': self.text_feedback,
            'images': self.get_image_data_list(),
            'image_sources': self.get_image_sources(),
            'has_text': self.has_text,
            'has_images': self.has_images,
            'image_count': self.get_image_count()
        }


class FeedbackCollector:
    """反馈收集器"""

    def __init__(self, timeout_seconds: int = 300):
        self.timeout_seconds = timeout_seconds
        self.feedback_data = FeedbackData()
        self.result_queue = queue.Queue()
        self.is_cancelled = False
        self.is_submitted = False

    def reset(self):
        """重置收集器状态"""
        self.feedback_data = FeedbackData()
        self.is_cancelled = False
        self.is_submitted = False

        # 清空队列
        while not self.result_queue.empty():
            try:
                self.result_queue.get_nowait()
            except queue.Empty:
                break

    def select_images(self) -> List[Dict[str, Any]]:
        """选择图片文件"""
        try:
            images = ImageHandler.select_files_dialog()
            return images

        except Exception as e:
            print(f"选择图片失败: {e}")
            return []

    def paste_image_from_clipboard(self) -> Optional[Dict[str, Any]]:
        """从剪贴板粘贴图片"""
        try:
            image_data = ImageHandler.load_from_clipboard()
            return image_data

        except Exception as e:
            print(f"从剪贴板粘贴图片失败: {e}")
            return None

    def add_text_feedback(self, text: str) -> bool:
        """添加文字反馈"""
        try:
            self.feedback_data.add_text_feedback(text)
            return True
        except Exception as e:
            print(f"添加文字反馈失败: {e}")
            return False

    def add_image(self, image_data: Dict[str, Any]) -> bool:
        """添加图片"""
        try:
            self.feedback_data.add_image(image_data)
            return True
        except Exception as e:
            print(f"添加图片失败: {e}")
            return False

    def remove_image(self, index: int) -> bool:
        """移除图片"""
        try:
            self.feedback_data.remove_image(index)
            return True
        except Exception as e:
            print(f"移除图片失败: {e}")
            return False

    def clear_images(self) -> bool:
        """清空所有图片"""
        try:
            self.feedback_data.clear_images()
            return True
        except Exception as e:
            print(f"清空图片失败: {e}")
            return False

    def get_feedback_data(self) -> FeedbackData:
        """获取反馈数据"""
        return self.feedback_data

    def submit_feedback(self) -> Dict[str, Any]:
        """提交反馈"""
        try:
            if not self.feedback_data.is_valid():
                return {
                    'success': False,
                    'message': get_text('no_feedback_error')
                }

            self.is_submitted = True
            result = self.feedback_data.to_dict()
            self.result_queue.put(result)
            return result

        except Exception as e:
            error_result = {
                'success': False,
                'message': f'提交反馈失败: {str(e)}'
            }
            self.result_queue.put(error_result)
            return error_result

    def cancel_feedback(self) -> Dict[str, Any]:
        """取消反馈"""
        try:
            self.is_cancelled = True
            result = {
                'success': False,
                'message': get_text('operation_cancelled')
            }
            self.result_queue.put(result)
            return result

        except Exception as e:
            error_result = {
                'success': False,
                'message': f'取消操作失败: {str(e)}'
            }
            self.result_queue.put(error_result)
            return error_result

    def wait_for_result(self) -> Optional[Dict[str, Any]]:
        """等待结果"""
        try:
            # 等待结果，带超时
            result = self.result_queue.get(timeout=self.timeout_seconds)
            return result

        except queue.Empty:
            # 超时
            return None
        except Exception as e:
            print(f"等待结果失败: {e}")
            return {
                'success': False,
                'message': f'等待结果失败: {str(e)}'
            }

    def get_summary(self) -> str:
        """获取反馈摘要"""
        try:
            data = self.feedback_data

            summary_parts = []

            if data.has_text:
                text_preview = data.text_feedback[:50] + "..." if len(
                    data.text_feedback) > 50 else data.text_feedback
                summary_parts.append(f"文字反馈: {text_preview}")

            if data.has_images:
                summary_parts.append(f"图片: {data.get_image_count()}张")

            if not summary_parts:
                return "无反馈内容"

            return " | ".join(summary_parts)

        except Exception as e:
            return f"获取摘要失败: {str(e)}"

    def validate_feedback(self) -> Tuple[bool, str]:
        """验证反馈数据"""
        try:
            if not self.feedback_data.is_valid():
                return False, get_text('no_feedback_error')

            # 验证文字反馈
            if self.feedback_data.has_text:
                text = self.feedback_data.text_feedback
                if not text or len(text.strip()) < 1:
                    return False, "文字反馈不能为空"

                if len(text) > 10000:  # 限制文字长度
                    return False, "文字反馈过长，请控制在10000字符以内"

            # 验证图片
            if self.feedback_data.has_images:
                if len(self.feedback_data.images) > 10:  # 限制图片数量
                    return False, "图片数量过多，最多支持10张图片"

                for i, img in enumerate(self.feedback_data.images):
                    if not img.get('data'):
                        return False, f"第{i+1}张图片数据无效"

            return True, "验证通过"

        except Exception as e:
            return False, f"验证失败: {str(e)}"
