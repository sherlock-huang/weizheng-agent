"""
OpenClaw 集成模块

实现与 OpenClaw 的 workspace 共享，包括：
1. 读取 OpenClaw 的对话历史
2. 共享记忆空间
3. 同步项目上下文
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class OpenClawIntegration:
    """
    OpenClaw 集成器
    
    OpenClaw 默认 workspace 位置：
    - Windows: %USERPROFILE%\.openclaw\workspace
    - Mac/Linux: ~/.openclaw/workspace
    """
    
    def __init__(self, workspace_path: Optional[str] = None):
        """
        初始化 OpenClaw 集成
        
        Args:
            workspace_path: OpenClaw workspace 路径，默认自动检测
        """
        if workspace_path:
            self.workspace_path = Path(workspace_path)
        else:
            self.workspace_path = self._detect_openclaw_workspace()
        
        self.projects_path = self.workspace_path / "projects"
        self.current_project: Optional[str] = None
        
    def _detect_openclaw_workspace(self) -> Path:
        """自动检测 OpenClaw workspace 位置"""
        possible_paths = [
            Path.home() / ".openclaw" / "workspace",
            Path(os.environ.get("USERPROFILE", "")) / ".openclaw" / "workspace",
            Path.home() / ".config" / "openclaw" / "workspace",
            Path.home() / ".local" / "share" / "openclaw" / "workspace",
            Path.home() / "openclaw" / "workspace",
        ]
        
        for path in possible_paths:
            if path.exists():
                print(f"[OpenClaw] 检测到 workspace: {path}")
                return path
        
        # 默认位置
        default = Path.home() / ".openclaw" / "workspace"
        default.mkdir(parents=True, exist_ok=True)
        print(f"[OpenClaw] 使用默认 workspace: {default}")
        return default
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """列出 OpenClaw 中的所有项目"""
        projects = []
        
        if not self.projects_path.exists():
            return projects
        
        for project_dir in self.projects_path.iterdir():
            if project_dir.is_dir():
                project_info = {
                    "id": project_dir.name,
                    "path": str(project_dir),
                    "has_memory": (project_dir / "memory").exists(),
                }
                
                config_file = project_dir / "config.json"
                if config_file.exists():
                    try:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            config = json.load(f)
                            project_info["name"] = config.get("name", project_dir.name)
                    except:
                        pass
                
                projects.append(project_info)
        
        return projects
    
    def set_current_project(self, project_id: str) -> bool:
        """设置当前项目"""
        project_path = self.projects_path / project_id
        if project_path.exists():
            self.current_project = project_id
            memory_path = project_path / "memory" / "weizheng"
            memory_path.mkdir(parents=True, exist_ok=True)
            return True
        return False
    
    def get_project_memory_path(self, project_id: Optional[str] = None) -> Path:
        """获取项目的记忆路径"""
        pid = project_id or self.current_project or "default"
        memory_path = self.projects_path / pid / "memory" / "weizheng"
        memory_path.mkdir(parents=True, exist_ok=True)
        return memory_path
    
    def read_conversation_history(self, project_id: Optional[str] = None, 
                                   limit: int = 10) -> List[Dict[str, Any]]:
        """读取 OpenClaw 的对话历史"""
        pid = project_id or self.current_project
        if not pid:
            return []
        
        history_file = self.projects_path / pid / "memory" / "conversation_history.jsonl"
        
        if not history_file.exists():
            return []
        
        conversations = []
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines[-limit:]:
                    try:
                        conv = json.loads(line.strip())
                        conversations.append(conv)
                    except:
                        continue
        except Exception as e:
            print(f"[OpenClaw] 读取失败: {e}")
        
        return conversations
    
    def get_shared_context(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """获取共享上下文"""
        context = {
            "project_id": project_id or self.current_project,
            "recent_conversations": self.read_conversation_history(project_id, limit=5),
            "weizheng_memory_path": str(self.get_project_memory_path(project_id)),
        }
        return context


def configure_shared_workspace(workspace_path: Optional[str] = None) -> OpenClawIntegration:
    """配置共享 workspace"""
    integration = OpenClawIntegration(workspace_path)
    
    projects = integration.list_projects()
    if projects:
        print(f"[OpenClaw] 发现 {len(projects)} 个项目")
        for p in projects:
            print(f"  - {p['id']}")
    
    return integration


_openclaw_instance: Optional[OpenClawIntegration] = None


def get_openclaw() -> OpenClawIntegration:
    """获取全局 OpenClaw 集成实例"""
    global _openclaw_instance
    if _openclaw_instance is None:
        _openclaw_instance = OpenClawIntegration()
    return _openclaw_instance
