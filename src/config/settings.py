"""
配置设置

管理魏征Agent的所有配置项
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict, field


@dataclass
class Settings:
    """
    魏征Agent配置类
    
    包含所有可配置项，支持从环境变量和配置文件加载
    """
    
    # 基础配置
    agent_name: str = "魏征"
    agent_name_en: str = "Weizheng"
    version: str = "0.1.0"
    
    # 批判强度 (low/medium/high/extreme)
    default_intensity: str = "medium"
    
    # 路径配置
    memory_path: str = field(default_factory=lambda: str(Path(__file__).parent.parent.parent / "memory"))
    config_path: str = field(default_factory=lambda: str(Path(__file__).parent.parent.parent / "config"))
    
    # 触发词配置
    trigger_words: list = field(default_factory=lambda: [
        "魏征，你怎么看",
        "魏征，有何高见",
        "魏征，说说你的看法",
        "魏征，点评一下",
        "魏征，挑挑毛病",
        "魏征，提提意见",
        "weizheng, what do you think",
        "@魏征",
        "@weizheng",
    ])
    
    # 记忆配置
    max_conversation_history: int = 1000  # 最大保存对话数
    memory_retention_days: int = 365  # 记忆保留天数
    enable_memory_compression: bool = True  # 启用记忆压缩
    
    # 学习配置
    enable_learning: bool = True  # 启用学习
    feedback_threshold_for_insight: int = 5  # 生成洞察所需的最小反馈数
    min_confidence_for_insight: float = 0.6  # 洞察最小置信度
    
    # 输出配置
    output_language: str = "zh"  # 输出语言 (zh/en)
    max_critics_per_response: int = 10  # 单次最多批判数
    include_suggestions: bool = True  # 是否包含建议
    include_code_examples: bool = True  # 是否包含代码示例
    
    # 集成配置
    enable_mcp: bool = False  # 启用MCP集成
    mcp_server_url: Optional[str] = None  # MCP服务器URL
    
    # 日志配置
    log_level: str = "INFO"  # 日志级别
    log_to_file: bool = True  # 是否记录到文件
    log_path: str = field(default_factory=lambda: str(Path(__file__).parent.parent.parent / "logs"))
    
    # 高级配置
    enable_vector_search: bool = False  # 启用向量搜索（需要额外依赖）
    similarity_threshold: float = 0.7  # 相似度阈值
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    def to_json(self, indent: int = 2) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Settings":
        """从字典创建"""
        # 过滤掉不存在的字段
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)
    
    @classmethod
    def from_json(cls, json_str: str) -> "Settings":
        """从JSON字符串创建"""
        return cls.from_dict(json.loads(json_str))
    
    @classmethod
    def from_file(cls, path: str) -> "Settings":
        """从配置文件加载"""
        with open(path, 'r', encoding='utf-8') as f:
            if path.endswith('.json'):
                return cls.from_dict(json.load(f))
            else:
                # 简单的key=value格式
                config = {}
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip().strip('"\'')
                return cls.from_dict(config)
    
    def save_to_file(self, path: str):
        """保存到配置文件"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            if path.endswith('.json'):
                f.write(self.to_json())
            else:
                for key, value in self.to_dict().items():
                    f.write(f"{key}={value}\n")
    
    def update_from_env(self):
        """从环境变量更新配置"""
        env_mappings = {
            "WEIZHENG_INTENSITY": "default_intensity",
            "WEIZHENG_MEMORY_PATH": "memory_path",
            "WEIZHENG_LOG_LEVEL": "log_level",
            "WEIZHENG_LANGUAGE": "output_language",
            "WEIZHENG_ENABLE_LEARNING": "enable_learning",
            "WEIZHENG_MAX_CRITICS": "max_critics_per_response",
        }
        
        for env_var, config_key in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                # 类型转换
                if config_key in ["enable_learning", "enable_memory_compression", 
                                  "include_suggestions", "include_code_examples",
                                  "log_to_file", "enable_mcp", "enable_vector_search"]:
                    value = value.lower() in ("true", "1", "yes", "on")
                elif config_key in ["max_conversation_history", "memory_retention_days",
                                    "feedback_threshold_for_insight", "max_critics_per_response"]:
                    value = int(value)
                elif config_key in ["min_confidence_for_insight", "similarity_threshold"]:
                    value = float(value)
                
                setattr(self, config_key, value)
    
    def get_memory_path(self, subpath: Optional[str] = None) -> str:
        """获取记忆路径"""
        base = Path(self.memory_path)
        if subpath:
            return str(base / subpath)
        return str(base)
    
    def get_log_path(self) -> str:
        """获取日志路径"""
        return str(Path(self.log_path))


# 全局配置实例
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    获取全局配置实例
    
    首次调用时会加载配置文件和环境变量
    """
    global _settings
    
    if _settings is None:
        _settings = Settings()
        
        # 尝试加载配置文件
        config_paths = [
            os.path.expanduser("~/.weizheng/config.json"),
            os.path.expanduser("~/.weizheng/config"),
            "./config.json",
            "./config",
        ]
        
        for path in config_paths:
            if os.path.exists(path):
                try:
                    _settings = Settings.from_file(path)
                    break
                except Exception:
                    continue
        
        # 从环境变量更新
        _settings.update_from_env()
    
    return _settings


def reload_settings() -> Settings:
    """重新加载配置"""
    global _settings
    _settings = None
    return get_settings()


def create_default_config(path: str):
    """创建默认配置文件"""
    settings = Settings()
    settings.save_to_file(path)
