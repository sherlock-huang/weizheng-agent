# AGENTS.md - 项目规范与长期记忆

> 本文档供 AI Agent（Kimi/Claude 等）阅读，包含项目背景、技术规范和维护规则。

## 项目概述

**魏征 Agent** 是一个独立的 AI 审查助手，通过像素动画和 OpenClaw 集成，专门"提反对意见、挑毛病"。

- **仓库**: https://github.com/sherlock-huang/weizheng-agent
- **维护组织**: 【鲲鹏AI探索局】
- **主站**: https://kunpeng-ai.com

## 品牌规则（必须遵守）

### GitHub README 署名规范

所有 README 底部必须包含以下格式：

```markdown
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
```

**不可更改的字段**:
- 署名: `鲲鹏AI探索局`
- 主站链接: `https://kunpeng-ai.com`
- GitHub 组织: `https://github.com/kunpeng-ai-research`
- OpenClaw: `https://openclaw.ai`

## 技术架构

### 核心文件

| 文件 | 职责 |
|------|------|
| `src/server/pixel_server.py` | HTTP API + tkinter GUI |
| `src/server/headless_server.py` | 无头模式（RDP）|
| `src/cli/weizheng_cli.py` | CLI 工具 |
| `src/core/agent.py` | Agent 核心逻辑 |
| `src/core/critic.py` | 审查引擎 |
| `src/ui/pixel_weizheng_v4.py` | 像素动画 V4 |

### OpenClaw Skill

- `skills/openclaw/weizheng_skill/hook.py` - Skill 钩子
- `skills/openclaw/weizheng_skill/SKILL.md` - Skill 元数据

### 关键实现

1. **RDP 兼容**: 使用 `LWA_COLORKEY` 而非 `LWA_ALPHA`
2. **气泡布局**: 在魏征上方（`bubble_frame.pack(side='top')`）
3. **轮播机制**: `msg_rotation_timer` + `msg_display_duration=3000`
4. **后台运行**: `pythonw.exe` 无控制台窗口

## 开发规范

### 代码风格

- Python 类型注解
- 中文注释 + ASCII 符号（避免编码问题）
- 函数文档字符串

### 提交规范

```
feat: 新功能
fix: 修复
docs: 文档
refactor: 重构
```

### 测试流程

```bash
# 1. 环境验证
python verify_setup.py

# 2. 启动测试
python -m src.server

# 3. CLI 测试
python -m src.cli talk "测试"
python -m src.cli stop

# 4. 完整测试
python test_complete_flow.py
```

## 部署方式

| 方式 | 命令 | 场景 |
|------|------|------|
| 后台 | `start_background.bat` | 日常使用 |
| 无头 | `python src/server/headless_server.py` | RDP/服务器 |
| 托盘 | `python run_with_tray.py` | 需要 GUI 控制 |

## 故障排查

### RDP 不显示
- 使用无头模式
- 检查 `fix_window_for_rdp_colorkey`

### 端口占用
```bash
netstat -ano | findstr 7788
```

### Skill 不触发
1. 检查符号链接: `~/.openclaw/skills/weizheng`
2. 检查服务器状态
3. 查看 OpenClaw 日志

## 文档清单

- `README.md` - 主文档（必须包含品牌署名）
- `docs/OPENCLAW_INTEGRATION.md` - OpenClaw 集成
- `docs/DEPLOYMENT.md` - 部署指南
- `CHANGELOG.md` - 更新日志
- `HANDOFF.md` - 交接规则
- `LICENSE` - MIT 许可证

## 外部依赖

- `Pillow` - 图像处理（必须）
- `pystray` - 系统托盘（可选）

## 记住

1. **永远使用**: 鲲鹏AI探索局 + kunpeng-ai.com
2. **测试 RDP**: 任何 GUI 修改都要测试 RDP 兼容性
3. **保持兼容**: OpenClaw Skill API 不能随意更改
4. **更新日志**: 每次修改都要更新 CHANGELOG.md

---

**维护组织**: 鲲鹏AI探索局
**主站**: https://kunpeng-ai.com
**创建**: 2026-04-10
