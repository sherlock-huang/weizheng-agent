"""
魏征 Agent - 专门提反对意见、挑毛病的独立Agent

这个Agent的设计理念：
- 独立于其他Agent（OpenClaw, Claude Code, Codex, Kimi Code等）
- 但共享记忆工作空间
- 专门负责提反对意见、找问题、挑毛病
- 支持可配置的反对强度
- 随着经验积累，提意见越来越精准

触发词："魏征，你怎么看？"
"""

__version__ = "0.1.0"
__author__ = "Weizheng Agent"
