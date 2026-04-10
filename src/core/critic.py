"""
批判逻辑引擎

负责生成批判意见的核心逻辑，包括：
1. 内容类型识别
2. 问题检测
3. 批判意见生成
4. 建设性建议生成
"""

import os
import json
import re
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime


class CriticIntensity(Enum):
    """反对强度等级"""
    LOW = "low"           # 温和提意见，侧重建议
    MEDIUM = "medium"     # 正常挑毛病，平衡批评与建议
    HIGH = "high"         # 严厉批评，重点找问题
    EXTREME = "extreme"   # 极度苛刻，鸡蛋里挑骨头


class CriticType(Enum):
    """批判类型"""
    LOGIC = "logic"           # 逻辑问题
    COMPLETENESS = "complete" # 完整性问题
    CLARITY = "clarity"       # 清晰度问题
    RISK = "risk"             # 风险问题
    EFFICIENCY = "efficiency" # 效率问题
    MAINTAINABILITY = "maintain"  # 可维护性问题
    SECURITY = "security"     # 安全问题
    CONSISTENCY = "consistency"   # 一致性问题
    EDGE_CASE = "edge_case"   # 边界情况
    BEST_PRACTICE = "best_practice"  # 最佳实践
    USABILITY = "usability"   # 可用性问题


class CriticEngine:
    """
    批判引擎 - 生成批判意见的核心
    
    设计原则：
    1. 系统性：从不同维度审视内容
    2. 可学习：从历史反馈中学习
    3. 可配置：根据强度调整批判力度
    """
    
    # 批判检查点 - 针对不同内容类型的检查项
    CHECKPOINTS = {
        "code": {
            CriticType.LOGIC: [
                "是否存在逻辑漏洞或条件判断不周全",
                "是否有死代码或不可达代码",
                "循环和递归是否有终止条件",
            ],
            CriticType.COMPLETENESS: [
                "是否处理了所有错误情况",
                "是否有必要的输入验证",
                "是否缺少关键功能实现",
            ],
            CriticType.CLARITY: [
                "命名是否清晰易懂",
                "代码结构是否清晰",
                "注释是否充分且准确",
            ],
            CriticType.EFFICIENCY: [
                "是否存在性能瓶颈",
                "算法复杂度是否可以优化",
                "是否有重复计算",
            ],
            CriticType.SECURITY: [
                "是否存在注入漏洞",
                "敏感数据是否安全处理",
                "是否有权限控制",
            ],
            CriticType.EDGE_CASE: [
                "空值和边界值是否处理",
                "极端输入是否安全",
                "并发场景是否考虑",
            ],
        },
        "text": {
            CriticType.CLARITY: [
                "表达是否清晰易懂",
                "是否存在歧义表述",
                "结构是否逻辑清晰",
            ],
            CriticType.COMPLETENESS: [
                "关键信息是否缺失",
                "背景说明是否充分",
                "结论是否有充分支撑",
            ],
            CriticType.CONSISTENCY: [
                "前后表述是否一致",
                "术语使用是否统一",
                "格式是否规范一致",
            ],
        },
        "plan": {
            CriticType.COMPLETENESS: [
                "是否考虑了所有必要环节",
                "资源需求是否评估充分",
                "依赖关系是否梳理清楚",
            ],
            CriticType.RISK: [
                "风险识别是否全面",
                "应急预案是否完备",
                "是否有Plan B",
            ],
            CriticType.LOGIC: [
                "时间安排是否合理",
                "里程碑设置是否科学",
                "执行顺序是否最优",
            ],
            CriticType.EFFICIENCY: [
                "资源利用是否高效",
                "是否有冗余步骤",
                "并行可能性是否考虑",
            ],
        },
        "design": {
            CriticType.CONSISTENCY: [
                "设计规范是否统一",
                "交互逻辑是否一致",
                "视觉风格是否协调",
            ],
            CriticType.COMPLETENESS: [
                "是否覆盖所有场景",
                "异常状态是否设计",
                "空状态和加载状态",
            ],
            CriticType.USABILITY: [
                "用户体验是否流畅",
                "操作反馈是否清晰",
                "学习成本是否过高",
            ],
        },
        "general": {
            CriticType.LOGIC: ["逻辑是否严密"],
            CriticType.COMPLETENESS: ["是否完整全面"],
            CriticType.CLARITY: ["是否清晰易懂"],
            CriticType.RISK: ["是否存在风险"],
        }
    }
    
    # 批判强度修饰符
    INTENSITY_MODIFIERS = {
        CriticIntensity.LOW: {
            "prefix": ["或许", "可能", "也许", "可以考虑"],
            "severity_bias": {"critical": 0.05, "major": 0.15, "minor": 0.4, "suggestion": 0.4},
            "tone": "温和"
        },
        CriticIntensity.MEDIUM: {
            "prefix": ["", "值得注意的是", "需要关注"],
            "severity_bias": {"critical": 0.15, "major": 0.3, "minor": 0.35, "suggestion": 0.2},
            "tone": "客观"
        },
        CriticIntensity.HIGH: {
            "prefix": ["明显", "严重", "必须解决"],
            "severity_bias": {"critical": 0.3, "major": 0.4, "minor": 0.25, "suggestion": 0.05},
            "tone": "严厉"
        },
        CriticIntensity.EXTREME: {
            "prefix": ["极其严重", "不可接受", "致命"],
            "severity_bias": {"critical": 0.5, "major": 0.35, "minor": 0.1, "suggestion": 0.05},
            "tone": "苛刻"
        }
    }
    
    def __init__(self, intensity: CriticIntensity = CriticIntensity.MEDIUM):
        self.intensity = intensity
        self.modifier = self.INTENSITY_MODIFIERS[intensity]
        self.feedback_history = []
    
    def set_intensity(self, intensity: CriticIntensity):
        """设置批判强度"""
        self.intensity = intensity
        self.modifier = self.INTENSITY_MODIFIERS[intensity]
    
    def generate_critics(
        self,
        content: str,
        content_type: str,
        context: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        生成批判意见列表
        
        Args:
            content: 待批判的内容
            content_type: 内容类型
            context: 上下文信息
        
        Returns:
            批判意见列表
        """
        critics = []
        checkpoints = self.CHECKPOINTS.get(content_type, self.CHECKPOINTS["general"])
        
        # 根据强度决定检查深度
        check_depth = {
            CriticIntensity.LOW: 0.3,
            CriticIntensity.MEDIUM: 0.6,
            CriticIntensity.HIGH: 0.9,
            CriticIntensity.EXTREME: 1.0
        }.get(self.intensity, 0.6)
        
        # 模拟检查过程（实际实现中会有更复杂的逻辑）
        for critic_type, checks in checkpoints.items():
            for check in checks:
                # 模拟发现问题（实际应基于AI分析）
                if self._should_flag_issue(content, check, context):
                    critic = self._create_critic(critic_type, check, content, context)
                    if critic:
                        critics.append(critic)
        
        # 根据强度过滤严重程度
        critics = self._filter_by_intensity(critics)
        
        # 排序：严重问题在前
        critics.sort(key=lambda x: ["critical", "major", "minor", "suggestion"].index(x.get("severity", "minor")))
        
        return critics
    
    def _should_flag_issue(
        self,
        content: str,
        check: str,
        context: Optional[Dict]
    ) -> bool:
        """
        判断是否应标记为问题
        
        这里是一个简化的模拟，实际应调用AI模型进行分析
        """
        # 基于内容特征和检查项进行启发式判断
        # 实际实现中会使用LLM进行深度分析
        
        import random
        # 模拟发现问题概率，实际应由AI判断
        base_prob = 0.3
        if self.intensity == CriticIntensity.HIGH:
            base_prob = 0.5
        elif self.intensity == CriticIntensity.EXTREME:
            base_prob = 0.7
        
        return random.random() < base_prob
    
    def _create_critic(
        self,
        critic_type: CriticType,
        check: str,
        content: str,
        context: Optional[Dict]
    ) -> Optional[Dict[str, Any]]:
        """创建单个批判意见"""
        # 根据强度分配严重程度
        severity = self._assign_severity()
        
        # 生成批判文本
        critique_text = self._generate_critique_text(critic_type, check, severity)
        
        # 生成建议
        suggestion = self._generate_suggestion(critic_type, check)
        
        return {
            "type": critic_type.value,
            "severity": severity,
            "title": check,
            "critique": critique_text,
            "suggestion": suggestion,
            "timestamp": datetime.now().isoformat(),
        }
    
    def _assign_severity(self) -> str:
        """根据强度设置分配严重程度"""
        import random
        bias = self.modifier["severity_bias"]
        roll = random.random()
        
        cumulative = 0
        for severity, prob in bias.items():
            cumulative += prob
            if roll <= cumulative:
                return severity
        return "minor"
    
    def _generate_critique_text(
        self,
        critic_type: CriticType,
        check: str,
        severity: str
    ) -> str:
        """生成批判文本"""
        prefixes = self.modifier["prefix"]
        prefix = prefixes[hash(check) % len(prefixes)] if prefixes else ""
        
        # 根据类型和严重程度生成批判语
        templates = {
            "critical": [
                f"{prefix}存在{critic_type.value}问题：{check}，这可能导致严重后果。",
                f"{prefix}此处{critic_type.value}缺陷明显：{check}。",
            ],
            "major": [
                f"{prefix}发现{critic_type.value}问题：{check}，建议改进。",
                f"{prefix}{check}方面存在不足。",
            ],
            "minor": [
                f"{prefix}{check}可以进一步优化。",
                f"{prefix}建议关注{check}。",
            ],
            "suggestion": [
                f"{prefix}可以考虑{check}。",
                f"{prefix}{check}或许有改进空间。",
            ]
        }
        
        import random
        return random.choice(templates.get(severity, templates["minor"]))
    
    def _generate_suggestion(self, critic_type: CriticType, check: str) -> str:
        """生成改进建议"""
        suggestions = {
            CriticType.LOGIC: "重新审视逻辑流程，考虑各种边界条件。",
            CriticType.COMPLETENESS: "补充缺失的部分，确保覆盖所有场景。",
            CriticType.CLARITY: "简化表达，使用更清晰的结构和命名。",
            CriticType.RISK: "制定风险应对预案，建立监控机制。",
            CriticType.EFFICIENCY: "优化算法或流程，减少不必要的开销。",
            CriticType.MAINTAINABILITY: "增加文档和注释，降低维护成本。",
            CriticType.SECURITY: "加强安全审查，遵循安全最佳实践。",
            CriticType.CONSISTENCY: "统一规范和风格，建立一致性检查。",
            CriticType.EDGE_CASE: "增加边界测试，处理异常情况。",
            CriticType.BEST_PRACTICE: "参考行业标准，采用最佳实践。",
        }
        return suggestions.get(critic_type, "请根据实际情况改进。")
    
    def _filter_by_intensity(self, critics: List[Dict]) -> List[Dict]:
        """根据强度过滤批判意见"""
        if self.intensity == CriticIntensity.LOW:
            # 低强度：只保留严重的和随机保留一些轻微的
            return [c for c in critics if c["severity"] in ["critical", "major"] or hash(c["title"]) % 2 == 0]
        elif self.intensity == CriticIntensity.EXTREME:
            # 极端：放大问题数量
            return critics  # 保留所有，并可能在后期生成更多
        return critics
    
    def learn_from_feedback(self, critic_id: str, was_accurate: bool, user_feedback: str):
        """从反馈中学习"""
        self.feedback_history.append({
            "critic_id": critic_id,
            "was_accurate": was_accurate,
            "feedback": user_feedback,
            "timestamp": datetime.now().isoformat()
        })
