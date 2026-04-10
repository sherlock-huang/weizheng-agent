# 大模型配置指南

## 支持的模型

魏征 Agent 支持以下大模型：

### 1. Moonshot AI (Kimi) - 推荐
- 官网: https://platform.moonshot.cn
- 特点: 中文优化，价格实惠
- 模型: `moonshot-v1-8k`, `moonshot-v1-32k`

### 2. OpenAI (GPT)
- 官网: https://platform.openai.com
- 特点: 功能强大
- 模型: `gpt-4`, `gpt-3.5-turbo`

### 3. Anthropic (Claude)
- 官网: https://console.anthropic.com
- 特点: 擅长长文本
- 模型: `claude-3-sonnet`, `claude-3-opus`

### 4. 本地模型 (Ollama)
- 官网: https://ollama.com
- 特点: 免费，本地运行
- 模型: `llama2`, `codellama` 等

## 快速配置

### 方式1: 环境变量

```bash
# Moonshot (推荐)
export LLM_PROVIDER="moonshot"
export LLM_API_KEY="sk-your-moonshot-key"
export LLM_MODEL="moonshot-v1-8k"

# OpenAI
export LLM_PROVIDER="openai"
export LLM_API_KEY="sk-your-openai-key"
export LLM_MODEL="gpt-4"

# Claude
export LLM_PROVIDER="anthropic"
export LLM_API_KEY="sk-ant-your-key"
export LLM_MODEL="claude-3-sonnet-20240229"
```

### 方式2: 配置文件

创建 `config.json`:

```json
{
  "llm": {
    "provider": "moonshot",
    "api_key": "sk-your-key",
    "model": "moonshot-v1-8k",
    "temperature": 0.7,
    "max_tokens": 2000
  }
}
```

## 测试连接

```bash
python -c "
from src.integrations.llm import get_llm_client
llm = get_llm_client()
result = llm.generate_critique('测试内容', 'general', 'medium')
print(result['agent_personality'])
"
```

## 魏征专用提示词

大模型使用的系统提示词已针对魏征角色优化：

- 身份：唐太宗时期谏臣
- 任务：挑毛病、提反对意见
- 风格：文言文风格的现代中文
- 原则：必须找出问题，不能全盘肯定

可以在 `src/integrations/llm.py` 中修改 `system_prompt`
