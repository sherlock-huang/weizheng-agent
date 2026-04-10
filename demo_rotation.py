#!/usr/bin/env python3
"""
魏征多句话轮播演示

展示 Agent 输出时魏征轮播多句话的效果
"""

import sys
import time
import json
import urllib.request
import threading

sys.path.insert(0, '.')

def call_api(port, path, data=None):
    """调用 API"""
    url = f"http://localhost:{port}{path}"
    if data is not None:
        data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(url, data=data, method='POST')
        req.add_header('Content-Type', 'application/json')
    else:
        req = urllib.request.Request(url)
    
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    port = 7788
    
    print("="*60)
    print("魏征多句话轮播演示")
    print("="*60)
    print()
    print("场景: OpenClaw 中输入 '魏征，你怎么看？'")
    print()
    
    # 检查服务器
    print("[1] 检查像素服务器...")
    result = call_api(port, "/api/status")
    if not result.get("success"):
        print("    服务器未启动，请先运行: python -m src.server")
        print("    或使用无头模式: python src/server/headless_server.py")
        return
    print("    [OK] 服务器运行中")
    
    # Agent 开始思考 - 启动轮播
    print()
    print("[2] Agent 开始思考 -> 启动魏征说话（轮播模式）...")
    thinking_messages = [
        "陛下，容臣思量...",
        "此事颇有蹊跷！",
        "臣斗胆直言...",
        "容臣细细道来...",
        "陛下圣明，但...",
    ]
    
    result = call_api(port, "/api/talk", {
        "message": "陛下！",
        "messages": thinking_messages
    })
    
    if result.get("success"):
        print(f"    [OK] 魏征开始轮播，共 {len(thinking_messages)} 句")
        print("    气泡在魏征右侧，显示轮播进度点")
    else:
        print(f"    [FAIL] {result}")
        return
    
    # 模拟 Agent 生成内容的过程
    print()
    print("[3] 模拟 Agent 生成审查意见（约 10 秒）...")
    print("    此期间魏征会持续轮播说话...")
    
    for i in range(10, 0, -1):
        print(f"    Agent 生成中... {i}s", end='\r')
        time.sleep(1)
    print()
    
    # Agent 输出完成 - 停止轮播
    print()
    print("[4] Agent 输出完成 -> 停止魏征说话...")
    result = call_api(port, "/api/stop")
    
    if result.get("success"):
        print("    [OK] 魏征停止说话，显示审查意见")
    else:
        print(f"    [FAIL] {result}")
    
    print()
    print("="*60)
    print("演示完成！")
    print("="*60)
    print()
    print("完整流程:")
    print("  1. 用户: '魏征，你怎么看？'")
    print("  2. Skill 启动轮播（多句话循环显示）")
    print("  3. Agent 生成回复（期间轮播继续）")
    print("  4. Agent 完成后调用 stop 停止轮播")
    print("  5. 显示 Agent 的审查意见")
    print()
    print("特点:")
    print("  - 气泡在魏征右侧，不遮挡")
    print("  - 多句话轮播，显示进度点")
    print("  - 只有 Agent 完成后才停止")

if __name__ == '__main__':
    main()
