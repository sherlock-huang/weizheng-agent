"""
服务器入口模块

允许以 `python -m src.server` 方式启动
"""

import argparse
from .pixel_server import run_server

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='魏征像素服务端')
    parser.add_argument('--port', '-p', type=int, default=7788, help='HTTP 端口 (默认: 7788)')
    
    args = parser.parse_args()
    
    print(f"启动魏征像素服务端 (端口 {args.port})...")
    run_server(port=args.port)
