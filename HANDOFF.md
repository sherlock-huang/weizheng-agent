# 项目交接与长期维护规则

## 项目信息

- **项目名称**: 魏征 Agent (Weizheng Agent)
- **GitHub 仓库**: https://github.com/sherlock-huang/weizheng-agent
- **维护组织**: 鲲鹏AI探索局

## 品牌与署名规则（必须遵守）

### README 署名规范

所有 GitHub 仓库的 README 必须包含以下格式：

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

### 规则要点

1. **署名必须是**: 【鲲鹏AI探索局】
2. **主站链接必须是**: https://kunpeng-ai.com
3. **GitHub 组织链接**: https://github.com/kunpeng-ai-research
4. **OpenClaw 官方**: https://openclaw.ai

## 技术架构

### 核心组件

- `src/server/pixel_server.py` - 像素服务器（HTTP API + GUI）
- `src/cli/weizheng_cli.py` - CLI 工具
- `src/core/agent.py` - Agent 核心
- `src/ui/pixel_weizheng_v4.py` - 像素动画 V4

### OpenClaw Skill

- `skills/openclaw/weizheng_skill/hook.py` - Skill Hook
- `skills/openclaw/weizheng_skill/SKILL.md` - Skill 配置

## 关键功能

1. **像素动画**: 140x140px，8帧待机 + 8帧说话
2. **气泡对话框**: 集成在窗口内，多句话轮播
3. **OpenClaw 集成**: 自动检测触发词
4. **RDP 兼容**: Win32 API LWA_COLORKEY 透明
5. **后台运行**: pythonw.exe 无窗口模式

## 部署方式

- 后台: `start_background.bat` 或 `pythonw -m src.server`
- 无头: `python src/server/headless_server.py`
- 托盘: `python run_with_tray.py`

## 更新注意事项

1. 修改代码后必须更新 `CHANGELOG.md`
2. 保持 README 署名和链接不变
3. 测试 RDP 兼容性
4. 提交前运行 `verify_setup.py`

## 联系方式

- 主站: https://kunpeng-ai.com
- GitHub: https://github.com/kunpeng-ai-research

---

**创建时间**: 2026-04-10
**维护者**: 鲲鹏AI探索局
