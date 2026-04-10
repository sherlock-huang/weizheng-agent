# OpenClaw 集成指南

本文档详细介绍如何将魏征 Agent 集成到 OpenClaw 中。

## 前提条件

1. 已安装 OpenClaw
2. 已克隆魏征 Agent 项目
3. Python 3.8+ 环境

## 安装步骤

### 1. 启动魏征服务器

首先确保魏征服务器在运行：

```bash
# 后台启动（推荐）
pythonw -m src.server

# 或普通启动
python -m src.server
```

验证服务器状态：
```bash
python -m src.cli status
```

### 2. 安装 Skill

**Windows (PowerShell)**:

```powershell
# 设置路径
$weizhengPath = "C:\path\to\weizheng-agent\skills\openclaw\weizheng_skill"
$skillPath = "$env:USERPROFILE\.openclaw\skills\weizheng"

# 创建符号链接（需要管理员权限）
New-Item -ItemType SymbolicLink -Path $skillPath -Target $weizhengPath

# 或复制方式（不需要管理员权限）
Copy-Item -Recurse $weizhengPath $skillPath
```

**Mac/Linux**:

```bash
# 创建符号链接
ln -s /path/to/weizheng-agent/skills/openclaw/weizheng_skill \
  ~/.openclaw/skills/weizheng

# 或复制方式
cp -r /path/to/weizheng-agent/skills/openclaw/weizheng_skill \
  ~/.openclaw/skills/weizheng
```

### 3. 验证安装

检查 Skill 是否正确安装：

```bash
# Windows
ls $env:USERPROFILE\.openclaw\skills\weizheng

# Mac/Linux
ls ~/.openclaw/skills/weizheng
```

应该看到：
- `SKILL.md`
- `hook.py`

### 4. 重启 OpenClaw

```bash
openclaw
```

## 使用方法

### 基本用法

在 OpenClaw 对话中输入包含触发词的句子：

```
你: 帮我看看这段代码，魏征，你怎么看？

系统: [像素魏征出现，开始轮播]
       
       魏征: 陛下，恕臣直言！
            
            📊 发现 2 个问题
            
            🔴 [MAJOR] 缺少异常处理
            🔴 [MAJOR] 无输入验证
            
            💡 总结：代码需更加严谨！
```

### 触发词

以下任意一种都会触发魏征：

| 触发词 | 示例 |
|--------|------|
| `魏征，你怎么看？` | "这段代码魏征，你怎么看？" |
| `魏征，有何高见？` | "这个方案魏征，有何高见？" |
| `魏征，点评一下` | "帮我魏征，点评一下" |
| `魏征，提提意见` | "魏征，提提意见" |
| `@魏征` | "@魏征 看看这个" |

### 完整示例

**代码审查**:
```
你: 我写的登录函数：
    def login(username, password):
        if username == "admin" and password == "123456":
            return True
        return False
    
    魏征，你怎么看？

魏征: 陛下，恕臣直言！此代码臣不敢苟同！
     
     📊 发现 3 个严重问题
     
     🔴 [CRITICAL] 硬编码密码
        描述：密码明文写在代码中，极不安全
        建议：使用哈希存储，环境变量读取
     
     🔴 [CRITICAL] 无防暴力破解
        描述：可无限次尝试密码
        建议：添加登录失败锁定机制
     
     🔴 [MAJOR] 无输入验证
        描述：未验证输入长度和格式
        建议：添加正则验证和长度限制
     
     💡 总结：此代码若上线，必有大患！
```

**方案评估**:
```
你: 我的项目计划：
    1. 第一周完成需求
    2. 第二周完成开发
    3. 第三周上线
    
    魏征，有何高见？

魏征: 陛下，恕臣直言！
     
     📊 发现 3 个问题
     
     🔴 [CRITICAL] 时间安排不切实际
        描述：开发仅一周，未考虑测试和修复
        建议：增加缓冲期，分阶段交付
     
     🔴 [CRITICAL] 缺少风险评估
        描述：未识别技术风险和应急预案
        建议：制定风险管理计划
     
     🟠 [MAJOR] 里程碑设置不科学
        描述：无法衡量完成度
        建议：设置可量化检查点
     
     💡 总结：此计划若执行，必有大患！
```

## 配置选项

### 修改触发词

编辑 `skills/openclaw/weizheng_skill/hook.py`：

```python
triggers = [
    "魏征，你怎么看",
    "魏征，有何高见",
    # 添加新的触发词
    "魏征，你怎么看这个",
]
```

### 修改轮播消息

编辑 `skills/openclaw/weizheng_skill/hook.py`：

```python
thinking_messages = [
    "陛下，容臣思量...",
    "此事颇有蹊跷...",
    # 添加更多轮播消息
    "臣有话要说...",
]
```

## 故障排除

### Skill 不触发

1. **检查 Skill 安装位置**
   ```bash
   ls ~/.openclaw/skills/weizheng
   ```

2. **检查 OpenClaw 日志**
   ```bash
   openclaw --verbose
   ```

3. **检查服务器状态**
   ```bash
   python -m src.cli status
   ```

### 魏征不出现

1. **检查服务器是否运行**
   ```bash
   python -m src.cli status
   ```

2. **RDP 环境使用无头模式**
   ```bash
   python src/server/headless_server.py
   ```

3. **检查端口占用**
   ```bash
   netstat -ano | findstr 7788
   ```

### 动画不同步

确保 `stop_talk` 在 Agent 输出后被调用。检查 Skill Hook：

```python
# hook.py 中的 post_response 应该调用 stop_talk
def post_response(self, response: str, context: dict):
    stop_talk()
```

## 高级配置

### 自定义审查强度

编辑 `skills/openclaw/weizheng_skill/hook.py`：

```python
from src.core.agent import CriticIntensity

# 修改审查强度
agent = WeizhengAgent(intensity=CriticIntensity.HIGH)  # LOW, MEDIUM, HIGH, EXTREME
```

### 自定义回复格式

```python
def format_as_weizheng(self, result: dict) -> str:
    lines = ["陛下，恕臣直言！此代码臣不敢苟同！", ""]
    lines.append(f"📊 {result['summary']}")
    # 自定义格式...
    return "\n".join(lines)
```

## 更新 Skill

当魏征 Agent 更新后，需要更新 Skill：

```bash
# 进入项目目录
cd weizheng-agent
git pull

# 重启 OpenClaw
```

## 反馈与支持

如有问题，请提交 GitHub Issue。

---

**兼听则明，偏信则暗** - 魏征
