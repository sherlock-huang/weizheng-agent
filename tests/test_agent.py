"""
魏征 Agent 测试
"""

import unittest
import tempfile
import shutil
from pathlib import Path

from src.core.agent import WeizhengAgent, CriticIntensity, TriggerPattern


class TestTriggerPattern(unittest.TestCase):
    """测试触发词模式"""
    
    def test_chinese_triggers(self):
        """测试中文触发词"""
        triggers = [
            "魏征，你怎么看？",
            "魏征，有何高见？",
            "魏征，说说你的看法",
            "魏征，点评一下",
            "魏征，挑挑毛病",
            "@魏征",
        ]
        for trigger in triggers:
            self.assertTrue(TriggerPattern.is_triggered(trigger), f"应触发: {trigger}")
    
    def test_english_triggers(self):
        """测试英文触发词"""
        triggers = [
            "weizheng, what do you think?",
            "@weizheng",
        ]
        for trigger in triggers:
            self.assertTrue(TriggerPattern.is_triggered(trigger), f"应触发: {trigger}")
    
    def test_non_triggers(self):
        """测试非触发内容"""
        non_triggers = [
            "你好",
            "今天天气不错",
            "帮我写代码",
            "魏征是谁",
        ]
        for text in non_triggers:
            self.assertFalse(TriggerPattern.is_triggered(text), f"不应触发: {text}")


class TestWeizhengAgent(unittest.TestCase):
    """测试魏征Agent"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.agent = WeizhengAgent(
            intensity=CriticIntensity.MEDIUM,
            memory_path=self.temp_dir
        )
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.agent.intensity, CriticIntensity.MEDIUM)
        self.assertIsNotNone(self.agent.memory)
        self.assertIsNotNone(self.agent.critic_engine)
    
    def test_process(self):
        """测试处理内容"""
        content = "这是一个测试内容"
        result = self.agent.process(content, context_type="text")
        
        self.assertIn("triggered", result)
        self.assertIn("intensity", result)
        self.assertIn("critics", result)
        self.assertIn("summary", result)
        self.assertIn("agent_personality", result)
    
    def test_intensity_setting(self):
        """测试强度设置"""
        self.agent.set_intensity(CriticIntensity.HIGH)
        self.assertEqual(self.agent.intensity, CriticIntensity.HIGH)
        
        self.agent.set_intensity("low")
        self.assertEqual(self.agent.intensity, CriticIntensity.LOW)
    
    def test_stats(self):
        """测试统计信息"""
        stats = self.agent.get_stats()
        self.assertIn("conversation_count", stats)
        self.assertIn("total_critics_made", stats)
        self.assertIn("current_intensity", stats)


class TestMemory(unittest.TestCase):
    """测试记忆功能"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.agent = WeizhengAgent(memory_path=self.temp_dir)
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir)
    
    def test_conversation_saved(self):
        """测试对话是否被保存"""
        self.agent.process("测试内容", context_type="text")
        
        # 检查记忆目录是否有文件
        memory_path = Path(self.temp_dir)
        conversations = list(memory_path.glob("conversations/**/*.json"))
        self.assertGreater(len(conversations), 0, "应有对话记录被保存")
    
    def test_stats_updated(self):
        """测试统计是否更新"""
        initial_count = self.agent.conversation_count
        self.agent.process("测试内容", context_type="text")
        self.assertEqual(self.agent.conversation_count, initial_count + 1)


if __name__ == "__main__":
    unittest.main()
