---
name: weizheng
description: 魏征 Agent - 专门提反对意见、挑毛病的批判型 Agent
when_to_use: 
  - 需要代码审查时
  - 需要文案审查时  
  - 需要计划/方案审查时
  - 需要独立第三方意见时
triggers:
  - "魏征，你怎么看？"
  - "魏征，有何高见？"
  - "魏征，点评一下？"
  - "@魏征"
version: "1.0"
---

# 魏征 Agent Skill

## 简介

魏征是一个独立的批判型 AI Agent，专门负责提反对意见、挑毛病。

当用户说"魏征，你怎么看？"时，本 Skill 会：
1. 调用魏征子 Agent 生成审查意见
2. 触发像素魏征动画（屏幕右下角）
3. 以魏征身份回复用户
4. 动画结束后自动停止

## 依赖

- 魏征像素服务端必须正在运行（端口 7788）
- CLI 工具：`python -m src.cli`

## 使用方法

### 启动像素服务端

```bash
# 在项目根目录运行
python -m src.server
```

### 在 OpenClaw 中使用

用户输入：
```
这段代码怎么样？
def add(a, b):
    return a + b

魏征，你怎么看？
```

OpenClaw 会自动调用本 Skill，你会看到：
1. 屏幕右下角像素魏征开始说话动画
2. 魏征生成并显示审查意见
3. 动画自动停止

## 配置

在 `.openclaw/skills/weizheng/config.json` 中配置：

```json
{
  "server_host": "localhost",
  "server_port": 7788,
  "cli_path": "python -m src.cli",
  "default_duration": 3.0
}
```

## API

本 Skill 提供以下工具给 OpenClaw：

- `weizheng_critique(content, context_type)` - 生成审查意见
- `weizheng_talk(message, duration)` - 触发像素动画
- `weizheng_stop()` - 停止像素动画

## 故障排除

### 像素魏征不出现

检查服务端是否运行：
```bash
curl http://localhost:7788/api/status
```

### CLI 调用失败

检查 CLI 工具：
```bash
python -m src.cli status
```

### 动画不触发

检查服务端日志，确认收到 HTTP 请求

## 链接

- 项目地址：https://github.com/your-username/weizheng-agent
- 文档：docs/
