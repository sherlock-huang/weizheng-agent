"""提示词模板模块"""

from .templates import (
    get_system_prompt,
    get_critic_prompt,
    get_summary_prompt,
    CRITIC_TEMPLATES,
    PERSONALITY_QUOTES,
)

__all__ = [
    "get_system_prompt",
    "get_critic_prompt",
    "get_summary_prompt",
    "CRITIC_TEMPLATES",
    "PERSONALITY_QUOTES",
]
