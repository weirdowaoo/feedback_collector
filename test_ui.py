#!/usr/bin/env python3
"""
直接测试反馈收集器UI界面
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ui.feedback_dialog import ModernFeedbackDialog

def main():
    """主函数"""
    print("启动反馈收集器界面测试...")
    
    try:
        # 创建对话框
        dialog = ModernFeedbackDialog(timeout_seconds=0)  # 无超时
        
        # 显示界面
        result = dialog.show_dialog()
        
        # 打印结果
        if result:
            print(f"反馈结果: {result}")
        else:
            print("用户取消了反馈")
            
    except Exception as e:
        print(f"启动界面失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
