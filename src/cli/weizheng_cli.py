"""
魏征 CLI 工具

供 OpenClaw Skill 调用，控制像素服务端

使用方法:
    # 启动说话动画
    python -m src.cli talk "陛下！臣有话说！" --duration 3
    
    # 停止说话动画
    python -m src.cli stop
    
    # 查看状态
    python -m src.cli status

OpenClaw Skill 中调用:
    subprocess.run(["python", "-m", "src.cli", "talk", message])
"""

import argparse
import json
import urllib.request
import urllib.error
import sys
from pathlib import Path


DEFAULT_HOST = "localhost"
DEFAULT_PORT = 7788


def talk(message: str = "陛下！臣有话说！", duration: float = None, 
         messages: list = None, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> dict:
    """
    触发像素魏征说话动画（支持多句话轮播）
    
    Args:
        message: 显示在气泡中的文字
        duration: 已废弃，保留兼容
        messages: 多句话列表，会轮播显示
        host: 服务端地址
        port: 服务端端口
    
    Returns:
        API 响应
    """
    url = f"http://{host}:{port}/api/talk"
    data = json.dumps({
        "message": message,
        "duration": duration,
        "messages": messages
    }).encode('utf-8')
    
    try:
        req = urllib.request.Request(url, data=data, method='POST')
        req.add_header('Content-Type', 'application/json')
        
        with urllib.request.urlopen(req, timeout=5) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result
    
    except urllib.error.URLError as e:
        return {
            "success": False,
            "error": f"无法连接到像素服务端: {e}",
            "hint": f"请确保服务端已启动: python -m src.server --port {port}"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def stop(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> dict:
    """
    停止像素魏征说话动画
    
    Args:
        host: 服务端地址
        port: 服务端端口
    
    Returns:
        API 响应
    """
    url = f"http://{host}:{port}/api/stop"
    data = json.dumps({}).encode('utf-8')
    
    try:
        req = urllib.request.Request(url, data=data, method='POST')
        req.add_header('Content-Type', 'application/json')
        
        with urllib.request.urlopen(req, timeout=5) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result
    
    except urllib.error.URLError as e:
        return {
            "success": False,
            "error": f"无法连接到像素服务端: {e}"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def status(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> dict:
    """
    获取像素服务端状态
    
    Args:
        host: 服务端地址
        port: 服务端端口
    
    Returns:
        API 响应
    """
    url = f"http://{host}:{port}/api/status"
    
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result
    
    except urllib.error.URLError as e:
        return {
            "success": False,
            "error": f"无法连接到像素服务端: {e}"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    """CLI 入口"""
    parser = argparse.ArgumentParser(
        description='魏征 CLI - 控制像素服务端',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 启动说话动画（单条）
  python -m src.cli talk "陛下！臣有话说！"
  
  # 启动说话动画（多条轮播）
  python -m src.cli talk "第一句" "第二句" "第三句"
  
  # 停止说话动画（Agent 输出完成后调用）
  python -m src.cli stop
  
  # 查看状态
  python -m src.cli status
  
  # 指定服务端地址
  python -m src.cli talk "你好" --host 192.168.1.100 --port 7788
        """
    )
    
    parser.add_argument('--host', default=DEFAULT_HOST, help='服务端地址 (默认: localhost)')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, help='服务端端口 (默认: 7788)')
    
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # talk 命令
    talk_parser = subparsers.add_parser('talk', help='触发说话动画')
    talk_parser.add_argument('message', nargs='*', default=['陛下！臣有话说！'], 
                            help='显示的文字（可多条，会轮播）')
    talk_parser.add_argument('--duration', type=float, default=None,
                            help='已废弃，保留兼容')
    
    # stop 命令
    subparsers.add_parser('stop', help='停止说话动画')
    
    # status 命令
    subparsers.add_parser('status', help='查看服务端状态')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 执行命令
    if args.command == 'talk':
        # 处理多句话
        if isinstance(args.message, list) and len(args.message) > 1:
            # 多句话模式
            result = talk(messages=args.message, host=args.host, port=args.port)
        else:
            # 单句话模式
            msg = args.message[0] if isinstance(args.message, list) else args.message
            result = talk(message=msg, host=args.host, port=args.port)
    elif args.command == 'stop':
        result = stop(args.host, args.port)
    elif args.command == 'status':
        result = status(args.host, args.port)
    else:
        parser.print_help()
        return
    
    # 输出结果
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 返回码
    sys.exit(0 if result.get('success') else 1)


if __name__ == '__main__':
    main()
