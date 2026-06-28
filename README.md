# Claude Code Custom Provider Proxy

> **Use Claude Code with ANY LLM.** DeepSeek, Qwen, Groq, Ollama — if it speaks OpenAI API, it works.

Claude Code locks you into Anthropic models. This 150-line proxy breaks the lock. It sits between Claude Code and your API provider, translating model names on the fly. Claude Code thinks it's talking to Anthropic. You're actually using whatever model you want.

## One-Liner

```bash
PROVIDER_BASE_URL="https://api.deepseek.com/v1" \
PROVIDER_API_KEY="***" \
PROVIDER_MODEL="deepseek-chat" \
python3 <(curl -sSL https://raw.githubusercontent.com/jade2-fff/-claude-code-custom-provider/master/proxy.py)
```

That's it. No clone, no pip, no config files. Just set your own env vars and run.

Then point Claude Code at the proxy:

**VSCode** (`Ctrl+,` → search `claudeCode`):
```json
{
  "claudeCode.model": "claude-sonnet-4-5",
  "claudeCode.environmentVariables": [
    { "name": "ANTHROPIC_BASE_URL", "value": "http://127.0.0.1:8080" },
    { "name": "ANTHROPIC_AUTH_TOKEN", "value": "any" }
  ]
}
```

**CLI** (`~/.claude/settings.json`):
```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "http://127.0.0.1:8080",
    "ANTHROPIC_AUTH_TOKEN": "any"
  }
}
```

Reload VSCode, then `claude --model claude-sonnet-4-5`. Done.

> Change `8080` to whatever port you want with `LISTEN_PORT=8080`.

## How It Works

```
┌─────────────┐     ┌──────────────┐     ┌────────────────┐
│  Claude Code │ ──▶ │   proxy.py   │ ──▶ │  Your Provider │
│             │     │              │     │                │
│  model:     │     │  translate   │     │  model:        │
│  claude-    │     │  claude-* →  │     │  deepseek-chat │
│  sonnet-4-5 │     │  your model  │     │  (or whatever) │
└─────────────┘     └──────────────┘     └────────────────┘
```

- `GET /v1/models` → returns fake Claude model list to pass Claude Code's model validation
- `POST /v1/messages` → replaces any `claude-*` model name with your `PROVIDER_MODEL`
- Everything else → forwarded transparently

## Supported Providers

Any OpenAI-compatible API. Here are ready-to-copy configs:

| Provider | `PROVIDER_BASE_URL` | `PROVIDER_MODEL` |
|---|---|---|
| **DeepSeek** | `https://api.deepseek.com/v1` | `deepseek-chat` |
| **DeepSeek V4 Pro** | `https://api.deepseek.com/v1` | `deepseek-v4-pro` |
| **Zhipu GLM** | `https://open.bigmodel.cn/api/paas/v4` | `glm-4-plus` |
| **Qwen (通义千问)** | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-plus` |
| **OpenAI** | `https://api.openai.com/v1` | `gpt-4o` |
| **Groq** | `https://api.groq.com/openai/v1` | `llama-3.3-70b-versatile` |
| **Ollama (local)** | `http://localhost:11434/v1` | `llama3.2` |
| **vLLM (local)** | `http://localhost:8000/v1` | `your-model` |
| **YAPI / New-API** | `https://your-yapi.click/v1` | `your-model` |
| **OpenRouter** | `https://openrouter.ai/api/v1` | `openai/gpt-4o` |
| **Together AI** | `https://api.together.xyz/v1` | `meta-llama/Llama-3.3-70B` |
| **SiliconFlow** | `https://api.siliconflow.cn/v1` | `deepseek-ai/DeepSeek-V3` |
| **Moonshot** | `https://api.moonshot.cn/v1` | `moonshot-v1-8k` |
| **MiniMax** | `https://api.minimax.chat/v1` | `abab6.5s-chat` |
| **StepFun** | `https://api.stepfun.com/v1` | `step-1-8k` |
| **Baichuan** | `https://api.baichuan-ai.com/v1` | `Baichuan4` |
| **Doubao (豆包)** | `https://ark.cn-beijing.volces.com/api/v3` | `your-endpoint-id` |

> Don't see yours? If it has an OpenAI-compatible `/v1/chat/completions` endpoint, it works.

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `PROVIDER_BASE_URL` | Yes | — | Provider API base URL |
| `PROVIDER_API_KEY` | Yes | — | Your API key |
| `PROVIDER_MODEL` | No | `gpt-4o` | Model name to use |
| `LISTEN_HOST` | No | `127.0.0.1` | Listen address |
| `LISTEN_PORT` | No | `8080` | Listen port |

## Why Not Just Set ANTHROPIC_BASE_URL?

You can point Claude Code at any Anthropic-compatible endpoint by setting `ANTHROPIC_BASE_URL`. That works — **if** the provider uses the same `/v1/messages` Anthropic format and **if** Claude Code doesn't reject the model name.

The problem: Claude Code validates model names. Set `ANTHROPIC_MODEL=deepseek-chat` and Claude Code says *"There's an issue with the selected model. It may not exist."* This proxy solves that by lying about `/v1/models` and translating model names.

## Auto-Start on Boot (systemd)

```bash
cat << 'EOF' > ~/.config/systemd/user/claude-proxy.service
[Unit]
Description=Claude Code Provider Proxy
After=network.target

[Service]
ExecStart=/usr/bin/python3 /path/to/proxy.py
Environment=PROVIDER_BASE_URL=https://api.deepseek.com/v1
Environment=PROVIDER_API_KEY=***
E...EOF

systemctl --user daemon-reload
systemctl --user enable --now claude-proxy
```

## Comparison

| | Proxy (this project) | ANTHROPIC_BASE_URL alone | CC-Switch |
|---|---|---|---|
| Works with VSCode | ✅ | ❌ (model rejection) | ✅ |
| Works with CLI | ✅ | ⚠️ (model-dependent) | ✅ |
| Any OpenAI-compatible API | ✅ | ❌ (needs Anthropic format) | ✅ |
| Lines of code | ~150 | 0 | 50,000+ |
| Dependencies | Python stdlib only | — | Electron app |
| Setup time | 30 seconds | ❌ (doesn't work) | 10+ minutes |

## FAQ

**Q: Are thinking/reasoning models supported?**  
Yes. DeepSeek-R1, o1-style models work. The proxy forwards SSE streams transparently. Note: reasoning models spend tokens on internal thinking — make sure your `max_tokens` is high enough for both thinking and the final answer.

**Q: Does this work with Claude Code's tool use?**  
Yes. Tool definitions, system prompts, multi-turn conversations — all forwarded as-is.

**Q: Is this against Anthropic's ToS?**  
This tool doesn't touch Anthropic's servers. It only connects Claude Code to third-party APIs using your own keys. You're responsible for compliance with those third-party providers.

**Q: What about rate limits?**  
Claude Code's own rate limiting is bypassed. Your provider's rate limits apply.

## License

MIT
