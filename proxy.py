#!/usr/bin/env python3
"""
Claude Code Custom Provider Proxy

A lightweight HTTP proxy that lets Claude Code (CLI or VSCode extension) use
any OpenAI-compatible API provider by translating model names on the fly.

Claude Code only accepts Anthropic model names (claude-sonnet-4-5, etc.).
This proxy sits between Claude Code and your provider, translating Claude model
names to your provider's model names and forwarding requests.

Usage:
    export PROVIDER_BASE_URL="https://your-api.com/v1"
    export PROVIDER_API_KEY="sk-xxx"
    export PROVIDER_MODEL="gpt-4o"          # optional, default: gpt-4o
    python3 proxy.py

Then configure Claude Code:
    ANTHROPIC_BASE_URL=http://127.0.0.1:3456
    ANTHROPIC_AUTH_TOKEN=any-value
"""

import http.server
import urllib.request
import urllib.error
import json
import os
import sys

LISTEN_HOST = os.environ.get("LISTEN_HOST", "127.0.0.1")
LISTEN_PORT = int(os.environ.get("LISTEN_PORT", "8080"))

PROVIDER_BASE_URL = os.environ.get("PROVIDER_BASE_URL", "").rstrip("/")
PROVIDER_API_KEY = os.environ.get("PROVIDER_API_KEY", "")
PROVIDER_MODEL = os.environ.get("PROVIDER_MODEL", "gpt-4o")

if not PROVIDER_BASE_URL or not PROVIDER_API_KEY:
    print("Error: PROVIDER_BASE_URL and PROVIDER_API_KEY must be set", file=sys.stderr)
    print("Example:", file=sys.stderr)
    print("  export PROVIDER_BASE_URL=https://api.openai.com/v1", file=sys.stderr)
    print("  export PROVIDER_API_KEY=sk-xxx", file=sys.stderr)
    print("  export PROVIDER_MODEL=gpt-4o", file=sys.stderr)
    sys.exit(1)

CLAUDE_MODELS = [
    "claude-sonnet-4-5",
    "claude-sonnet-4-6",
    "claude-opus-4-6",
    "claude-opus-4-7",
    "claude-opus-4-8",
    "claude-haiku-4-5",
    "claude-3-5-sonnet-20241022",
]


class Proxy(http.server.BaseHTTPRequestHandler):
    """HTTP proxy that translates Claude model names to custom provider models."""

    def log_message(self, format, *args):
        print(f"[proxy] {args[0]}", flush=True)

    # ── GET ──────────────────────────────────────────────────────────

    def do_GET(self):
        if self.path == "/v1/models" or self.path == "/v1/models/":
            self._fake_models()
            return

        # Forward everything else
        self._forward("GET")

    def _fake_models(self):
        """Return a fake model list with Claude model names to satisfy validation."""
        data = {
            "object": "list",
            "data": [{"id": m, "object": "model", "created": 1, "owned_by": "anthropic"}
                     for m in CLAUDE_MODELS],
        }
        self._json_response(200, data)

    # ── POST ─────────────────────────────────────────────────────────

    def do_POST(self):
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len) if content_len else b""

        # Translate model name if this looks like an Anthropic chat request
        if "/messages" in self.path and body:
            try:
                data = json.loads(body)
                model = data.get("model", "")
                if model.startswith("claude-"):
                    data["model"] = PROVIDER_MODEL
                    body = json.dumps(data).encode()
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass  # not JSON, forward as-is

        self._forward("POST", body)

    # ── OPTIONS ──────────────────────────────────────────────────────

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    # ── Internal ─────────────────────────────────────────────────────

    def _forward(self, method, body=None):
        # Strip common API prefix from path to avoid double /v1
        # e.g. PROVIDER_BASE_URL=https://api.com/v1, path=/v1/messages → /messages
        path = self.path
        if PROVIDER_BASE_URL.endswith("/v1") and path.startswith("/v1"):
            path = path[3:]  # strip leading /v1
        url = f"{PROVIDER_BASE_URL}{path}"
        req = urllib.request.Request(url, data=body, method=method)

        # Pass through relevant client headers
        for h in ["anthropic-version", "anthropic-beta", "content-type"]:
            v = self.headers.get(h)
            if v:
                req.add_header(h, v)

        # Authenticate with the upstream provider
        req.add_header("Authorization", f"Bearer {PROVIDER_API_KEY}")

        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                self.send_response(resp.status)
                ct = resp.headers.get("Content-Type", "application/octet-stream")
                self.send_header("Content-Type", ct)
                self.end_headers()
                # Stream the response
                while True:
                    chunk = resp.read(65536)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    self.wfile.flush()
        except urllib.error.HTTPError as e:
            body = e.read()
            self.send_response(e.code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)
        except Exception as e:
            self._json_response(502, {"error": str(e)})

    def _json_response(self, status, data):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())


def main():
    """Entry point for console_scripts."""
    server = http.server.HTTPServer((LISTEN_HOST, LISTEN_PORT), Proxy)
    print(f"Claude Code Custom Provider Proxy", flush=True)
    print(f"  Listening: http://{LISTEN_HOST}:{LISTEN_PORT}", flush=True)
    print(f"  Provider:  {PROVIDER_BASE_URL}", flush=True)
    print(f"  Model:     {PROVIDER_MODEL}", flush=True)
    print(f"  Ready.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.", flush=True)


if __name__ == "__main__":
    main()
