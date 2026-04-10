# ECC 对 Kimi Code 的增强方案

## 分析：ECC 能为 Kimi Code 带来什么？

### Kimi Code 当前配置结构

```
~/.kimi/
├── config.toml          # 主配置
├── kimi.json            # 工作目录列表
├── sessions/            # 会话历史
├── logs/                # 日志
└── plans/               # 计划文件
```

### 可以增强的方面

#### 1. AGENTS.md 支持 ✅
Kimi Code **可以读取** AGENTS.md 文件来获取 Agent 配置。

**价值**：让 Kimi Code 识别并使用魏征 Agent

#### 2. 规则文件 (rules/) ⚠️ 部分支持
Kimi Code 没有内置的 rules/ 目录，但可以通过以下方式复用：
- 将规则转换为 SKILL.md 放在项目目录
- 通过 MCP (Model Context Protocol) 加载规则

#### 3. 安全扫描 (AgentShield) ✅
AgentShield 是独立的 npm 包，可以在 Kimi Code 中调用：
```bash
npx ecc-agentshield scan
```

#### 4. 记忆持久化 ✅
Kimi Code 已经有 sessions/ 目录存储会话，可以扩展与魏征共享

---

## 安装步骤

### 步骤 1: 在 Kimi Code 项目目录添加 AGENTS.md

```bash
# 在当前项目目录创建 AGENTS.md
cd your-project
cp /path/to/weizheng-agent/AGENTS.md ./AGENTS.md
```

这样 Kimi Code 会读取并识别魏征 Agent。

### 步骤 2: 安装 AgentShield 安全扫描

```bash
# 全局安装 AgentShield
npm install -g ecc-agentshield

# 在项目目录创建 .kimi/hooks/ 目录（如果 Kimi Code 支持 hooks）
mkdir -p .kimi/hooks
```

### 步骤 3: 创建 Kimi Code 专用配置

创建 `.kimi/config.toml` 在项目目录：

```toml
# 项目级 Kimi Code 配置

[agents]
enabled = ["weizheng"]

[hooks]
pre_critique = "python /path/to/weizheng-agent/trigger.py"

[mcp.servers.weizheng]
command = "python"
args = ["/path/to/weizheng-agent/mcp_server.py"]
```

### 步骤 4: 启用魏征作为 Kimi Code 的子 Agent

在 `~/.kimi/config.toml` 中添加：

```toml
[mcp.servers.weizheng]
command = "python"
args = ["C:/path/to/weizheng-agent/mcp_server.py"]
```

---

## 具体启用方法

### 方法 A: 通过 MCP 集成（推荐）

Kimi Code 支持 MCP (Model Context Protocol)，可以将魏征作为 MCP 服务器：

```bash
# 1. 确保魏征的 MCP 服务器可运行
cd weizheng-agent
python mcp_server.py

# 2. 在 ~/.kimi/config.toml 中添加 MCP 配置
cat >> ~/.kimi/config.toml << 'EOF'

[mcp.servers.weizheng]
command = "python"
args = ["C:/Users/openclaw-windows-2/kzy/workspace/weizheng-anget/mcp_server.py"]
EOF
```

### 方法 B: 作为外部工具调用

在 Kimi Code 中直接运行魏征：

```python
# 在 Kimi Code 中运行
!python C:/Users/openclaw-windows-2/kzy/workspace/weizheng-anget/weizheng_desktop.py
```

### 方法 C: 共享记忆空间

让 Kimi Code 和魏征共享同一个 workspace：

```python
# 在 weizheng-agent 中配置
export KIMI_CODE_WORKSPACE="~/.kimi"
python weizheng_with_ecc.py
```

---

## 实际使用场景

### 场景 1: 在 Kimi Code 中触发魏征

```
用户在 Kimi Code 中:
"帮我审查这段代码"

Kimi Code 识别意图 -> 调用魏征 MCP 工具 -> 魏征返回审查结果 -> Kimi Code 展示
```

### 场景 2: 安全扫描

```bash
# 在 Kimi Code 中运行
!agentshield scan .
```

### 场景 3: 读取历史上下文

魏征可以读取 Kimi Code 的 sessions/ 目录获取对话历史。

---

## 安装脚本

创建 `install_for_kimi.bat`：

```batch
@echo off
echo Installing Weizheng Agent for Kimi Code...

:: 1. 复制 AGENTS.md 到当前目录
copy AGENTS.md .\AGENTS.md

:: 2. 安装 AgentShield
call npm install -g ecc-agentshield

:: 3. 创建 .kimi 目录
mkdir .kimi 2>nul

:: 4. 创建 MCP 配置
echo [mcp.servers.weizheng] > .kimi\config.toml
echo command = "python" >> .kimi\config.toml
echo args = ["%CD%\mcp_server.py"] >> .kimi\config.toml

echo Installation complete!
echo You can now use Weizheng in Kimi Code.
pause
```

---

## 总结

**对 Kimi Code 最有价值的增强**：

1. **AGENTS.md** - Kimi Code 可以读取，识别魏征角色
2. **AgentShield** - 独立运行，提供安全扫描
3. **MCP 集成** - 将魏征作为工具提供给 Kimi Code 调用
4. **共享记忆** - 读取 Kimi Code 的会话历史

**不能直接使用的内容**：
- Claude Code 特定的 hooks（PreToolUse 等）
- settings.json 配置（Kimi Code 使用 config.toml）
- 部分 skills（需要适配格式）
