#!/usr/bin/env bash
# Quick setup script for Claude Code Custom Provider
set -e

echo "=== Claude Code Custom Provider Setup ==="
echo ""

# ── Check Python ──
if ! command -v python3 &>/dev/null; then
    echo "✗ python3 not found. Install Python 3.8+ first."
    exit 1
fi
echo "✓ python3 $(python3 --version)"

# ── Provider config ──
if [ -z "$PROVIDER_API_KEY" ]; then
    echo ""
    echo "Select your provider:"
    echo "  1) DeepSeek"
    echo "  2) OpenAI"
    echo "  3) Groq"
    echo "  4) Custom (enter URL)"
    echo "  5) YAPI / New-API (aggregator)"
    read -p "Choice [1-5]: " choice

    case $choice in
        1)
            PROVIDER_BASE_URL="https://api.deepseek.com/v1"
            DEFAULT_MODEL="deepseek-chat"
            ;;
        2)
            PROVIDER_BASE_URL="https://api.openai.com/v1"
            DEFAULT_MODEL="gpt-4o"
            ;;
        3)
            PROVIDER_BASE_URL="https://api.groq.com/v1"
            DEFAULT_MODEL="llama-3.3-70b-versatile"
            ;;
        4)
            read -p "Base URL (e.g. https://api.xxx.com/v1): " PROVIDER_BASE_URL
            read -p "Model name: " DEFAULT_MODEL
            ;;
        5)
            read -p "Base URL (e.g. https://your-api.click/v1): " PROVIDER_BASE_URL
            read -p "Model name: " DEFAULT_MODEL
            ;;
        *)
            echo "Invalid choice."
            exit 1
            ;;
    esac

    read -sp "API Key: " PROVIDER_API_KEY
    echo ""
    read -p "Model [$DEFAULT_MODEL]: " model_input
    PROVIDER_MODEL="${model_input:-$DEFAULT_MODEL}"

    echo ""
    read -p "Save to ~/.claude-proxy.env for auto-start? [y/N]: " save
    if [ "$save" = "y" ] || [ "$save" = "Y" ]; then
        cat > ~/.claude-proxy.env <<EOF
PROVIDER_BASE_URL=$PROVIDER_BASE_URL
PROVIDER_API_KEY=***
PROVIDER_MODEL=$PROVIDER_MODEL
EOF
        chmod 600 ~/.claude-proxy.env
        echo "✓ Saved to ~/.claude-proxy.env"
    fi
fi

# ── Start proxy ──
if [ -f ~/.claude-proxy.env ]; then
    source ~/.claude-proxy.env
fi

export PROVIDER_BASE_URL PROVIDER_API_KEY PROVIDER_MODEL

echo ""
echo "Starting proxy on http://127.0.0.1:15721 ..."
echo "  Provider: $PROVIDER_BASE_URL"
echo "  Model:    $PROVIDER_MODEL"
echo ""
echo "Now configure Claude Code:"
echo ""
echo "  VSCode (settings.json):"
echo '    "claudeCode.model": "claude-sonnet-4-5"'
echo '    "claudeCode.environmentVariables": ['
echo '      {"name":"ANTHROPIC_BASE_URL","value":"http://127.0.0.1:15721"},'
echo '      {"name":"ANTHROPIC_AUTH_TOKEN","value":"any"}'
echo '    ]'
echo ""
echo "  CLI (~/.claude/settings.json):"
echo '    "env": {'
echo '      "ANTHROPIC_BASE_URL": "http://127.0.0.1:15721",'
echo '      "ANTHROPIC_AUTH_TOKEN": "any"'
echo '    }'
echo ""

exec python3 "$(dirname "$0")/proxy.py"
