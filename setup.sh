#!/usr/bin/env bash
# Rapid Setup: Claude Code Custom Provider Proxy
# 
# Usage:
#   export PROVIDER_BASE_URL="https://api.deepseek.com/v1"
#   export PROVIDER_API_KEY=***
#   export PROVIDER_MODEL="deepseek-chat"
#   bash setup.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ -z "$PROVIDER_API_KEY" ] || [ -z "$PROVIDER_BASE_URL" ]; then
    echo "Set your provider credentials first:"
    echo ""
    echo "  export PROVIDER_BASE_URL=\"https://api.deepseek.com/v1\""
    echo "  export PROVIDER_API_KEY=***"
    echo "  export PROVIDER_MODEL=\"deepseek-chat\""
    echo "  bash setup.sh"
    echo ""
    echo "See README for provider-specific configs."
    exit 1
fi

PORT="${LISTEN_PORT:-8080}"
PROVIDER_MODEL="${PROVIDER_MODEL:-gpt-4o}"

echo "=== Claude Code Custom Provider Proxy ==="
echo ""
echo "  Provider: $PROVIDER_BASE_URL"
echo "  Model:    $PROVIDER_MODEL"
echo "  Proxy:    http://127.0.0.1:$PORT"
echo ""
echo "Now point Claude Code at http://127.0.0.1:$PORT :"
echo ""
echo "  VSCode settings.json:"
echo "    \"claudeCode.model\": \"claude-sonnet-4-5\""
echo "    \"claudeCode.environmentVariables\": ["
echo "      {\"name\":\"ANTHROPIC_BASE_URL\",\"value\":\"http://127.0.0.1:$PORT\"},"
echo "      {\"name\":\"ANTHROPIC_AUTH_TOKEN\",\"value\":\"any\"}"
echo "    ]"
echo ""
echo "  CLI ~/.claude/settings.json:"
echo "    \"env\": {"
echo "      \"ANTHROPIC_BASE_URL\": \"http://127.0.0.1:$PORT\","
echo "      \"ANTHROPIC_AUTH_TOKEN\": \"any\""
echo "    }"
echo ""

exec python3 "$SCRIPT_DIR/proxy.py"
