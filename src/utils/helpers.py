"""
通用工具函数
"""

import re
import hashlib
import uuid
from datetime import datetime
from typing import Optional


def generate_id(content: Optional[str] = None) -> str:
    """
    生成唯一ID
    
    Args:
        content: 可选的内容，用于生成确定性ID
    
    Returns:
        唯一ID字符串
    """
    if content:
        # 基于内容生成确定性ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:8]
        return f"{timestamp}_{content_hash}"
    else:
        # 随机UUID
        return str(uuid.uuid4())[:8]


def format_timestamp(
    timestamp: Optional[datetime] = None,
    format_str: str = "%Y-%m-%d %H:%M:%S"
) -> str:
    """
    格式化时间戳
    
    Args:
        timestamp: 时间对象，默认为当前时间
        format_str: 格式字符串
    
    Returns:
        格式化后的时间字符串
    """
    if timestamp is None:
        timestamp = datetime.now()
    return timestamp.strftime(format_str)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    截断文本
    
    Args:
        text: 原始文本
        max_length: 最大长度
        suffix: 截断后缀
    
    Returns:
        截断后的文本
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def count_tokens_approx(text: str) -> int:
    """
    估算token数量（简化版）
    
    对于中文，大约1个汉字 ≈ 1.5 tokens
    对于英文，大约1个单词 ≈ 1.3 tokens
    
    Args:
        text: 文本内容
    
    Returns:
        估算的token数量
    """
    # 中文字符数
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    # 英文单词数
    english_words = len(re.findall(r'[a-zA-Z]+', text))
    # 其他字符（标点、数字等）
    other_chars = len(text) - chinese_chars - sum(len(w) for w in re.findall(r'[a-zA-Z]+', text))
    
    # 估算
    tokens = chinese_chars * 1.5 + english_words * 1.3 + other_chars * 0.5
    return int(tokens)


def sanitize_filename(filename: str, replacement: str = "_") -> str:
    """
    清理文件名中的非法字符
    
    Args:
        filename: 原始文件名
        replacement: 替换字符
    
    Returns:
        清理后的文件名
    """
    # Windows非法字符: < > : " / \ | ? *
    illegal_chars = '<>:"/\\|?*'
    for char in illegal_chars:
        filename = filename.replace(char, replacement)
    
    # 移除控制字符
    filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
    
    # 限制长度
    if len(filename) > 255:
        name, ext = filename[:250], filename[250:].rsplit('.', 1)[-1] if '.' in filename[250:] else ''
        filename = name + ('.' + ext if ext else '')
    
    # 移除首尾空格和点
    filename = filename.strip('. ')
    
    # 保留不能为空
    if not filename:
        filename = "unnamed"
    
    return filename


def extract_code_blocks(text: str) -> list:
    """
    提取文本中的代码块
    
    Args:
        text: 包含代码块的文本
    
    Returns:
        代码块列表，每个元素是 (language, code) 元组
    """
    pattern = r'```(\w+)?\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    return [(lang or "text", code.strip()) for lang, code in matches]


def estimate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """
    估算阅读时间
    
    Args:
        text: 文本内容
        words_per_minute: 每分钟阅读字数（中文）或单词数（英文）
    
    Returns:
        估算的阅读时间（分钟）
    """
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    english_words = len(re.findall(r'[a-zA-Z]+', text))
    
    # 中文按字数，英文按单词
    total = chinese_chars + english_words
    return max(1, total // words_per_minute)


def calculate_similarity(text1: str, text2: str) -> float:
    """
    计算两段文本的简单相似度（Jaccard系数）
    
    Args:
        text1: 第一段文本
        text2: 第二段文本
    
    Returns:
        相似度分数（0-1）
    """
    # 分词（简化版：按字符）
    set1 = set(text1.lower())
    set2 = set(text2.lower())
    
    intersection = set1 & set2
    union = set1 | set2
    
    if not union:
        return 0.0
    
    return len(intersection) / len(union)


def highlight_differences(old: str, new: str) -> tuple:
    """
    高亮两段文本的差异
    
    Args:
        old: 旧文本
        new: 新文本
    
    Returns:
        (高亮后的旧文本, 高亮后的新文本)
    """
    # 简化实现，实际可以使用difflib
    import difflib
    
    diff = list(difflib.ndiff(old.splitlines(), new.splitlines()))
    
    old_highlighted = []
    new_highlighted = []
    
    for line in diff:
        if line.startswith('- '):
            old_highlighted.append(f"[- {line[2:]}]")
        elif line.startswith('+ '):
            new_highlighted.append(f"[+ {line[2:]}]")
        elif line.startswith('? '):
            continue
        else:
            old_highlighted.append(line[2:])
            new_highlighted.append(line[2:])
    
    return '\n'.join(old_highlighted), '\n'.join(new_highlighted)


def parse_intensity(value: str) -> str:
    """
    解析强度字符串
    
    Args:
        value: 强度值（数字或字符串）
    
    Returns:
        标准化后的强度值（low/medium/high/extreme）
    """
    value = value.lower().strip()
    
    # 数字映射
    if value.isdigit():
        level = int(value)
        if level <= 1:
            return "low"
        elif level <= 3:
            return "medium"
        elif level <= 4:
            return "high"
        else:
            return "extreme"
    
    # 字符串映射
    intensity_map = {
        "低": "low",
        "弱": "low",
        "温和": "low",
        "low": "low",
        "轻": "low",
        
        "中": "medium",
        "中等": "medium",
        "medium": "medium",
        "正常": "medium",
        "普通": "medium",
        
        "高": "high",
        "强": "high",
        "严厉": "high",
        "high": "high",
        "严格": "high",
        
        "极高": "extreme",
        "极端": "extreme",
        "extreme": "extreme",
        "极限": "extreme",
        "苛刻": "extreme",
        "鸡蛋里挑骨头": "extreme",
    }
    
    return intensity_map.get(value, "medium")


def format_critic_for_display(critic: dict, index: int = 1) -> str:
    """
    格式化批判意见用于显示
    
    Args:
        critic: 批判意见字典
        index: 序号
    
    Returns:
        格式化后的字符串
    """
    severity_icons = {
        "critical": "🔴",
        "major": "🟠",
        "medium": "🟡",
        "minor": "🟢",
        "suggestion": "💡",
    }
    
    severity = critic.get("severity", "minor")
    icon = severity_icons.get(severity, "⚪")
    
    lines = [
        f"{icon} **问题 {index}: {critic.get('title', '未命名')}**",
        f"   类型: {critic.get('type', '未知')}",
        f"   严重程度: {severity}",
        f"   描述: {critic.get('critique', '无描述')}",
    ]
    
    if critic.get("suggestion"):
        lines.append(f"   建议: {critic['suggestion']}")
    
    return '\n'.join(lines)
