"""
图片处理模块
负责图片的加载、处理、验证和格式转换
"""

import io
import base64
from pathlib import Path
from typing import Optional, Dict, Any, List
from PIL import Image, ImageGrab
import tkinter as tk
from tkinter import filedialog, messagebox

try:
    # 尝试相对导入
    from ..utils.i18n import get_text
except ImportError:
    # 回退到绝对导入
    from utils.i18n import get_text


class ImageHandler:
    """图片处理器"""

    # 支持的图片格式
    SUPPORTED_FORMATS = {
        '.png': 'PNG',
        '.jpg': 'JPEG',
        '.jpeg': 'JPEG',
        '.gif': 'GIF',
        '.bmp': 'BMP',
        '.webp': 'WEBP'
    }

    # 最大图片尺寸（像素）
    MAX_IMAGE_SIZE = (4096, 4096)

    # 最大文件大小（字节）
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    @classmethod
    def load_image_as_bytes(cls, file_path: str) -> bytes:
        """从文件加载图片并返回字节数据"""
        try:
            path = Path(file_path)

            # 检查文件是否存在
            if not path.exists():
                raise FileNotFoundError(get_text('file_not_found', file_path))

            # 检查文件大小
            file_size = path.stat().st_size
            if file_size > cls.MAX_FILE_SIZE:
                raise ValueError(
                    f"文件过大: {file_size / 1024 / 1024:.1f}MB，最大支持 {cls.MAX_FILE_SIZE / 1024 / 1024}MB")

            # 检查文件格式
            if path.suffix.lower() not in cls.SUPPORTED_FORMATS:
                raise ValueError(get_text('invalid_image', path.suffix))

            # 读取并验证图片
            with open(path, 'rb') as f:
                image_data = f.read()

            # 验证图片
            img = Image.open(io.BytesIO(image_data))

            # 检查图片尺寸
            if img.size[0] > cls.MAX_IMAGE_SIZE[0] or img.size[1] > cls.MAX_IMAGE_SIZE[1]:
                raise ValueError(
                    f"图片尺寸过大: {img.size}，最大支持 {cls.MAX_IMAGE_SIZE}")

            # 转换为PNG格式以确保兼容性
            if img.format != 'PNG':
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                image_data = buffer.getvalue()

            return image_data

        except Exception as e:
            raise Exception(f"加载图片失败: {str(e)}")

    @classmethod
    def get_clipboard_image(cls) -> Optional[bytes]:
        """从剪贴板获取图片数据（简化版本，仅返回字节数据）"""
        try:
            result = cls.load_from_clipboard()
            return result['data'] if result else None
        except Exception as e:
            print(f"从剪贴板获取图片失败: {e}")
            return None

    @classmethod
    def load_from_file(cls, file_path: str) -> Optional[Dict[str, Any]]:
        """从文件加载图片"""
        try:
            path = Path(file_path)

            # 检查文件是否存在
            if not path.exists():
                raise FileNotFoundError(get_text('file_not_found', file_path))

            # 检查文件大小
            file_size = path.stat().st_size
            if file_size > cls.MAX_FILE_SIZE:
                raise ValueError(
                    f"文件过大: {file_size / 1024 / 1024:.1f}MB，最大支持 {cls.MAX_FILE_SIZE / 1024 / 1024}MB")

            # 检查文件格式
            if path.suffix.lower() not in cls.SUPPORTED_FORMATS:
                raise ValueError(get_text('invalid_image', path.suffix))

            # 读取文件数据
            with open(path, 'rb') as f:
                image_data = f.read()

            # 验证图片
            img = Image.open(io.BytesIO(image_data))

            # 检查图片尺寸
            if img.size[0] > cls.MAX_IMAGE_SIZE[0] or img.size[1] > cls.MAX_IMAGE_SIZE[1]:
                raise ValueError(
                    f"图片尺寸过大: {img.size}，最大支持 {cls.MAX_IMAGE_SIZE}")

            return {
                'data': image_data,
                'image': img,
                'source': f'文件: {path.name}',
                'size': img.size,
                'format': img.format,
                'file_size': file_size
            }

        except Exception as e:
            print(f"加载图片文件失败: {e}")
            return None

    @classmethod
    def load_from_clipboard(cls) -> Optional[Dict[str, Any]]:
        """从剪贴板加载图片"""
        try:
            # 尝试获取剪贴板图片
            img = ImageGrab.grabclipboard()

            if img is None:
                return None

            # 检查图片尺寸
            if img.size[0] > cls.MAX_IMAGE_SIZE[0] or img.size[1] > cls.MAX_IMAGE_SIZE[1]:
                raise ValueError(
                    f"图片尺寸过大: {img.size}，最大支持 {cls.MAX_IMAGE_SIZE}")

            # 转换为PNG格式
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            image_data = buffer.getvalue()

            return {
                'data': image_data,
                'image': img,
                'source': '剪贴板',
                'size': img.size,
                'format': 'PNG',
                'file_size': len(image_data)
            }

        except ImportError:
            print("ImageGrab功能在当前系统上不可用")
            return None
        except Exception as e:
            print(f"从剪贴板获取图片失败: {e}")
            return None

    @classmethod
    def select_files_dialog(cls, parent: tk.Widget = None) -> List[Dict[str, Any]]:
        """显示文件选择对话框"""
        try:
            file_types = [
                ("图片文件", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("PNG文件", "*.png"),
                ("JPEG文件", "*.jpg *.jpeg"),
                ("所有文件", "*.*")
            ]

            file_paths = filedialog.askopenfilenames(
                parent=parent,
                title="选择图片文件（可多选）",
                filetypes=file_types
            )

            images = []
            failed_files = []

            for file_path in file_paths:
                image_data = cls.load_from_file(file_path)
                if image_data:
                    images.append(image_data)
                else:
                    failed_files.append(Path(file_path).name)

            # 显示失败的文件
            if failed_files:
                messagebox.showwarning(
                    "警告",
                    f"以下文件加载失败:\n" + "\n".join(failed_files)
                )

            return images

        except Exception as e:
            print(f"文件选择对话框失败: {e}")
            return []

    @classmethod
    def validate_image_data(cls, image_data: bytes) -> bool:
        """验证图片数据"""
        try:
            img = Image.open(io.BytesIO(image_data))

            # 检查尺寸
            if img.size[0] > cls.MAX_IMAGE_SIZE[0] or img.size[1] > cls.MAX_IMAGE_SIZE[1]:
                return False

            # 检查文件大小
            if len(image_data) > cls.MAX_FILE_SIZE:
                return False

            return True

        except Exception:
            return False

    @classmethod
    def get_image_info(cls, image_path: str) -> Dict[str, Any]:
        """获取图片信息"""
        try:
            path = Path(image_path)

            if not path.exists():
                return {'error': f'文件不存在: {image_path}'}

            with Image.open(path) as img:
                info = {
                    'filename': path.name,
                    'format': img.format,
                    'size': img.size,
                    'mode': img.mode,
                    'file_size': path.stat().st_size,
                    'file_size_mb': round(path.stat().st_size / 1024 / 1024, 2)
                }

            return info

        except Exception as e:
            return {'error': f'获取图片信息失败: {str(e)}'}

    @classmethod
    def format_image_info(cls, info: Dict[str, Any]) -> str:
        """格式化图片信息为字符串"""
        if 'error' in info:
            return info['error']

        return f"""文件名: {info['filename']}
格式: {info['format']}
尺寸: {info['size'][0]} × {info['size'][1]}
模式: {info['mode']}
文件大小: {info['file_size_mb']} MB"""

    @classmethod
    def create_thumbnail(cls, image: Image.Image, size: tuple = (100, 80)) -> Image.Image:
        """创建缩略图"""
        try:
            thumbnail = image.copy()
            thumbnail.thumbnail(size, Image.Resampling.LANCZOS)
            return thumbnail
        except Exception as e:
            print(f"创建缩略图失败: {e}")
            return image

    @classmethod
    def convert_to_base64(cls, image_data: bytes) -> str:
        """将图片数据转换为base64字符串"""
        try:
            return base64.b64encode(image_data).decode('utf-8')
        except Exception as e:
            print(f"转换base64失败: {e}")
            return ""

    @classmethod
    def convert_from_base64(cls, base64_str: str) -> Optional[bytes]:
        """从base64字符串转换为图片数据"""
        try:
            return base64.b64decode(base64_str)
        except Exception as e:
            print(f"从base64转换失败: {e}")
            return None
