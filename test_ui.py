#!/usr/bin/env python3
"""
直接测试反馈收集器UI界面
测试窗口重用功能
"""

from src.ui.feedback_dialog import ModernFeedbackDialog
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_single_dialog():
    """测试单次对话框"""
    print("=== 单次对话框测试 ===")

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

        # 清理资源
        dialog.destroy()

    except Exception as e:
        print(f"启动界面失败: {e}")
        import traceback
        traceback.print_exc()


def test_reusable_dialog():
    """测试可重用对话框"""
    print("=== 可重用对话框测试 ===")

    try:
        # 创建对话框（只创建一次）
        dialog = ModernFeedbackDialog(timeout_seconds=0)  # 无超时

        test_count = 0
        max_tests = 3

        while test_count < max_tests:
            test_count += 1
            print(f"\n--- 第 {test_count} 次测试 ---")
            print("请在对话框中输入反馈或取消...")

            # 显示界面（重用同一个窗口）
            result = dialog.show_dialog()

            # 打印结果
            if result:
                if result.get('success'):
                    print(f"✅ 反馈提交成功!")
                    if result.get('has_text'):
                        print(f"   文字反馈: {result['text_feedback'][:50]}...")
                    if result.get('has_images'):
                        print(f"   图片数量: {len(result['images'])}")
                else:
                    print(f"❌ 操作取消: {result.get('message', '未知原因')}")
            else:
                print("❌ 未获取到结果")

            # 询问是否继续测试
            if test_count < max_tests:
                try:
                    continue_test = input(
                        f"\n是否继续测试？(y/n，剩余 {max_tests - test_count} 次): ").strip().lower()
                    if continue_test not in ['y', 'yes', '是', '']:
                        break
                except KeyboardInterrupt:
                    print("\n用户中断测试")
                    break

        print(f"\n=== 测试完成，共进行了 {test_count} 次测试 ===")

        # 最后清理资源
        dialog.destroy()
        print("✅ 资源清理完成")

    except Exception as e:
        print(f"启动界面失败: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主函数"""
    print("反馈收集器界面测试工具")
    print("=" * 40)

    try:
        test_mode = input(
            "选择测试模式:\n1. 单次测试\n2. 重用测试（推荐）\n请输入选择 (1/2): ").strip()

        if test_mode == "1":
            test_single_dialog()
        elif test_mode == "2" or test_mode == "":
            test_reusable_dialog()
        else:
            print("无效选择，使用默认的重用测试模式")
            test_reusable_dialog()

    except KeyboardInterrupt:
        print("\n\n用户中断测试")
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
