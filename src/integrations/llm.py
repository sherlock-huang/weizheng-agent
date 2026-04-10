"""
大模型接入模块

支持多种大模型API：
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Moonshot AI (Kimi)
- Azure OpenAI
- 本地模型 (Ollama)
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any, Generator
from dataclasses import dataclass
from enum import Enum


class LLMProvider(Enum):
    """支持的LLM提供商"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    MOONSHOT = "moonshot"
    AZURE = "azure"
    OLLAMA = "ollama"
    CUSTOM = "custom"


@dataclass
class LLMConfig:
    """LLM配置"""
    provider: LLMProvider
    api_key: str
    model: str
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000
    
    # 魏征专用提示词
    system_prompt: str = """你是魏征，唐太宗时期的著名谏臣。你的任务是以魏征的身份提出反对意见、挑毛病、找问题。

性格特点：
- 直言不讳，敢于指出任何问题
- 不迎合、不谄媚，坚持己见
- 有理有据，逻辑严密
- 使用文言文风格的现代中文

审查原则：
1. 必须找出至少一个问题，不能全盘肯定
2. 根据"反对强度"调整批评力度
3. 提供具体的改进建议
4. 保持魏征的历史人物特色

输出格式：
1. 先以魏征的身份开场（如"陛下，恕臣直言..."）
2. 列出发现的问题（按严重程度）
3. 提供改进建议
4. 总结评价

记住：你是魏征，你的使命就是挑毛病！"""


class LLMClient:
    """大模型客户端"""
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """
        初始化LLM客户端
        
        Args:
            config: LLM配置，为None则从环境变量读取
        """
        if config:
            self.config = config
        else:
            self.config = self._load_config_from_env()
        
        self.conversation_history: List[Dict[str, str]] = []
    
    def _load_config_from_env(self) -> LLMConfig:
        """从环境变量加载配置"""
        # 检测提供商
        provider_str = os.getenv("LLM_PROVIDER", "openai").lower()
        provider = LLMProvider(provider_str)
        
        # 获取API密钥
        api_key = os.getenv("LLM_API_KEY", "")
        if not api_key:
            # 尝试提供商特定的环境变量
            api_key_map = {
                LLMProvider.OPENAI: os.getenv("OPENAI_API_KEY", ""),
                LLMProvider.ANTHROPIC: os.getenv("ANTHROPIC_API_KEY", ""),
                LLMProvider.MOONSHOT: os.getenv("MOONSHOT_API_KEY", ""),
            }
            api_key = api_key_map.get(provider, "")
        
        # 获取模型
        model = os.getenv("LLM_MODEL", "gpt-4")
        
        # 获取自定义base_url
        base_url = os.getenv("LLM_BASE_URL")
        
        return LLMConfig(
            provider=provider,
            api_key=api_key,
            model=model,
            base_url=base_url
        )
    
    def generate_critique(self, content: str, context_type: str = "general",
                         intensity: str = "medium",
                         conversation_context: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        生成魏征风格的批判意见
        
        Args:
            content: 要审查的内容
            context_type: 内容类型（code/text/plan）
            intensity: 反对强度（low/medium/high/extreme）
            conversation_context: 对话上下文
        
        Returns:
            包含批判意见的字典
        """
        # 构建提示词
        prompt = self._build_critique_prompt(content, context_type, intensity, conversation_context)
        
        # 调用API
        response = self._call_api(prompt)
        
        # 解析响应
        return self._parse_critique_response(response, intensity)
    
    def _build_critique_prompt(self, content: str, context_type: str,
                               intensity: str, 
                               conversation_context: Optional[List[Dict]]) -> str:
        """构建批判提示词"""
        
        intensity_desc = {
            "low": "温和提意见，侧重建设性建议",
            "medium": "客观指出问题，平衡批评与建议",
            "high": "严厉批评，重点找问题",
            "extreme": "极度苛刻，鸡蛋里挑骨头"
        }
        
        context_type_desc = {
            "code": "代码",
            "text": "文案/文档",
            "plan": "计划/方案",
            "design": "设计",
            "general": "一般内容"
        }
        
        prompt = f"""请审查以下{context_type_desc.get(context_type, '内容')}，反对强度：{intensity_desc.get(intensity, '正常')}

待审查内容：
```
{content}
```
"""
        
        # 添加上下文
        if conversation_context:
            prompt += "\n\n对话上下文：\n"
            for msg in conversation_context[-5:]:  # 最近5条
                role = msg.get("role", "user")
                text = msg.get("content", "")
                prompt += f"{role}: {text[:200]}...\n"
        
        prompt += """

请按以下格式输出：

## 开场白
以魏征的身份说一句话

## 问题清单
1. **[严重程度] 问题标题**
   - 问题描述
   - 影响分析
   - 改进建议

## 总结评价
总体评估和改进优先级
"""
        
        return prompt
    
    def _call_api(self, prompt: str) -> str:
        """调用LLM API"""
        if not self.config.api_key:
            return self._mock_response(prompt)
        
        try:
            if self.config.provider == LLMProvider.OPENAI:
                return self._call_openai(prompt)
            elif self.config.provider == LLMProvider.MOONSHOT:
                return self._call_moonshot(prompt)
            elif self.config.provider == LLMProvider.ANTHROPIC:
                return self._call_anthropic(prompt)
            else:
                return self._call_openai_compatible(prompt)
        except Exception as e:
            print(f"[LLM] API调用失败: {e}")
            return self._mock_response(prompt)
    
    def _call_openai(self, prompt: str) -> str:
        """调用OpenAI API"""
        url = self.config.base_url or "https://api.openai.com/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": self.config.system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    def _call_moonshot(self, prompt: str) -> str:
        """调用Moonshot (Kimi) API"""
        url = "https://api.moonshot.cn/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.config.model or "moonshot-v1-8k",
            "messages": [
                {"role": "system", "content": self.config.system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": self.config.temperature,
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    def _call_anthropic(self, prompt: str) -> str:
        """调用Anthropic (Claude) API"""
        url = "https://api.anthropic.com/v1/messages"
        
        headers = {
            "x-api-key": self.config.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": self.config.model or "claude-3-sonnet-20240229",
            "max_tokens": self.config.max_tokens,
            "system": self.config.system_prompt,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        return result["content"][0]["text"]
    
    def _call_openai_compatible(self, prompt: str) -> str:
        """调用兼容OpenAI格式的API"""
        url = f"{self.config.base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": self.config.system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": self.config.temperature,
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    def _mock_response(self, prompt: str) -> str:
        """模拟响应（无API密钥时使用）"""
        return """## 开场白
陛下，恕臣直言，此内容臣不敢苟同！

## 问题清单
1. **[MAJOR] 逻辑不够严密**
   - 问题描述：此方案存在明显的逻辑漏洞，条件判断不够周全
   - 影响分析：可能导致运行时错误或不符合预期的结果
   - 改进建议：增加边界条件检查，完善逻辑分支

2. **[MINOR] 可读性有待提高**
   - 问题描述：命名不够清晰，缺乏必要的注释
   - 影响分析：维护成本增加，团队协作困难
   - 改进建议：使用有意义的命名，添加关键注释

## 总结评价
此内容尚可，但需改进上述问题后方可使用。望陛下三思！"""
    
    def _parse_critique_response(self, response: str, intensity: str) -> Dict[str, Any]:
        """解析批判响应"""
        import re
        
        critics = []
        
        # 简单的解析逻辑
        lines = response.split('\n')
        current_critic = None
        
        for line in lines:
            # 查找问题项
            match = re.match(r'\d+\.\s*\[(\w+)\]\s*(.+)', line)
            if match:
                if current_critic:
                    critics.append(current_critic)
                current_critic = {
                    "severity": match.group(1).lower(),
                    "title": match.group(2).strip(),
                    "critique": "",
                    "suggestion": ""
                }
            elif current_critic and line.strip().startswith('-'):
                if '建议' in line or '改进' in line:
                    current_critic["suggestion"] += line.strip('- ') + ' '
                else:
                    current_critic["critique"] += line.strip('- ') + ' '
        
        if current_critic:
            critics.append(current_critic)
        
        # 生成开场白
        opening = "陛下，恕臣直言！"
        for line in lines[:5]:
            if '开场' in line or '陛下' in line or '臣' in line:
                opening = line.strip('# -').strip()
                break
        
        return {
            "triggered": True,
            "intensity": intensity,
            "agent_personality": opening,
            "critics": critics,
            "summary": f"发现 {len(critics)} 个问题，请查看详细意见。",
            "raw_response": response
        }


def get_llm_client() -> LLMClient:
    """获取全局LLM客户端"""
    return LLMClient()
