# 魏征 Agent (Weizheng Agent)

> **专门提反对意见、挑毛病的独立 AI Agent**
>
> 像素动画 + OpenClaw Skill + CLI 工具完整闭环

![Python](https://img.shields.io/badge/python-3.8+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## 项目介绍

魏征 Agent 是一个独立的 AI 审查助手，灵感来源于唐朝名臣魏征——敢于直言进谏、专门挑毛病的角色。

当你在开发中需要有人"提反对意见"时，只需说一句"**魏征，你怎么看？**"，魏征就会：

1. 🎭 屏幕右下角出现像素魏征（大眼萌造型）
2. 💬 气泡显示轮播思考中...
3. 🔍 AI 分析你的代码/方案，找出问题
4. 📋 给出详细的审查意见和改进建议

## 完整闭环链路

```
用户: "这段代码有问题吗？魏征，你怎么看？"
    ↓
OpenClaw Skill 检测触发词
    ↓
调用 CLI → HTTP POST → 像素服务器 (端口 7788)
    ↓
屏幕右下角像素魏征出现，气泡轮播显示思考中...
    ↓
魏征 Agent 生成审查意见
    ↓
显示审查结果，像素魏征停止
```

## 功能特性

- 🎨 **像素动画** - 140x140px 大眼萌魏征，8帧待机动画 + 8帧说话动画
- 💬 **气泡对话框** - 集成在窗口内，多句话轮播显示
- 🔌 **OpenClaw 集成** - 自动检测触发词，无缝集成到对话中
- 🖥️ **后台运行** - 支持无窗口后台运行，不占用终端
- 🌐 **HTTP API** - RESTful API 供外部调用
- 🖼️ **RDP 兼容** - 支持远程桌面环境

## 快速开始

### 1. 安装

```bash
# 克隆项目
git clone <repository-url>
cd weizheng-agent

# 安装依赖
pip install Pillow

# 可选：系统托盘模式需要
pip install pystray pillow
```

### 2. 启动服务器

**方式一：后台启动（推荐）**

双击 `start_background.bat` 或在终端执行：

```bash
pythonw -m src.server
```

服务器将在后台运行，无终端窗口。

**方式二：普通启动（调试）**

```bash
python -m src.server
```

**方式三：无头模式（RDP/无显示器）**

```bash
python src/server/headless_server.py
```

### 3. 验证安装

```bash
python verify_setup.py
```

### 4. 测试

```bash
# 触发魏征说话
python -m src.cli talk "陛下，容臣思量..." "此事颇有蹊跷！" "臣斗胆直言..."

# 9秒后停止
python -m src.cli stop
```

## OpenClaw 集成

### 安装 Skill

**Windows (PowerShell)**:
```powershell
$source = "C:\path\to\weizheng-agent\skills\openclaw\weizheng_skill"
$target = "$env:USERPROFILE\.openclaw\skills\weizheng"
New-Item -ItemType SymbolicLink -Path $target -Target $source
```

**Mac/Linux**:
```bash
ln -s /path/to/weizheng-agent/skills/openclaw/weizheng_skill \
  ~/.openclaw/skills/weizheng
```

### 使用

在 OpenClaw 中正常对话，当提到触发词时自动触发：

```
你: 这段代码怎么样？
    def add(a, b):
        return a + b
    
    魏征，你怎么看？

系统:
[屏幕右下角像素魏征出现，气泡轮播]
  → "陛下，容臣思量..."
  → "此事颇有蹊跷！"
  → "臣斗胆直言..."

[Agent生成回复...]

魏征: 陛下，恕臣直言！
     
     📊 发现 1 个问题
     
     🔴 [MAJOR] 缺少类型注解
        描述：函数参数无类型提示，难以维护
        建议：添加 -> int 和类型注解
     
     💡 总结：虽是小函数，亦需严谨！

[像素魏征停止]
```

### 人格切换规则

魏征 Agent 采用**双人格模式**：

| 状态 | 触发词 | 效果 |
|------|--------|------|
| **默认** | 无 | 普通助手人格，正常对话 |
| **魏征人格** | "魏征，你怎么看？" | 进入审查模式，像素动画出现，语气变为谏臣风格 |
| **退出** | "魏征，退下" | 魏征显示"微臣告退..."，3秒后消失，恢复普通人格 |

### 触发词

**进入魏征人格**：
- `魏征，你怎么看？`
- `魏征，有何高见？`
- `魏征，点评一下`
- `魏征，提提意见`
- `@魏征`

**退出魏征人格**：
- `魏征，退下`
- `魏征退下`
- `退下吧魏征`

## API 参考

### HTTP API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/talk` | POST | 开始说话动画（支持多句话轮播） |
| `/api/stop` | POST | 停止说话动画 |
| `/api/status` | GET | 获取服务器状态 |

### CLI 命令

```bash
# 检查状态
python -m src.cli status

# 单句说话
python -m src.cli talk "陛下！臣有话说！"

# 多句轮播（每句3秒）
python -m src.cli talk "句1" "句2" "句3"

# 停止
python -m src.cli stop
```

## 文件结构

```
weizheng-agent/
├── README.md                  # 本文档
├── LICENSE                    # MIT 许可证
├── requirements.txt           # Python 依赖
│
├── start_background.bat       # 后台启动（推荐）
├── start_server.bat           # 普通启动
├── start_headless.bat         # 无头模式启动
├── start_server_background.vbs # VBS 启动（无窗口）
├── stop_server.bat            # 停止服务器
├── check_status.bat           # 查看状态
│
├── verify_setup.py            # 环境验证
├── demo.py                    # 演示脚本
├── run_with_tray.py           # 系统托盘模式
│
├── src/
│   ├── server/               # 像素服务端
│   │   ├── pixel_server.py   # 核心服务器
│   │   ├── headless_server.py # 无头模式
│   │   └── __main__.py
│   ├── cli/                  # CLI 工具
│   │   ├── weizheng_cli.py
│   │   └── __main__.py
│   ├── core/                 # Agent 核心
│   │   ├── agent.py
│   │   └── critic.py
│   └── ui/                   # 像素动画
│       └── pixel_weizheng_v4.py
│
├── skills/openclaw/          # OpenClaw Skill
│   └── weizheng_skill/
│       ├── SKILL.md
│       └── hook.py
│
├── assets/sprites/v4/        # 像素帧资源
└── docs/                     # 详细文档
```

## 配置说明

### 修改轮播速度

编辑 `src/server/pixel_server.py`：

```python
self.msg_display_duration = 3000  # 毫秒，3000=3秒
```

### 修改端口

```bash
python -m src.server --port 7789
```

### CLI 指定端口

```bash
python -m src.cli talk "消息" --host localhost --port 7789
```

## 故障排除

### 服务器启动后没显示魏征

**原因**：RDP/远程桌面不支持 tkinter GUI

**解决**：使用无头模式
```bash
python src/server/headless_server.py
```

### 无法连接到服务器

```bash
# 检查服务器状态
python -m src.cli status

# 检查端口占用
netstat -ano | findstr 7788
```

### OpenClaw Skill 不触发

1. 检查 Skill 是否正确链接到 `~/.openclaw/skills/weizheng`
2. 检查服务器是否运行
3. 查看 OpenClaw 日志

## 系统要求

- Windows 10/11（需要显示器，RDP 用无头模式）
- Python 3.8+
- Pillow (`pip install Pillow`)
- 可选：pystray (`pip install pystray`)

## 贡献与反馈

欢迎分享、引用与改进。

- 发现问题：欢迎提交 [Issue](https://github.com/sherlock-huang/weizheng-agent/issues)
- 有改进建议：欢迎提交 [Pull Request](https://github.com/sherlock-huang/weizheng-agent/pulls)

## 相关链接

- 主站博客：https://kunpeng-ai.com
- GitHub 组织：https://github.com/kunpeng-ai-research
- OpenClaw 官方：https://openclaw.ai

## 维护与署名

- 维护者：鲲鹏AI探索局

## 许可证

MIT License

---

**兼听则明，偏信则暗** - 魏征
