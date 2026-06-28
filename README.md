1|# Claude Code Custom Provider Proxy
2|
3|> **Use Claude Code with ANY LLM.** DeepSeek, Qwen, Groq, Ollama — if it speaks OpenAI API, it works.
4|
5|Claude Code locks you into Anthropic models. This 150-line proxy breaks the lock. It sits between Claude Code and your API provider, translating model names on the fly. Claude Code thinks it's talking to Anthropic. You're actually using whatever model you want.
6|
7|## 30-Second Setup
8|
9|```bash
10|git clone https://github.com/jade2-fff/-claude-code-custom-provider
11|cd -claude-code-custom-provider
12|
13|# Pick your provider:
14|export PROVIDER_BASE_URL="https://api.deepseek.com/v1"
15|export PROVIDER_API_KEY="***"or"
16|export PROVIDER_MODEL="deepseek-chat"
17|
18|python3 proxy.py
19|# → Listening on http://127.0.0.1:15721
20|```
21|
22|Then point Claude Code at `http://127.0.0.1:15721`:
23|
24|**VSCode** (`Ctrl+,` → search `claudeCode`):
25|```json
26|{
27|  "claudeCode.model": "claude-sonnet-4-5",
28|  "claudeCode.environmentVariables": [
29|    { "name": "ANTHROPIC_BASE_URL", "value": "http://127.0.0.1:15721" },
30|    { "name": "ANTHROPIC_AUTH_TOKEN", "value": "any" }
31|  ]
32|}
33|```
34|
35|**CLI** (`~/.claude/settings.json`):
36|```json
37|{
38|  "env": {
39|    "ANTHROPIC_BASE_URL": "http://127.0.0.1:15721",
40|    "ANTHROPIC_AUTH_TOKEN": "any"
41|  }
42|}
43|```
44|
45|Reload VSCode, then `claude --model claude-sonnet-4-5`. Done.
46|
47|## How It Works
48|
49|```
50|┌─────────────┐     ┌──────────────┐     ┌────────────────┐
51|│  Claude Code │ ──▶ │   proxy.py   │ ──▶ │  Your Provider │
52|│             │     │              │     │                │
53|│  model:     │     │  translate   │     │  model:        │
54|│  claude-    │     │  claude-* →  │     │  deepseek-chat │
55|│  sonnet-4-5 │     │  your model  │     │  (or whatever) │
56|└─────────────┘     └──────────────┘     └────────────────┘
57|```
58|
59|- `GET /v1/models` → returns fake Claude model list to pass Claude Code's model validation
60|- `POST /v1/messages` → replaces any `claude-*` model name with your `PROVIDER_MODEL`
61|- Everything else → forwarded transparently
62|
63|## Supported Providers
64|
65|Any OpenAI-compatible API. Here are ready-to-copy configs:
66|
67|| Provider | PROVIDER_BASE_URL | PROVIDER_MODEL |
68||---|---|---|
69|| **DeepSeek** | `https://api.deepseek.com/v1` | `deepseek-chat` |
70|| **DeepSeek V4 Pro** | `https://api.deepseek.com/v1` | `deepseek-v4-pro` |
71|| **Zhipu GLM** | `https://open.bigmodel.cn/api/paas/v4` | `glm-4-plus` |
73|| **Qwen (通义千问)** | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-plus` |
74|| **Qwen Max** | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-max` |
75|| **OpenAI** | `https://api.openai.com/v1` | `gpt-4o` |
76|| **Groq** | `https://api.groq.com/openai/v1` | `llama-3.3-70b-versatile` |
77|| **Groq (fast)** | `https://api.groq.com/openai/v1` | `deepseek-r1-distill-llama-70b` |
78|| **Ollama (local)** | `http://localhost:11434/v1` | `llama3.2` |
79|| **vLLM (local)** | `http://localhost:8000/v1` | `your-model-name` |
80|| **YAPI / New-API** | `https://your-yapi.click/v1` | `any-model-on-your-key` |
81|| **OpenRouter** | `https://openrouter.ai/api/v1` | `openai/gpt-4o` |
82|| **Together AI** | `https://api.together.xyz/v1` | `meta-llama/Llama-3.3-70B-Instruct-Turbo` |
83|| **SiliconFlow** | `https://api.siliconflow.cn/v1` | `deepseek-ai/DeepSeek-V3` |
84|| **Moonshot (月之暗面)** | `https://api.moonshot.cn/v1` | `moonshot-v1-8k` |
85|| **MiniMax** | `https://api.minimax.chat/v1` | `abab6.5s-chat` |
86|| **StepFun (阶跃星辰)** | `https://api.stepfun.com/v1` | `step-1-8k` |
87|| **Baichuan (百川)** | `https://api.baichuan-ai.com/v1` | `Baichuan4` |
88|| **Doubao (豆包)** | `https://ark.cn-beijing.volces.com/api/v3` | `your-endpoint-id` |
89|
90|> Don't see yours? If it has an OpenAI-compatible `/v1/chat/completions` endpoint, it works.
91|
92|## Environment Variables
93|
94|| Variable | Required | Default | Description |
95||---|---|---|---|
96|| `PROVIDER_BASE_URL` | Yes | — | Provider API base URL (with `/v1`) |
97|| `PROVIDER_API_KEY` | Yes | — | Your API key |
98|| `PROVIDER_MODEL` | No | `gpt-4o` | Model name to use |
99|| `LISTEN_HOST` | No | `127.0.0.1` | Listen address |
100|| `LISTEN_PORT` | No | `15721` | Listen port |
101|
102|## Why Not Just Set ANTHROPIC_BASE_URL?
103|
104|You can point Claude Code at any Anthropic-compatible endpoint by setting `ANTHROPIC_BASE_URL`. That works — **if** the provider uses the same `/v1/messages` Anthropic format and **if** Claude Code doesn't reject the model name.
105|
106|The problem: Claude Code validates model names. Set `ANTHROPIC_MODEL=deepseek-chat` and Claude Code says *"There's an issue with the selected model. It may not exist."* This proxy solves that by lying about `/v1/models` and translating model names.
107|
108|## Auto-Start on Boot (systemd)
109|
110|```bash
111|cat << 'EOF' > ~/.config/systemd/user/claude-proxy.service
112|[Unit]
113|Description=Claude Code Provider Proxy
114|After=network.target
115|
116|[Service]
117|ExecStart=/usr/bin/python3 /home/YOU/-claude-code-custom-provider/proxy.py
118|Environment=PROVIDER_BASE_URL=https://api.deepseek.com/v1
119|Environment=PROVIDER_API_KEY=***
120|E...systemctl --user daemon-reload
121|systemctl --user enable --now claude-proxy
122|```
123|
124|## Comparison
125|
126|| | Proxy (this project) | ANTHROPIC_BASE_URL alone | CC-Switch |
127||---|---|---|---|
128|| Works with VSCode | ✅ | ❌ (model rejection) | ✅ |
129|| Works with CLI | ✅ | ⚠️ (model-dependent) | ✅ |
130|| Any OpenAI-compatible API | ✅ | ❌ (needs Anthropic format) | ✅ |
131|| Lines of code | ~150 | 0 | 50,000+ |
132|| Dependencies | Python stdlib only | — | Electron app |
133|| Setup time | 30 seconds | ❌ (doesn't work) | 10+ minutes |
134|
135|## FAQ
136|
137|**Q: Are thinking/reasoning models supported?**  
138|Yes. DeepSeek-R1, o1-style models work. The proxy forwards SSE streams transparently. Note: reasoning models spend tokens on internal thinking — make sure your `max_tokens` is high enough for both thinking and the final answer.
139|
140|**Q: Does this work with Claude Code's tool use?**  
141|Yes. Tool definitions, system prompts, multi-turn conversations — all forwarded as-is.
142|
143|**Q: Is this against Anthropic's ToS?**  
144|This tool doesn't touch Anthropic's servers. It only connects Claude Code to third-party APIs using your own keys. You're responsible for compliance with those third-party providers.
145|
146|**Q: What about rate limits?**  
147|Claude Code's own rate limiting is bypassed. Your provider's rate limits apply.
148|
149|## License
150|
151|MIT
152|