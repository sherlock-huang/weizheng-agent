# OpenClaw 集成指南

## 功能说明

魏征 Agent 可以与 OpenClaw 共享 workspace：

1. **共享记忆**: 魏征的记忆保存在 OpenClaw 项目目录中
2. **读取上下文**: 魏征可以读取 OpenClaw 的对话历史
3. **同步审查**: 魏征的审查结果同步到 OpenClaw

## OpenClaw Workspace 结构

```
~/.openclaw/workspace/
├── projects/
│   └── {project_id}/
│       ├── memory/
│       │   ├── conversation_history.jsonl  <- OpenClaw对话
│       │   └── weizheng/                    <- 魏征记忆
│       │       ├── conversations/
│       │       └── insights/
│       └── files/
└── global/
    └── settings.json
```

## 自动检测

魏征会自动检测 OpenClaw 安装位置：

- Windows: `%USERPROFILE%\.openclaw\workspace`
- Mac/Linux: `~/.openclaw/workspace`

## 手动配置

如果需要指定路径：

```python
from src.integrations.openclaw import configure_shared_workspace

# 指定路径
openclaw = configure_shared_workspace("/path/to/openclaw/workspace")

# 或使用环境变量
export OPENCLAW_WORKSPACE="/path/to/workspace"
```

## 使用示例

```python
from src.integrations.openclaw import get_openclaw

# 获取集成实例
openclaw = get_openclaw()

# 列出所有项目
projects = openclaw.list_projects()
for p in projects:
    print(f"项目: {p['id']}")

# 设置当前项目
openclaw.set_current_project("my-project")

# 读取 OpenClaw 的对话历史
history = openclaw.read_conversation_history(limit=10)
for h in history:
    print(f"[{h['timestamp']}] {h['content'][:100]}...")

# 魏征的记忆会自动保存在该项目下
memory_path = openclaw.get_project_memory_path()
print(f"魏征记忆路径: {memory_path}")
```

## 与魏征 Agent 集成

在 `weizheng_with_llm.py` 中已自动集成：

```python
# 启动时会自动检测并连接 OpenClaw
python weizheng_with_llm.py

# 输出:
# [初始化] 连接 OpenClaw...
# [OpenClaw] 检测到 workspace: ~/.openclaw/workspace
# [OpenClaw] 发现 3 个项目:
#   - project-a
#   - project-b
#   - project-c
```

## 记忆共享

当魏征进行审查时：

1. 先读取 OpenClaw 项目的对话历史
2. 结合当前内容进行审查
3. 审查结果保存到该项目的 `memory/weizheng/` 目录
4. OpenClaw 可以看到魏征的审查记录

这样两边的记忆是互通的！
