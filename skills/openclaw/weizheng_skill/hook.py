"""
魏征 Skill Hook

OpenClaw 插件钩子，监听对话并触发魏征

安装到 OpenClaw:
    复制本目录到 ~/.openclaw/skills/weizheng/
"""

import subprocess
import json
import os
from pathlib import Path


# 配置
WEIZHENG_CLI = ["python", "-m", "src.cli"]
WEIZHENG_SERVER_HOST = "localhost"
WEIZHENG_SERVER_PORT = 7788
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


def check_trigger(text: str) -> tuple[bool, str]:
    """
    检查是否触发魏征
    
    Returns:
        (是否触发, 提取的内容)
    """
    triggers = [
        "魏征，你怎么看",
        "魏征，有何高见",
        "魏征，说说你的看法",
        "魏征，点评一下",
        "魏征，提提意见",
        "@魏征",
        "weizheng, what do you think",
    ]
    
    text_lower = text.lower()
    
    for trigger in triggers:
        if trigger in text_lower:
            # 提取触发词后的内容
            idx = text_lower.find(trigger)
            content = text[idx + len(trigger):].strip()
            content = content.strip('？?。.,')
            return True, content
    
    return False, ""


def trigger_talk(message: str = "陛下！臣有话说！", messages: list = None) -> dict:
    """
    触发像素魏征说话动画（支持多句话轮播）
    
    通过 CLI 工具调用像素服务端
    
    Args:
        message: 单条消息（向后兼容）
        messages: 多句话列表，会轮播显示直到调用 stop
    """
    try:
        # 构建命令
        cmd = WEIZHENG_CLI + [
            "--host", WEIZHENG_SERVER_HOST,
            "--port", str(WEIZHENG_SERVER_PORT),
            "talk"
        ]
        
        # 添加消息
        if messages and isinstance(messages, list):
            cmd.extend(messages)
        else:
            cmd.append(message)
        
        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return {
                "success": False,
                "error": result.stderr,
                "hint": "请确保像素服务端已启动: python -m src.server"
            }
    
    except Exception as e:
        return {"success": False, "error": str(e)}


def stop_talk() -> dict:
    """停止像素魏征说话动画"""
    try:
        cmd = WEIZHENG_CLI + [
            "stop",
            "--host", WEIZHENG_SERVER_HOST,
            "--port", str(WEIZHENG_SERVER_PORT)
        ]
        
        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return {"success": False, "error": result.stderr}
    
    except Exception as e:
        return {"success": False, "error": str(e)}


def on_user_message(message: str, context: dict) -> dict:
    """
    OpenClaw 钩子：用户发送消息时调用
    
    触发魏征说话动画，开始轮播，直到 Agent 输出完成后调用 stop
    
    Returns:
        如果需要处理，返回处理结果
    """
    triggered, content = check_trigger(message)
    
    if not triggered:
        return {"handled": False}
    
    # 准备多句话轮播（魏征开始思考的提示语）
    thinking_messages = [
        "陛下，容臣思量...",
        "此事颇有蹊跷...",
        "臣斗胆直言...",
        "容臣细细道来...",
        "陛下圣明，但...",
    ]
    
    # 触发像素魏征动画（轮播模式，不自动停止）
    talk_result = trigger_talk(messages=thinking_messages)
    
    return {
        "handled": True,
        "triggered": True,
        "content": content,
        "talk_result": talk_result
    }


# OpenClaw Hook 接口
class WeizhengHook:
    """OpenClaw Hook 类"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
    
    def on_message(self, message: str, context: dict) -> dict:
        """消息钩子"""
        return on_user_message(message, context)
    
    def pre_response(self, response: str, context: dict) -> str:
        """响应前钩子"""
        # 如果当前是魏征响应，确保动画持续
        return response
    
    def post_response(self, response: str, context: dict):
        """响应后钩子"""
        # 响应完成后停止动画
        stop_talk()


# 导出
hook = WeizhengHook
