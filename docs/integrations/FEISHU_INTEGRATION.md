# 飞书集成指南

## 功能说明

将魏征 Agent 集成到飞书，实现：
1. 在飞书群里 @魏征 或说"魏征你怎么看"
2. 魏征读取群聊上下文 + OpenClaw 项目上下文
3. 魏征用AI大模型进行审查并回复到群里

## 配置步骤

### 1. 创建飞书应用

1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 创建企业自建应用
3. 记录 **App ID** 和 **App Secret**

### 2. 配置权限

在"权限管理"中添加以下权限：
- `im:chat:readonly` - 读取群聊信息
- `im:message:send` - 发送消息
- `im:message:readonly` - 读取消息

### 3. 订阅事件

在"事件订阅"中：
1. 开启加密（记录 Encrypt Key）
2. 设置请求 URL: `https://your-server.com/feishu/webhook`
3. 订阅事件：`im.message.receive_v1`

### 4. 配置环境变量

```bash
# 飞书配置
export FEISHU_APP_ID="cli_xxxxxxxxxx"
export FEISHU_APP_SECRET="xxxxxxxxxx"
export FEISHU_ENCRYPT_KEY="your-encrypt-key"
export FEISHU_VERIFICATION_TOKEN="your-token"

# 大模型配置
export LLM_PROVIDER="moonshot"  # 或 openai / anthropic
export LLM_API_KEY="your-api-key"
export LLM_MODEL="moonshot-v1-8k"

# OpenClaw 项目（可选）
export OPENCLAW_PROJECT="your-project-id"
```

### 5. 启动服务

```bash
python feishu_server.py
```

## 使用方式

在飞书群里：

```
用户A: 这个功能设计怎么样？
用户B: 我觉得还可以
你: @魏征 你怎么看？
魏征: 陛下，恕臣直言！此设计有以下问题...
```

## 工作原理

```
飞书消息
    ↓
飞书 Bot 接收
    ↓
提取群聊上下文（最近10条）
    ↓
读取 OpenClaw 项目记忆
    ↓
合并上下文
    ↓
LLM生成审查意见
    ↓
回复到飞书
    ↓
同步到 OpenClaw
```

## 文件说明

```
src/integrations/feishu.py     # 飞书Bot核心
feishu_server.py               # 飞书Webhook服务器
config.json                    # 配置文件
```

## 常见问题

**Q: 如何获取 App ID 和 Secret？**
A: 在飞书开放平台 -> 应用详情 -> 凭证和基础信息

**Q: 需要公网IP吗？**
A: 是的，飞书需要能访问到你的服务器。本地测试可使用 ngrok

**Q: 支持哪些大模型？**
A: 支持 OpenAI GPT、Claude、Moonshot(Kimi)、Azure OpenAI
