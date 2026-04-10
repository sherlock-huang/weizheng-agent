#!/usr/bin/env python3
"""
完整链路闭环测试

测试：OpenClaw Skill → CLI → 像素服务端 → 动画

使用方法:
    1. 先启动像素服务端: python -m src.server
    2. 运行此测试: python test_complete_flow.py
"""

import subprocess
import sys
import time
import json
from pathlib import Path


# 配置
PROJECT_ROOT = Path(__file__).parent
CLI_CMD = [sys.executable, "-m", "src.cli"]


def test_server_status():
    """测试服务端状态"""
    print("\n[1/5] 检查像素服务端状态...")
    
    result = subprocess.run(
        CLI_CMD + ["status"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=5
    )
    
    if result.returncode != 0:
        print("  ✗ 像素服务端未启动")
        print("  请先运行: python -m src.server")
        return False
    
    data = json.loads(result.stdout)
    if data.get("success"):
        print(f"  ✓ 服务端运行中")
        print(f"    说话次数: {data['data'].get('talk_count', 0)}")
        print(f"    当前状态: {'正在说话' if data['data'].get('is_talking') else '空闲'}")
        return True
    else:
        print(f"  ✗ 服务端错误: {data.get('error')}")
        return False


def test_talk():
    """测试说话动画"""
    print("\n[2/5] 测试说话动画...")
    print("  观察屏幕右下角的像素魏征！")
    
    result = subprocess.run(
        CLI_CMD + ["talk", "陛下！臣有话说！", "--duration", "3"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=5
    )
    
    if result.returncode == 0:
        data = json.loads(result.stdout)
        if data.get("success"):
            print("  ✓ 说话动画已触发")
            print("  请观察像素魏征是否显示气泡并说话...")
            time.sleep(3)  # 等待动画完成
            return True
        else:
            print(f"  ✗ 触发失败: {data.get('error')}")
            return False
    else:
        print(f"  ✗ CLI 调用失败: {result.stderr}")
        return False


def test_stop():
    """测试停止动画"""
    print("\n[3/5] 测试停止动画...")
    
    # 先触发说话
    subprocess.run(
        CLI_CMD + ["talk", "测试中...", "--duration", "10"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        timeout=5
    )
    
    time.sleep(1)  # 等待动画开始
    
    # 然后停止
    result = subprocess.run(
        CLI_CMD + ["stop"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=5
    )
    
    if result.returncode == 0:
        data = json.loads(result.stdout)
        if data.get("success"):
            print("  ✓ 停止动画成功")
            return True
        else:
            print(f"  ✗ 停止失败: {data.get('error')}")
            return False
    else:
        print(f"  ✗ CLI 调用失败: {result.stderr}")
        return False


def test_skill_hook():
    """测试 Skill Hook"""
    print("\n[4/5] 测试 Skill Hook...")
    
    sys.path.insert(0, str(PROJECT_ROOT))
    from skills.openclaw.weizheng_skill.hook import check_trigger, trigger_talk
    
    # 测试触发词检测
    test_cases = [
        ("魏征，你怎么看？", True),
        ("这段代码怎么样？", False),
        ("魏征，点评一下这个方案", True),
        ("@魏征", True),
    ]
    
    all_passed = True
    for text, expected in test_cases:
        triggered, _ = check_trigger(text)
        status = "✓" if triggered == expected else "✗"
        print(f"  {status} '{text[:20]}...' -> {'触发' if triggered else '未触发'}")
        if triggered != expected:
            all_passed = False
    
    return all_passed


def test_complete_flow():
    """测试完整链路"""
    print("\n[5/5] 测试完整链路（模拟 OpenClaw 调用）...")
    print("  模拟场景: 用户说 '魏征，你怎么看？'")
    
    sys.path.insert(0, str(PROJECT_ROOT))
    from skills.openclaw.weizheng_skill.hook import on_user_message
    
    # 模拟用户消息
    message = "这段代码有问题吗？\ndef add(a, b):\n    return a + b\n\n魏征，你怎么看？"
    context = {}
    
    # 调用 Hook
    result = on_user_message(message, context)
    
    if result.get("triggered"):
        print("  ✓ 触发词检测成功")
        print(f"  ✓ 内容提取: '{result.get('content', '')[:30]}...'")
        
        if result.get("talk_result", {}).get("success"):
            print("  ✓ 像素动画触发成功")
            print("\n  观察屏幕右下角的像素魏征！")
            time.sleep(3)
            return True
        else:
            print(f"  ✗ 动画触发失败: {result.get('talk_result', {}).get('error')}")
            return False
    else:
        print("  ✗ 触发词检测失败")
        return False


def main():
    """主测试函数"""
    print("="*60)
    print("魏征 Agent 完整链路测试")
    print("="*60)
    print("\n测试内容:")
    print("  1. 像素服务端状态")
    print("  2. CLI talk 命令")
    print("  3. CLI stop 命令")
    print("  4. Skill Hook 触发词检测")
    print("  5. 完整链路闭环")
    print("="*60)
    
    # 运行测试
    results = []
    
    results.append(("服务端状态", test_server_status()))
    results.append(("说话动画", test_talk()))
    results.append(("停止动画", test_stop()))
    results.append(("Skill Hook", test_skill_hook()))
    results.append(("完整链路", test_complete_flow()))
    
    # 结果汇总
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    passed = 0
    failed = 0
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {status} - {name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("="*60)
    print(f"总计: {passed} 通过, {failed} 失败")
    print("="*60)
    
    if failed == 0:
        print("\n🎉 所有测试通过！链路闭环完整！")
    else:
        print(f"\n⚠️ 有 {failed} 项测试失败，请检查配置")
    
    return failed == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
