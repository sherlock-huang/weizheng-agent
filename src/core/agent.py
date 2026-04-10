"""
魏征 Agent 主类

设计理念：
1. 独立性：完全独立于其他Agent，有自己的思考方式和性格
2. 批判性：唯一任务就是挑毛病、提反对意见
3. 学习性：随着经验积累，越来越精准
4. 可控性：用户可以调整反对强度
"""

import os
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from enum import Enum

from .critic import CriticEngine, CriticType, CriticIntensity
from .memory import MemoryManager


class TriggerPattern:
    """触发词模式"""
    PATTERNS = [
        r"魏征[，,]?\s*你怎么看[？?]?",
        r"魏征[，,]?\s*有何高见[？?]?",
        r"魏征[，,]?\s*说说你的看法[？?]?",
        r"魏征[，,]?\s*点评一下[？?]?",
        r"魏征[，,]?\s*挑挑毛病[？?]?",
        r"魏征[，,]?\s*提提意见[？?]?",
        r"weizheng[，,]?\s*what do you think[?]?",
        r"@魏征",
        r"@weizheng",
    ]
    
    @classmethod
    def is_triggered(cls, text: str) -> bool:
        """检查是否触发Agent"""
        text = text.lower().strip()
        for pattern in cls.PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False


class WeizhengAgent:
    """
    魏征 Agent - 专门提反对意见的独立Agent
    
    性格特点：
    - 直言不讳，敢于指出问题
    - 逻辑严密，有理有据
    - 不迎合，不谄媚
    - 随着经验积累，越来越精准
    """
    
    def __init__(
        self,
        intensity: CriticIntensity = CriticIntensity.MEDIUM,
        memory_path: Optional[str] = None
    ):
        """
        初始化魏征Agent
        
        Args:
            intensity: 反对强度（LOW/MEDIUM/HIGH/EXTREME）
            memory_path: 记忆存储路径，默认为项目memory目录
        """
        self.intensity = intensity
        self.critic_engine = CriticEngine(intensity)
        
        # 记忆管理
        if memory_path is None:
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            memory_path = os.path.join(base_path, "memory")
        self.memory = MemoryManager(memory_path)
        
        # Agent状态
        self.conversation_count = 0
        self.total_critics_made = 0
        self._load_stats()
    
    def _load_stats(self):
        """加载统计信息"""
        stats_file = os.path.join(self.memory.base_path, "stats.json")
        if os.path.exists(stats_file):
            with open(stats_file, 'r', encoding='utf-8') as f:
                stats = json.load(f)
                self.conversation_count = stats.get("conversation_count", 0)
                self.total_critics_made = stats.get("total_critics_made", 0)
    
    def _save_stats(self):
        """保存统计信息"""
        stats_file = os.path.join(self.memory.base_path, "stats.json")
        stats = {
            "conversation_count": self.conversation_count,
            "total_critics_made": self.total_critics_made,
            "last_updated": datetime.now().isoformat()
        }
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
    
    def process(self, content: str, context_type: str = "general") -> Dict[str, Any]:
        """
        处理内容并返回批判意见
        
        Args:
            content: 要批判的内容
            context_type: 内容类型（code/text/plan/design/general）
        
        Returns:
            包含批判意见的字典
        """
        # 检查触发词
        triggered = TriggerPattern.is_triggered(content)
        
        # 移除触发词，获取实际内容
        clean_content = self._extract_content(content)
        
        # 分析内容
        analysis = self._analyze_content(clean_content, context_type)
        
        # 生成批判意见
        critics = self.critic_engine.generate_critics(
            content=clean_content,
            content_type=context_type,
            context=analysis
        )
        
        # 保存到记忆
        self.memory.save_conversation(
            content=clean_content,
            context_type=context_type,
            critics=critics,
            triggered=triggered
        )
        
        # 更新统计
        self.conversation_count += 1
        self.total_critics_made += len(critics)
        self._save_stats()
        
        return {
            "triggered": triggered,
            "intensity": self.intensity.value,
            "critics": critics,
            "summary": self._generate_summary(critics),
            "suggestions": self._extract_suggestions(critics),
            "agent_personality": self._get_personality_quote()
        }
    
    def _extract_content(self, text: str) -> str:
        """从触发语句中提取实际内容"""
        # 移除触发词
        for pattern in TriggerPattern.PATTERNS:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)
        return text.strip()
    
    def _analyze_content(self, content: str, context_type: str) -> Dict[str, Any]:
        """分析内容特征"""
        analysis = {
            "length": len(content),
            "line_count": len(content.split('\n')),
            "content_type": context_type,
            "timestamp": datetime.now().isoformat(),
            "has_code_blocks": '```' in content or '`' in content,
            "has_lists": bool(re.search(r'^[\s]*[-*+][\s]', content, re.MULTILINE)),
        }
        
        # 根据类型进行特定分析
        if context_type == "code":
            analysis.update(self._analyze_code(content))
        elif context_type == "plan":
            analysis.update(self._analyze_plan(content))
        elif context_type == "text":
            analysis.update(self._analyze_text(content))
        
        return analysis
    
    def _analyze_code(self, content: str) -> Dict[str, Any]:
        """分析代码内容"""
        return {
            "has_comments": '#' in content or '//' in content or '/*' in content,
            "function_count": len(re.findall(r'(def |function |func )', content)),
            "class_count": len(re.findall(r'(class |struct |interface )', content)),
            "import_count": len(re.findall(r'(import |from |require|include)', content)),
        }
    
    def _analyze_plan(self, content: str) -> Dict[str, Any]:
        """分析计划内容"""
        return {
            "has_timeline": bool(re.search(r'(\d+[dwmy]|week|day|month|timeline|schedule)', content, re.I)),
            "has_risk_analysis": bool(re.search(r'(risk|风险|问题|issue|concern)', content, re.I)),
            "has_milestones": bool(re.search(r'(milestone|里程碑|阶段|phase)', content, re.I)),
            "step_count": len(re.findall(r'^\s*\d+[.、]', content, re.MULTILINE)),
        }
    
    def _analyze_text(self, content: str) -> Dict[str, Any]:
        """分析文本内容"""
        return {
            "word_count": len(content.split()),
            "has_structure": bool(re.search(r'^(#{1,6}|【|\[)', content, re.MULTILINE)),
            "paragraph_count": len([p for p in content.split('\n\n') if p.strip()]),
        }
    
    def _generate_summary(self, critics: List[Dict]) -> str:
        """生成批判总结"""
        if not critics:
            return "暂时未发现明显问题，但保持警惕。"
        
        severity_counts = {"critical": 0, "major": 0, "minor": 0, "suggestion": 0}
        for c in critics:
            severity_counts[c.get("severity", "minor")] += 1
        
        summary_parts = []
        if severity_counts["critical"] > 0:
            summary_parts.append(f"发现 {severity_counts['critical']} 个关键问题")
        if severity_counts["major"] > 0:
            summary_parts.append(f"发现 {severity_counts['major']} 个重要问题")
        if severity_counts["minor"] > 0:
            summary_parts.append(f"发现 {severity_counts['minor']} 个小问题")
        if severity_counts["suggestion"] > 0:
            summary_parts.append(f"提出 {severity_counts['suggestion']} 条改进建议")
        
        return "；".join(summary_parts) + "。"
    
    def _extract_suggestions(self, critics: List[Dict]) -> List[str]:
        """提取建设性建议"""
        suggestions = []
        for critic in critics:
            if "suggestion" in critic and critic["suggestion"]:
                suggestions.append(critic["suggestion"])
        return suggestions
    
    def _get_personality_quote(self) -> str:
        """获取符合当前强度的性格语录"""
        quotes = {
            CriticIntensity.LOW: [
                "臣有一言，不知当讲不当讲...",
                "此事尚可，但臣以为仍有改进之处...",
                "陛下圣明，然臣斗胆进言...",
            ],
            CriticIntensity.MEDIUM: [
                "臣以为，此事有三处不妥...",
                "陛下，恕臣直言，这其中有问题...",
                "臣不敢苟同，且听臣一一道来...",
            ],
            CriticIntensity.HIGH: [
                "陛下！此事万万不可！",
                "臣冒死进谏，此方案漏洞百出！",
                "若依此行事，必有大患！",
            ],
            CriticIntensity.EXTREME: [
                "荒谬！此等方案怎堪一用！",
                "陛下昏聩！此计断不可行！",
                "臣以项上人头担保，此路不通！",
            ]
        }
        import random
        return random.choice(quotes.get(self.intensity, quotes[CriticIntensity.MEDIUM]))
    
    def set_intensity(self, intensity: Union[str, CriticIntensity]):
        """设置反对强度"""
        if isinstance(intensity, str):
            intensity = CriticIntensity(intensity.upper())
        self.intensity = intensity
        self.critic_engine.set_intensity(intensity)
    
    def get_insights(self) -> List[Dict[str, Any]]:
        """获取积累的洞察"""
        return self.memory.get_insights()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取Agent统计信息"""
        return {
            "conversation_count": self.conversation_count,
            "total_critics_made": self.total_critics_made,
            "current_intensity": self.intensity.value,
            "insights_count": len(self.get_insights()),
            "memory_path": self.memory.base_path
        }
