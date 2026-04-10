"""
记忆管理模块

负责：
1. 对话历史存储
2. 反馈记录
3. 洞察积累
4. 与其他Agent共享记忆空间
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path


class MemoryManager:
    """
    记忆管理器
    
    设计原则：
    1. 共享性：与其他Agent共享工作空间
    2. 持久性：记忆长期保存，不断积累
    3. 可检索：支持高效的回忆和关联
    4. 隐私性：敏感信息妥善处理
    """
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.conversations_path = self.base_path / "conversations"
        self.feedback_path = self.base_path / "feedback"
        self.insights_path = self.base_path / "insights"
        
        # 确保目录存在
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保所有记忆目录存在"""
        for path in [self.conversations_path, self.feedback_path, self.insights_path]:
            path.mkdir(parents=True, exist_ok=True)
    
    def save_conversation(
        self,
        content: str,
        context_type: str,
        critics: List[Dict],
        triggered: bool = True
    ) -> str:
        """
        保存对话记录
        
        Args:
            content: 原始内容
            context_type: 内容类型
            critics: 生成的批判意见
            triggered: 是否由触发词触发
        
        Returns:
            对话ID
        """
        conversation_id = self._generate_id(content)
        timestamp = datetime.now()
        
        conversation_data = {
            "id": conversation_id,
            "timestamp": timestamp.isoformat(),
            "content_preview": content[:500] if len(content) > 500 else content,
            "content_hash": hashlib.sha256(content.encode()).hexdigest()[:16],
            "context_type": context_type,
            "triggered": triggered,
            "critics_count": len(critics),
            "critics": critics,
        }
        
        # 按日期组织文件
        date_str = timestamp.strftime("%Y-%m")
        date_dir = self.conversations_path / date_str
        date_dir.mkdir(exist_ok=True)
        
        file_path = date_dir / f"{conversation_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(conversation_data, f, ensure_ascii=False, indent=2)
        
        # 更新索引
        self._update_index(conversation_id, timestamp, context_type)
        
        return conversation_id
    
    def _generate_id(self, content: str) -> str:
        """生成唯一ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:8]
        return f"{timestamp}_{content_hash}"
    
    def _update_index(self, conversation_id: str, timestamp: datetime, context_type: str):
        """更新对话索引"""
        index_file = self.conversations_path / "index.json"
        
        index = {}
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                index = json.load(f)
        
        index[conversation_id] = {
            "timestamp": timestamp.isoformat(),
            "context_type": context_type,
        }
        
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """获取特定对话记录"""
        # 从索引中查找日期
        index_file = self.conversations_path / "index.json"
        if not index_file.exists():
            return None
        
        with open(index_file, 'r', encoding='utf-8') as f:
            index = json.load(f)
        
        if conversation_id not in index:
            return None
        
        timestamp = datetime.fromisoformat(index[conversation_id]["timestamp"])
        date_str = timestamp.strftime("%Y-%m")
        file_path = self.conversations_path / date_str / f"{conversation_id}.json"
        
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def get_recent_conversations(
        self,
        days: int = 7,
        context_type: Optional[str] = None
    ) -> List[Dict]:
        """获取最近的对话记录"""
        conversations = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        index_file = self.conversations_path / "index.json"
        if not index_file.exists():
            return conversations
        
        with open(index_file, 'r', encoding='utf-8') as f:
            index = json.load(f)
        
        for conv_id, info in index.items():
            timestamp = datetime.fromisoformat(info["timestamp"])
            if timestamp < cutoff_date:
                continue
            
            if context_type and info.get("context_type") != context_type:
                continue
            
            conv = self.get_conversation(conv_id)
            if conv:
                conversations.append(conv)
        
        return sorted(conversations, key=lambda x: x["timestamp"], reverse=True)
    
    def save_feedback(
        self,
        conversation_id: str,
        feedback_type: str,
        feedback_content: str,
        accuracy_rating: Optional[int] = None
    ):
        """
        保存用户反馈
        
        Args:
            conversation_id: 关联的对话ID
            feedback_type: 反馈类型（accurate/inaccurate/helpful/unhelpful）
            feedback_content: 反馈内容
            accuracy_rating: 准确性评分（1-5）
        """
        feedback_data = {
            "conversation_id": conversation_id,
            "timestamp": datetime.now().isoformat(),
            "feedback_type": feedback_type,
            "feedback_content": feedback_content,
            "accuracy_rating": accuracy_rating,
        }
        
        # 按日期组织
        date_str = datetime.now().strftime("%Y-%m-%d")
        feedback_file = self.feedback_path / f"{date_str}.jsonl"
        
        with open(feedback_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(feedback_data, ensure_ascii=False) + '\n')
        
        # 尝试生成洞察
        self._try_generate_insight(feedback_data)
    
    def _try_generate_insight(self, feedback_data: Dict):
        """尝试从反馈中生成洞察"""
        # 简化实现：累积一定数量反馈后生成洞察
        # 实际实现可能使用更复杂的分析
        pass
    
    def add_insight(self, insight: Dict[str, Any]):
        """
        添加洞察
        
        洞察是基于历史经验总结出的规律
        """
        insight_data = {
            "id": self._generate_id(json.dumps(insight, sort_keys=True)),
            "timestamp": datetime.now().isoformat(),
            "insight": insight,
            "source": insight.get("source", "analysis"),
            "confidence": insight.get("confidence", 0.5),
        }
        
        insight_file = self.insights_path / f"{insight_data['id']}.json"
        with open(insight_file, 'w', encoding='utf-8') as f:
            json.dump(insight_data, f, ensure_ascii=False, indent=2)
    
    def get_insights(
        self,
        context_type: Optional[str] = None,
        min_confidence: float = 0.0
    ) -> List[Dict]:
        """获取洞察列表"""
        insights = []
        
        for insight_file in self.insights_path.glob("*.json"):
            with open(insight_file, 'r', encoding='utf-8') as f:
                insight = json.load(f)
            
            if insight.get("confidence", 0) < min_confidence:
                continue
            
            if context_type and insight.get("insight", {}).get("context_type") != context_type:
                continue
            
            insights.append(insight)
        
        return sorted(insights, key=lambda x: x.get("confidence", 0), reverse=True)
    
    def get_related_memories(self, content: str, limit: int = 5) -> List[Dict]:
        """
        获取相关记忆
        
        基于内容相似度检索相关历史记录
        """
        # 简化实现：基于关键词匹配
        # 实际实现可能使用向量相似度
        
        keywords = set(content.lower().split())
        related = []
        
        for conv_file in self.conversations_path.rglob("*.json"):
            if conv_file.name == "index.json":
                continue
            
            with open(conv_file, 'r', encoding='utf-8') as f:
                conv = json.load(f)
            
            conv_text = conv.get("content_preview", "").lower()
            conv_keywords = set(conv_text.split())
            
            # 计算Jaccard相似度
            intersection = keywords & conv_keywords
            union = keywords | conv_keywords
            similarity = len(intersection) / len(union) if union else 0
            
            if similarity > 0.1:  # 阈值
                related.append((similarity, conv))
        
        # 按相似度排序
        related.sort(key=lambda x: x[0], reverse=True)
        return [r[1] for r in related[:limit]]
    
    def get_stats(self) -> Dict[str, Any]:
        """获取记忆统计信息"""
        stats = {
            "total_conversations": 0,
            "total_feedback": 0,
            "total_insights": 0,
            "context_type_distribution": {},
        }
        
        # 统计对话
        index_file = self.conversations_path / "index.json"
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                index = json.load(f)
            stats["total_conversations"] = len(index)
            
            for info in index.values():
                ct = info.get("context_type", "unknown")
                stats["context_type_distribution"][ct] = \
                    stats["context_type_distribution"].get(ct, 0) + 1
        
        # 统计反馈
        for feedback_file in self.feedback_path.glob("*.jsonl"):
            with open(feedback_file, 'r', encoding='utf-8') as f:
                stats["total_feedback"] += sum(1 for _ in f)
        
        # 统计洞察
        stats["total_insights"] = len(list(self.insights_path.glob("*.json")))
        
        return stats
    
    def export_memory(self, output_path: str):
        """导出所有记忆数据"""
        export_data = {
            "export_time": datetime.now().isoformat(),
            "stats": self.get_stats(),
            "conversations": [],
            "insights": self.get_insights(),
        }
        
        # 收集所有对话
        for conv_file in self.conversations_path.rglob("*.json"):
            if conv_file.name == "index.json":
                continue
            with open(conv_file, 'r', encoding='utf-8') as f:
                export_data["conversations"].append(json.load(f))
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    def import_memory(self, input_path: str):
        """导入记忆数据"""
        with open(input_path, 'r', encoding='utf-8') as f:
            import_data = json.load(f)
        
        # 导入对话
        for conv in import_data.get("conversations", []):
            conv_id = conv.get("id")
            if conv_id:
                timestamp = datetime.fromisoformat(conv.get("timestamp", datetime.now().isoformat()))
                date_str = timestamp.strftime("%Y-%m")
                date_dir = self.conversations_path / date_str
                date_dir.mkdir(exist_ok=True)
                
                file_path = date_dir / f"{conv_id}.json"
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(conv, f, ensure_ascii=False, indent=2)
                
                self._update_index(conv_id, timestamp, conv.get("context_type", "general"))
        
        # 导入洞察
        for insight in import_data.get("insights", []):
            self.add_insight(insight.get("insight", {}))
