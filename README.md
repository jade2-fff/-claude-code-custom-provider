# Claude Code Custom Provider Proxy

Let Claude Code (CLI & VSCode) use **any** OpenAI-compatible API provider — DeepSeek, GLM, Qwen, Groq, local LLMs, etc.

Claude Code hard-codes Anthropic model names (`claude-sonnet-4-5`, etc.) and rejects anything it doesn't recognise. This proxy sits between Claude Code and your provider, translating model names on the fly so Claude Code thinks it's talking to Anthropic.

## Quick Start

```bash
# 1. Set your provider credentials
export PROVIDER_BASE_URL="https://your-api.com/v1"
export PROVIDER_API_KEY="your-api-key"
export PROVIDER_MODEL="your-model-name"    # default: gpt-4o

# 2. Start the proxy
python3 proxy.py
# Listening on http://127.0.0.1:15721
```

Then point Claude Code at the proxy:

**VSCode** (`settings.json`):
```json
{
  "claudeCode.model": "claude-sonnet-4-5",
  "claudeCode.environmentVariables": [
    { "name": "ANTHROPIC_BASE_URL", "value": "http://127.0.0.1:15721" },
    { "name": "ANTHROPIC_AUTH_TOKEN", "value": "any-value" }
  ]
}
```

**CLI** (`~/.claude/settings.json`):
```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "http://127.0.0.1:15721",
    "ANTHROPIC_AUTH_TOKEN": "any-value"
  }
}
```

```bash
claude --model claude-sonnet-4-5
```

## How It Works

```
Claude Code                    proxy.py                    Your Provider
──────────                    ────────                    ─────────────
POST /v1/messages      →     model="claude-sonnet-4-5"
model=claude-sonnet-4-5       ↓ translate                 
                              model="glm-5.2"        →    POST /v1/chat/completions
                                                           model=glm-5.2
                              ← response              ←    "Hello!"
← "Hello!"
```

- `GET /v1/models` → returns fake Claude model list to pass validation
- `POST /v1/messages` → replaces Claude model names with `PROVIDER_MODEL`
- Everything else forwarded as-is

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `PROVIDER_BASE_URL` | Yes | — | Your provider's API base URL |
| `PROVIDER_API_KEY` | Yes | — | Your provider's API key |
| `PROVIDER_MODEL` | No | `gpt-4o` | Model name sent to your provider |
| `LISTEN_HOST` | No | `127.0.0.1` | Proxy listen address |
| `LISTEN_PORT` | No | `15721` | Proxy listen port |

## Supported Providers

Any OpenAI-compatible API works. Tested with:

- **YAPI / New-API** (aggregators)
- **Zhipu GLM** (open.bigmodel.cn)
- **DeepSeek**
- **OpenAI**
- **Groq**
- **local** (ollama, vllm, llama.cpp)

## Claude Model Mapping

All Claude model names map to a single `PROVIDER_MODEL`:

| Claude Code model | → | Sent to provider |
|---|---|---|
| `claude-sonnet-4-5` | → | `PROVIDER_MODEL` |
| `claude-opus-4-7` | → | `PROVIDER_MODEL` |
| `claude-haiku-4-5` | → | `PROVIDER_MODEL` |
| ... any `claude-*` | → | `PROVIDER_MODEL` |

## Auto-Start (systemd)

```ini
# ~/.config/systemd/user/claude-proxy.service
[Unit]
Description=Claude Code Provider Proxy
After=network.target

[Service]
ExecStart=/usr/bin/python3 /path/to/proxy.py
Environment=PROVIDER_BASE_URL=https://your-api.com/v1
Environment=PROVIDER_API_KEY=***
Environment=PROVIDER_MODEL=gpt-4o
Restart=always

[Install]
WantedBy=default.target
```

```bash
systemctl --user daemon-reload
systemctl --user enable --now claude-proxy
```

## License

MIT
