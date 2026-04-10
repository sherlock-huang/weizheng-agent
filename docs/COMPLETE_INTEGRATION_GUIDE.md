# 魏征 Agent 完整集成指南

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                         用户层                                │
│                   (在 OpenClaw 中对话)                        │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼ 说"魏征，你怎么看？"
┌─────────────────────────────────────────────────────────────┐
│                      OpenClaw 层                            │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Skill: weizheng_skill                                │  │
│  │  - 检测触发词                                          │  │
│  │  - 调用魏征子 Agent 生成审查意见                        │  │
│  │  - 调用 CLI 触发像素动画                                │  │
│  └────────────────────┬──────────────────────────────────┘  │
└───────────────────────┼─────────────────────────────────────┘
                        │
                        ▼ CLI 命令
┌─────────────────────────────────────────────────────────────┐
│                      CLI 工具层                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  python -m src.cli talk "消息"                         │  │
│  │  python -m src.cli stop                                │  │
│  └────────────────────┬──────────────────────────────────┘  │
└───────────────────────┼─────────────────────────────────────┘
                        │ HTTP POST
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                      像素服务端层                            │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  PixelWeizhengServer                                  │  │
│  │  - 监听端口 7788                                       │  │
│  │  - 接收 talk/stop 命令                                 │  │
│  │  - 播放像素动画                                        │  │
│  └───────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼ 显示
                    ┌──────────────┐
                    │  像素魏征     │
                    │ (屏幕右下角)  │
                    └──────────────┘
```

## 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/your-username/weizheng-agent.git
cd weizheng-agent
```

### 2. 安装依赖

```bash
pip install Pillow
```

### 3. 安装 OpenClaw Skill

```bash
# 创建 OpenClaw Skill 目录
mkdir -p ~/.openclaw/skills

# 链接魏征 Skill
ln -s $(pwd)/skills/openclaw/weizheng_skill ~/.openclaw/skills/weizheng

# 或者复制
cp -r skills/openclaw/weizheng_skill ~/.openclaw/skills/weizheng
```

### 4. 配置 OpenClaw

在 `~/.openclaw/config.json` 中添加：

```json
{
  "skills": {
    "weizheng": {
      "enabled": true,
      "auto_trigger": true
    }
  }
}
```

## 启动步骤

### 1. 启动像素服务端

在终端中运行：

```bash
python -m src.server
```

你应该看到：
- 屏幕右下角出现像素魏征
- 终端显示 "像素服务端已启动"

### 2. 启动 OpenClaw

在另一个终端中：

```bash
openclaw
```

## 使用流程

### 正常对话流程

1. **用户在 OpenClaw 中输入**：
   ```
   这段代码怎么样？
   def add(a, b):
       return a + b
   
   魏征，你怎么看？
   ```

2. **OpenClaw Skill 触发**：
   - 检测到触发词 "魏征，你怎么看？"
   - 提取前面的代码内容
   - 调用魏征子 Agent 生成审查意见

3. **触发像素动画**：
   ```python
   # Skill 内部自动调用
   subprocess.run(["python", "-m", "src.cli", "talk", "陛下！臣有话说！"])
   ```

4. **像素魏征响应**：
   - 屏幕右下角的像素魏征开始说话动画
   - 显示气泡对话框

5. **魏征回复用户**：
   ```
   魏征: 陛下，恕臣直言！此代码臣不敢苟同！
   
   🔴 [CRITICAL] 缺少输入验证...
   🟠 [MAJOR] 缺少文档字符串...
   ```

6. **动画自动停止**：
   - 回复完成后，Skill 自动调用 stop
   - 像素魏征恢复 idle 状态

### CLI 手动控制

```bash
# 触发说话动画
python -m src.cli talk "陛下！臣有话说！" --duration 3

# 停止说话动画
python -m src.cli stop

# 查看状态
python -m src.cli status
```

## 测试

运行完整链路测试：

```bash
python test_complete_flow.py
```

测试内容包括：
1. 服务端状态检查
2. CLI talk 命令
3. CLI stop 命令
4. Skill Hook 触发词检测
5. 完整链路闭环

## 故障排除

### 问题 1: 像素服务端无法启动

**症状**：运行 `python -m src.server` 报错

**解决**：
```bash
# 检查 Python 版本
python --version  # 需要 3.8+

# 检查 tkinter
python -c "import tkinter; print('OK')"

# 检查 Pillow
python -c "from PIL import Image; print('OK')"
```

### 问题 2: CLI 无法连接到服务端

**症状**：`python -m src.cli status` 返回错误

**解决**：
```bash
# 检查服务端是否运行
curl http://localhost:7788/api/status

# 检查端口是否被占用
lsof -i :7788  # Mac/Linux
netstat -an | findstr 7788  # Windows
```

### 问题 3: OpenClaw Skill 不触发

**症状**：说"魏征，你怎么看？"没有反应

**解决**：
```bash
# 检查 Skill 是否安装
ls ~/.openclaw/skills/weizheng/

# 检查 OpenClaw 配置
cat ~/.openclaw/config.json

# 查看 OpenClaw 日志
openclaw --verbose
```

### 问题 4: 动画不显示

**症状**：CLI 返回成功，但看不到像素魏征

**解决**：
1. 检查是否在远程服务器上运行（需要本地显示器）
2. 检查屏幕右下角是否被其他窗口遮挡
3. 检查多显示器设置

## 配置选项

### 像素服务端配置

```python
# src/server/pixel_server.py
PixelWeizhengServer(
    http_port=7788,      # HTTP 端口
    pixel_size=140       # 像素大小
)
```

### CLI 配置

```python
# src/cli/weizheng_cli.py
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 7788
```

### Skill 配置

```python
# skills/openclaw/weizheng_skill/hook.py
WEIZHENG_SERVER_HOST = "localhost"
WEIZHENG_SERVER_PORT = 7788
```

## 开发指南

### 添加新的触发词

编辑 `skills/openclaw/weizheng_skill/hook.py`：

```python
triggers = [
    "魏征，你怎么看",
    "魏征，有何高见",
    # 添加新的触发词
    "魏征，请批评",
]
```

### 修改动画时长

编辑 `skills/openclaw/weizheng_skill/hook.py`：

```python
def on_user_message(message: str, context: dict) -> dict:
    # ...
    talk_result = trigger_talk("陛下！臣有话说！", duration=5.0)  # 改为 5 秒
```

### 自定义气泡文字

编辑 `src/server/pixel_server.py`：

```python
def talk(self, message: str = "陛下！臣有话说！", duration: float = 3.0):
    # 自定义默认消息
```

## 架构说明

### 为什么这样设计？

1. **像素服务端独立运行**
   - GUI 需要主线程，不能与 OpenClaw 阻塞
   - 可以单独启动/停止，不影响 OpenClaw

2. **CLI 作为桥梁**
   - 简单的命令行接口，易于调用
   - 可以被任何工具调用（OpenClaw、脚本、其他 Agent）

3. **Skill 集成到 OpenClaw**
   - 利用 OpenClaw 的 Skill 系统
   - 自动触发，无需手动干预
   - 完整的生命周期管理

### 扩展性

- 可以轻松集成到其他工具（Cursor、Kimi Code 等）
- CLI 接口标准化，易于调用
- HTTP API 可以被远程调用

## 链接

- 项目地址：https://github.com/your-username/weizheng-agent
- 问题反馈：https://github.com/your-username/weizheng-agent/issues
