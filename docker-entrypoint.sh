#!/bin/bash
set -e

CONFIG_FILE="/root/.nanobot/config.json"
WORKSPACE_DIR="/root/.nanobot/workspace"

# 创建目录
mkdir -p /root/.nanobot
mkdir -p "$WORKSPACE_DIR"

# 如果配置文件不存在，或者设置了 NANOBOT_FORCE_CONFIG=true，则生成配置
if [ ! -f "$CONFIG_FILE" ] || [ "$NANOBOT_FORCE_CONFIG" = "true" ]; then
    echo "🐈 Generating config.json from environment variables..."
    
    # 使用 Python 生成配置文件，自动读取环境变量
    python3 << 'PYTHON_SCRIPT'
import json
import os

config = {
    "agents": {
        "defaults": {
            "workspace": "~/.nanobot/workspace",
            "model": os.environ.get("NANOBOT_MODEL", "qwen-plus"),
            "maxTokens": int(os.environ.get("NANOBOT_MAX_TOKENS", "8192")),
            "temperature": float(os.environ.get("NANOBOT_TEMPERATURE", "0.7")),
            "maxToolIterations": int(os.environ.get("NANOBOT_MAX_TOOL_ITERATIONS", "20"))
        }
    },
    "channels": {
        "telegram": {
            "enabled": bool(os.environ.get("TELEGRAM_BOT_TOKEN", "")),
            "token": os.environ.get("TELEGRAM_BOT_TOKEN", ""),
            "allowFrom": [x.strip() for x in os.environ.get("TELEGRAM_ALLOW_FROM", "").split(",") if x.strip()],
            "proxy": os.environ.get("TELEGRAM_PROXY") or None
        },
        "whatsapp": {
            "enabled": False,
            "bridgeUrl": "ws://localhost:3001",
            "allowFrom": []
        },
        "discord": {
            "enabled": bool(os.environ.get("DISCORD_BOT_TOKEN", "")),
            "token": os.environ.get("DISCORD_BOT_TOKEN", ""),
            "allowFrom": [x.strip() for x in os.environ.get("DISCORD_ALLOW_FROM", "").split(",") if x.strip()]
        },
        "feishu": {
            "enabled": bool(os.environ.get("FEISHU_APP_ID", "")),
            "appId": os.environ.get("FEISHU_APP_ID", ""),
            "appSecret": os.environ.get("FEISHU_APP_SECRET", ""),
            "allowFrom": []
        },
        "dingtalk": {
            "enabled": bool(os.environ.get("DINGTALK_CLIENT_ID", "")),
            "clientId": os.environ.get("DINGTALK_CLIENT_ID", ""),
            "clientSecret": os.environ.get("DINGTALK_CLIENT_SECRET", ""),
            "allowFrom": []
        }
    },
    "providers": {
        "dashscope": {
            "apiKey": os.environ.get("DASHSCOPE_API_KEY", ""),
            "apiBase": os.environ.get("DASHSCOPE_API_BASE") or None
        },
        "openrouter": {
            "apiKey": os.environ.get("OPENROUTER_API_KEY", ""),
            "apiBase": os.environ.get("OPENROUTER_API_BASE") or None
        },
        "anthropic": {
            "apiKey": os.environ.get("ANTHROPIC_API_KEY", ""),
            "apiBase": os.environ.get("ANTHROPIC_API_BASE") or None
        },
        "openai": {
            "apiKey": os.environ.get("OPENAI_API_KEY", ""),
            "apiBase": os.environ.get("OPENAI_API_BASE") or None
        },
        "deepseek": {
            "apiKey": os.environ.get("DEEPSEEK_API_KEY", ""),
            "apiBase": os.environ.get("DEEPSEEK_API_BASE") or None
        },
        "moonshot": {
            "apiKey": os.environ.get("MOONSHOT_API_KEY", ""),
            "apiBase": os.environ.get("MOONSHOT_API_BASE") or None
        },
        "zhipu": {
            "apiKey": os.environ.get("ZHIPU_API_KEY", ""),
            "apiBase": os.environ.get("ZHIPU_API_BASE") or None
        },
        "groq": {
            "apiKey": os.environ.get("GROQ_API_KEY", ""),
            "apiBase": os.environ.get("GROQ_API_BASE") or None
        },
        "vllm": {
            "apiKey": os.environ.get("VLLM_API_KEY", "dummy"),
            "apiBase": os.environ.get("VLLM_API_BASE") or None
        }
    },
    "gateway": {
        "host": "0.0.0.0",
        "port": int(os.environ.get("NANOBOT_PORT", "18790"))
    },
    "tools": {
        "web": {
            "search": {
                "apiKey": os.environ.get("BRAVE_SEARCH_API_KEY", ""),
                "maxResults": int(os.environ.get("BRAVE_SEARCH_MAX_RESULTS", "5"))
            }
        },
        "exec": {
            "timeout": int(os.environ.get("NANOBOT_EXEC_TIMEOUT", "60"))
        },
        "restrictToWorkspace": os.environ.get("NANOBOT_RESTRICT_WORKSPACE", "false").lower() == "true"
    }
}

with open("/root/.nanobot/config.json", "w") as f:
    json.dump(config, f, indent=2)

print("✓ Config file generated successfully")
PYTHON_SCRIPT

fi

# 初始化 workspace（如果不存在必要文件）
if [ ! -f "$WORKSPACE_DIR/AGENTS.md" ]; then
    echo "🐈 Initializing workspace..."
    nanobot onboard --skip-config 2>/dev/null || true
fi

# 显示状态
echo "🐈 nanobot starting..."
echo "   Config: $CONFIG_FILE"
echo "   Model: ${NANOBOT_MODEL:-qwen-plus}"

# 执行传入的命令（默认是 gateway）
exec nanobot "$@"
