#!/usr/bin/env python3
"""
魏征 Agent 演示

展示完整闭环功能：
1. 检查/启动像素服务端
2. 触发说话动画
3. 模拟 OpenClaw Skill 调用
4. 停止动画
"""

import subprocess
import sys
import time
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent
CLI_CMD = [sys.executable, "-m", "src.cli"]


def check_server():
    """检查服务端是否运行"""
    result = subprocess.run(
        CLI_CMD + ["status"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=5
    )
    if result.returncode == 0:
        try:
            data = json.loads(result.stdout)
            return data.get("success", False)
        except:
            pass
    return False


def start_talk(message="陛下！臣有话说！", duration=3):
    """触发说话动画"""
    result = subprocess.run(
        CLI_CMD + ["talk", message, "--duration", str(duration)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=5
    )
    return result.returncode == 0


def stop_talk():
    """停止说话动画"""
    result = subprocess.run(
        CLI_CMD + ["stop"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=5
    )
    return result.returncode == 0


def simulate_openclaw_skill():
    """模拟 OpenClaw Skill 调用"""
    sys.path.insert(0, str(PROJECT_ROOT))
    from skills.openclaw.weizheng_skill.hook import on_user_message
    
    message = """
我的代码：
def calculate_total(items):
    total = 0
    for item in items:
        total += item['price']
    return total

魏征，你怎么看？
"""
    return on_user_message(message, {})


def main():
    print("=" * 60)
    print("魏征 Agent 演示")
    print("=" * 60)
    print()
    
    # 1. 检查服务端
    print("[1/4] 检查像素服务端...")
    if check_server():
        print("  + 服务端已运行")
    else:
        print("  - 服务端未运行")
        print("  请运行: python -m src.server")
        print("  或在另一个窗口运行: start_server.bat")
        return False
    
    # 2. 测试说话
    print()
    print("[2/4] 测试说话动画...")
    print("  观察屏幕右下角的像素魏征！")
    if start_talk("陛下！臣有本奏！", duration=3):
        print("  + 说话动画已触发")
        time.sleep(3)
    else:
        print("  - 触发失败")
        return False
    
    # 3. 模拟 OpenClaw 调用
    print()
    print("[3/4] 模拟 OpenClaw Skill 调用...")
    try:
        result = simulate_openclaw_skill()
        if result.get("triggered"):
            print("  + 触发词检测成功")
            if result.get("talk_result", {}).get("success"):
                print("  + 像素动画触发成功")
                time.sleep(2)
            else:
                print(f"  - 动画触发失败")
        else:
            print("  - 触发词检测失败")
    except Exception as e:
        print(f"  - Skill 错误: {e}")
    
    # 4. 停止动画
    print()
    print("[4/4] 停止动画...")
    if stop_talk():
        print("  + 动画已停止")
    else:
        print("  - 停止失败")
    
    print()
    print("=" * 60)
    print("演示完成！")
    print("=" * 60)
    print()
    print("实际使用场景：")
    print("  在 OpenClaw 中对话时输入：")
    print('    "魏征，你怎么看？"')
    print()
    print("  系统将：")
    print("  1. 检测触发词")
    print("  2. 启动像素魏征说话动画")
    print("  3. 魏征 Agent 生成审查意见")
    print("  4. 自动停止动画")
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
