"""
ECC (Everything Claude Code) 适配器

让魏征 Agent 能够复用 ECC 的组件：
1. 加载 ECC 的规则文件
2. 调用 ECC 的技能
3. 集成 AgentShield 安全扫描
4. 符合 AGENTS.md 标准
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class ECCRule:
    """ECC 规则"""
    name: str
    description: str
    languages: List[str]
    severity: str
    pattern: Optional[str] = None
    message: Optional[str] = None


@dataclass
class ECCSkill:
    """ECC 技能"""
    name: str
    description: str
    when_to_use: str
    examples: List[str]
    content: str


class ECCAdapter:
    """
    ECC 适配器
    
    用于加载和复用 Everything Claude Code 的组件
    """
    
    def __init__(self, ecc_path: Optional[str] = None):
        """
        初始化 ECC 适配器
        
        Args:
            ecc_path: ECC 仓库路径，默认自动检测
        """
        if ecc_path:
            self.ecc_path = Path(ecc_path)
        else:
            self.ecc_path = self._detect_ecc()
        
        self.rules: Dict[str, List[ECCRule]] = {}
        self.skills: Dict[str, ECCSkill] = {}
        
    def _detect_ecc(self) -> Optional[Path]:
        """自动检测 ECC 安装位置"""
        possible_paths = [
            Path.home() / "everything-claude-code",
            Path.home() / "ecc",
            Path.home() / ".ecc",
            Path("./everything-claude-code"),
        ]
        
        for path in possible_paths:
            if path.exists() and (path / "rules").exists():
                print(f"[ECC] 检测到: {path}")
                return path
        
        print("[ECC] 未检测到 ECC，将使用内置规则")
        return None
    
    def load_rules(self, language: str = "common") -> List[ECCRule]:
        """
        加载 ECC 规则
        
        Args:
            language: 语言 (common/typescript/python/golang/...)
        
        Returns:
            规则列表
        """
        if not self.ecc_path:
            return self._get_builtin_rules(language)
        
        if language in self.rules:
            return self.rules[language]
        
        rules_dir = self.ecc_path / "rules" / language
        if not rules_dir.exists():
            print(f"[ECC] 未找到 {language} 规则，使用 common")
            rules_dir = self.ecc_path / "rules" / "common"
        
        rules = []
        
        # 加载 .md 规则文件
        for rule_file in rules_dir.glob("*.md"):
            try:
                with open(rule_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 解析 frontmatter
                rule = self._parse_rule_file(content, rule_file.stem)
                if rule:
                    rules.append(rule)
            except Exception as e:
                print(f"[ECC] 加载规则失败 {rule_file}: {e}")
        
        self.rules[language] = rules
        print(f"[ECC] 加载了 {len(rules)} 条 {language} 规则")
        return rules
    
    def _parse_rule_file(self, content: str, name: str) -> Optional[ECCRule]:
        """解析规则文件"""
        # 简单解析 YAML frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                body = parts[2]
                
                try:
                    metadata = yaml.safe_load(frontmatter)
                    return ECCRule(
                        name=name,
                        description=metadata.get('description', ''),
                        languages=metadata.get('languages', ['common']),
                        severity=metadata.get('severity', 'warning'),
                        pattern=metadata.get('pattern'),
                        message=body.strip()
                    )
                except:
                    pass
        
        # 没有 frontmatter，使用文件名
        return ECCRule(
            name=name,
            description=content[:100],
            languages=['common'],
            severity='warning',
            message=content
        )
    
    def load_skill(self, skill_name: str) -> Optional[ECCSkill]:
        """
        加载 ECC 技能
        
        Args:
            skill_name: 技能名称
        
        Returns:
            技能对象
        """
        if skill_name in self.skills:
            return self.skills[skill_name]
        
        if not self.ecc_path:
            return None
        
        skill_file = self.ecc_path / "skills" / skill_name / "SKILL.md"
        if not skill_file.exists():
            print(f"[ECC] 未找到技能: {skill_name}")
            return None
        
        try:
            with open(skill_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析 frontmatter
            skill = self._parse_skill_file(content, skill_name)
            if skill:
                self.skills[skill_name] = skill
            return skill
            
        except Exception as e:
            print(f"[ECC] 加载技能失败 {skill_name}: {e}")
            return None
    
    def _parse_skill_file(self, content: str, name: str) -> Optional[ECCSkill]:
        """解析技能文件"""
        if not content.startswith('---'):
            return None
        
        parts = content.split('---', 2)
        if len(parts) < 3:
            return None
        
        frontmatter = parts[1]
        body = parts[2]
        
        try:
            metadata = yaml.safe_load(frontmatter)
            return ECCSkill(
                name=name,
                description=metadata.get('description', ''),
                when_to_use=metadata.get('when_to_use', ''),
                examples=metadata.get('examples', []),
                content=body.strip()
            )
        except:
            return None
    
    def apply_rules(self, content: str, language: str = "common") -> List[Dict]:
        """
        对内容应用规则检查
        
        Args:
            content: 要检查的内容
            language: 语言
        
        Returns:
            违规列表
        """
        rules = self.load_rules(language)
        violations = []
        
        for rule in rules:
            # 简单的关键词匹配
            if rule.pattern and rule.pattern in content.lower():
                violations.append({
                    "rule": rule.name,
                    "severity": rule.severity,
                    "message": rule.message,
                    "description": rule.description
                })
        
        return violations
    
    def get_critique_prompt(self, skill_name: str = "code-review") -> Optional[str]:
        """
        获取批判提示词
        
        从 ECC 技能中提取审查相关的提示词
        """
        skill = self.load_skill(skill_name)
        if skill:
            return skill.content
        
        # 默认提示词
        return """审查代码时请注意：
1. 逻辑漏洞和边界条件
2. 性能瓶颈
3. 安全隐患
4. 可读性和维护性
5. 最佳实践遵循"""
    
    def _get_builtin_rules(self, language: str) -> List[ECCRule]:
        """获取内置规则（当 ECC 不可用时）"""
        builtin_rules = {
            "common": [
                ECCRule(
                    name="no-console-log",
                    description="避免在生产代码中使用 console.log",
                    languages=["common"],
                    severity="warning",
                    pattern="console.log",
                    message="请移除调试用的 console.log"
                ),
                ECCRule(
                    name="no-hardcoded-secrets",
                    description="不要硬编码密钥",
                    languages=["common"],
                    severity="error",
                    pattern="api_key",
                    message="密钥应该使用环境变量"
                ),
            ],
            "python": [
                ECCRule(
                    name="no-bare-except",
                    description="避免裸 except",
                    languages=["python"],
                    severity="warning",
                    pattern="except:",
                    message="请使用具体的异常类型"
                ),
            ]
        }
        return builtin_rules.get(language, builtin_rules["common"])


class AgentShieldIntegration:
    """
    AgentShield 安全扫描集成
    
    AgentShield 是 ECC 的安全扫描工具
    """
    
    def __init__(self):
        self.enabled = self._check_agentshield()
    
    def _check_agentshield(self) -> bool:
        """检查是否安装了 AgentShield"""
        import subprocess
        try:
            result = subprocess.run(
                ["npx", "ecc-agentshield", "--version"],
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False
    
    def scan(self, target_path: str) -> Dict[str, Any]:
        """
        运行安全扫描
        
        Args:
            target_path: 要扫描的路径
        
        Returns:
            扫描结果
        """
        if not self.enabled:
            return {"error": "AgentShield 未安装", "enabled": False}
        
        import subprocess
        try:
            result = subprocess.run(
                ["npx", "ecc-agentshield", "scan", target_path, "--json"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return {"error": result.stderr, "enabled": True}
                
        except Exception as e:
            return {"error": str(e), "enabled": self.enabled}


def create_ecc_adapter() -> ECCAdapter:
    """创建 ECC 适配器"""
    return ECCAdapter()


# 全局实例
_ecc_adapter: Optional[ECCRule] = None


def get_ecc_adapter() -> ECCAdapter:
    """获取全局 ECC 适配器"""
    global _ecc_adapter
    if _ecc_adapter is None:
        _ecc_adapter = ECCAdapter()
    return _ecc_adapter
