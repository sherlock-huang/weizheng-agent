"""
飞书机器人集成模块

功能：
1. 接收飞书消息
2. 读取 OpenClaw/魏征的对话上下文
3. 触发魏征进行审查
4. 发送审查结果到飞书
"""

import json
import requests
import hmac
import hashlib
import base64
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
import threading
import time


class FeishuBot:
    """
    飞书机器人
    
    使用方式：
    1. 在飞书开放平台创建机器人
    2. 获取 App ID 和 App Secret
    3. 订阅消息事件
    """
    
    def __init__(self, app_id: Optional[str] = None, 
                 app_secret: Optional[str] = None,
                 webhook_url: Optional[str] = None):
        """
        初始化飞书机器人
        
        Args:
            app_id: 飞书应用ID
            app_secret: 飞书应用密钥
            webhook_url: Webhook地址（用于发送消息）
        """
        self.app_id = app_id or ""
        self.app_secret = app_secret or ""
        self.webhook_url = webhook_url or ""
        
        self.access_token: Optional[str] = None
        self.token_expire_time: Optional[float] = None
        
        # 消息处理器
        self.message_handler: Optional[Callable] = None
        
        # 上下文存储
        self.conversation_contexts: Dict[str, List[Dict]] = {}
        
    def set_message_handler(self, handler: Callable[[str, str, Dict], None]):
        """设置消息处理器"""
        self.message_handler = handler
    
    def _get_access_token(self) -> str:
        """获取访问令牌"""
        if self.access_token and self.token_expire_time and time.time() < self.token_expire_time:
            return self.access_token
        
        url = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal"
        
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        response = requests.post(url, json=data, timeout=30)
        result = response.json()
        
        if result.get("code") == 0:
            self.access_token = result["app_access_token"]
            # 提前5分钟过期
            self.token_expire_time = time.time() + result.get("expire", 7200) - 300
            return self.access_token
        else:
            raise Exception(f"获取token失败: {result}")
    
    def send_message(self, chat_id: str, content: str, msg_type: str = "text") -> bool:
        """
        发送消息到飞书
        
        Args:
            chat_id: 聊天ID
            content: 消息内容
            msg_type: 消息类型
        """
        try:
            token = self._get_access_token()
            
            url = "https://open.feishu.cn/open-apis/message/v4/send"
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            if msg_type == "text":
                message = {
                    "chat_id": chat_id,
                    "msg_type": "text",
                    "content": {
                        "text": content
                    }
                }
            elif msg_type == "interactive":
                # 卡片消息
                message = {
                    "chat_id": chat_id,
                    "msg_type": "interactive",
                    "card": content
                }
            else:
                message = {
                    "chat_id": chat_id,
                    "msg_type": msg_type,
                    "content": content
                }
            
            response = requests.post(url, headers=headers, json=message, timeout=30)
            result = response.json()
            
            if result.get("code") == 0:
                print(f"[Feishu] 消息发送成功")
                return True
            else:
                print(f"[Feishu] 发送失败: {result}")
                return False
                
        except Exception as e:
            print(f"[Feishu] 发送错误: {e}")
            return False
    
    def handle_webhook(self, request_data: Dict) -> Dict:
        """
        处理飞书 webhook 回调
        
        需要在飞书后台配置事件订阅URL
        """
        # 验证 URL（首次配置时需要）
        if request_data.get("type") == "url_verification":
            return {"challenge": request_data.get("challenge")}
        
        # 处理事件
        event = request_data.get("event", {})
        event_type = event.get("type")
        
        if event_type == "message":
            return self._handle_message_event(event)
        
        return {"status": "ok"}
    
    def _handle_message_event(self, event: Dict) -> Dict:
        """处理消息事件"""
        msg_type = event.get("msg_type")
        chat_id = event.get("chat_id")
        sender = event.get("sender", {}).get("sender_id", {}).get("user_id", "")
        message_id = event.get("message_id", "")
        
        # 获取消息内容
        content = event.get("content", "")
        if isinstance(content, str):
            try:
                content = json.loads(content)
            except:
                pass
        
        text = content.get("text", "") if isinstance(content, dict) else str(content)
        
        # 存储上下文
        if chat_id not in self.conversation_contexts:
            self.conversation_contexts[chat_id] = []
        
        self.conversation_contexts[chat_id].append({
            "timestamp": datetime.now().isoformat(),
            "role": "user",
            "sender": sender,
            "content": text
        })
        
        # 只保留最近20条
        if len(self.conversation_contexts[chat_id]) > 20:
            self.conversation_contexts[chat_id] = self.conversation_contexts[chat_id][-20:]
        
        # 调用处理器
        if self.message_handler:
            self.message_handler(text, chat_id, {
                "sender": sender,
                "message_id": message_id,
                "context": self.conversation_contexts[chat_id]
            })
        
        return {"status": "ok"}
    
    def get_context(self, chat_id: str, limit: int = 10) -> List[Dict]:
        """获取对话上下文"""
        context = self.conversation_contexts.get(chat_id, [])
        return context[-limit:] if context else []
    
    def reply_with_weizheng(self, chat_id: str, user_message: str, 
                           weizheng_result: Dict, context: List[Dict]):
        """
        使用魏征的审查结果回复飞书
        """
        # 构建回复内容
        reply = f"{weizheng_result.get('agent_personality', '')}\n\n"
        reply += f"{weizheng_result.get('summary', '')}\n"
        
        if weizheng_result.get('critics'):
            reply += "\n详细意见：\n"
            for i, c in enumerate(weizheng_result['critics'][:5], 1):
                sev = c.get('severity', 'minor')
                icon = {'critical': '🔴', 'major': '🟠', 'minor': '🟡', 'suggestion': '💡'}.get(sev, '⚪')
                reply += f"\n{icon} **{c['title']}**\n"
                reply += f"> {c.get('critique', '')}\n"
                if c.get('suggestion'):
                    reply += f"> 💡 建议：{c['suggestion']}\n"
        
        # 发送
        self.send_message(chat_id, reply)


class FeishuOpenClawBridge:
    """
    飞书-OpenClaw 桥接器
    
    实现：
    1. 读取 OpenClaw 的对话上下文
    2. 在飞书中触发魏征审查
    3. 同步两边的记忆
    """
    
    def __init__(self, feishu_bot: FeishuBot, openclaw_integration):
        from .openclaw import OpenClawIntegration
        self.feishu = feishu_bot
        self.openclaw: OpenClawIntegration = openclaw_integration
        self.weizheng_agent = None
        
    def set_weizheng_agent(self, agent):
        """设置魏征Agent"""
        self.weizheng_agent = agent
    
    def handle_feishu_message(self, text: str, chat_id: str, meta: Dict):
        """
        处理飞书消息
        
        当检测到触发词时，读取上下文并进行审查
        """
        # 检查触发词
        triggers = ["魏征", "weizheng", "你怎么看", "提意见", "挑毛病"]
        is_triggered = any(t in text.lower() for t in triggers)
        
        if not is_triggered:
            return
        
        print(f"[Bridge] 检测到魏征触发词，来自飞书: {chat_id}")
        
        # 1. 获取飞书上下文
        feishu_context = meta.get('context', [])
        
        # 2. 获取 OpenClaw 上下文（如果配置了项目）
        openclaw_context = []
        if self.openclaw.current_project:
            openclaw_history = self.openclaw.read_conversation_history(
                limit=5
            )
            openclaw_context = [
                {"role": h.get("agent", "user"), "content": h.get("content", "")}
                for h in openclaw_history
            ]
        
        # 3. 合并上下文
        merged_context = self._merge_contexts(feishu_context, openclaw_context)
        
        print(f"[Bridge] 合并上下文: {len(merged_context)} 条")
        
        # 4. 调用魏征进行审查
        if self.weizheng_agent:
            # 使用LLM进行真正的审查
            result = self.weizheng_agent.process_with_context(
                content=text,
                context=merged_context,
                context_type="general"
            )
            
            # 5. 回复飞书
            self.feishu.reply_with_weizheng(chat_id, text, result, merged_context)
            
            # 6. 同步到 OpenClaw
            if self.openclaw.current_project:
                self.openclaw.write_to_openclaw_memory(
                    content=f"[飞书/{chat_id}] {result.get('summary', '')}",
                    context_type="feishu"
                )
    
    def _merge_contexts(self, feishu_ctx: List[Dict], 
                       openclaw_ctx: List[Dict]) -> List[Dict]:
        """合并两个上下文列表"""
        # 简单的合并策略：交替取两边的消息
        merged = []
        
        # 先添加 OpenClaw 的上下文
        for msg in openclaw_ctx:
            merged.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", ""),
                "source": "openclaw"
            })
        
        # 再添加飞书的上下文
        for msg in feishu_ctx:
            merged.append({
                "role": "user",
                "content": msg.get("content", ""),
                "source": "feishu",
                "sender": msg.get("sender", "")
            })
        
        # 按时间排序（如果有时间戳）
        # 这里简化处理，只返回最近10条
        return merged[-10:] if len(merged) > 10 else merged


def create_feishu_bot_from_env() -> FeishuBot:
    """从环境变量创建飞书机器人"""
    import os
    
    app_id = os.getenv("FEISHU_APP_ID", "")
    app_secret = os.getenv("FEISHU_APP_SECRET", "")
    
    return FeishuBot(app_id=app_id, app_secret=app_secret)
