# 🐈 nanobot Unraid 部署指南

## 📦 自动构建

本仓库 Fork 自 [HKUDS/nanobot](https://github.com/HKUDS/nanobot)，添加了：
- ✅ GitHub Actions 每日自动同步上游并构建 Docker 镜像
- ✅ Unraid Docker 模板

镜像地址：`ghcr.io/nonewind/nanobot:latest`

## 🚀 Unraid 快速部署

### 方式一：使用模板

1. 在 Unraid Docker 页面，点击 **Add Container**
2. 点击 **Template** → **Add Template**
3. 输入模板 URL：
   ```
   https://raw.githubusercontent.com/nonewind/nanobot/main/unraid/nanobot.xml
   ```
4. 填写配置参数，点击 **Apply**

### 方式二：命令行

```bash
docker run -d \
  --name nanobot \
  --restart=unless-stopped \
  -v /mnt/user/appdata/nanobot:/root/.nanobot \
  -p 18790:18790 \
  -e TZ=Asia/Shanghai \
  ghcr.io/nonewind/nanobot:latest \
  gateway
```

## ⚙️ 配置 Telegram + Qwen

编辑 `/mnt/user/appdata/nanobot/config.json`：

```json
{
  "agents": {
    "defaults": {
      "model": "qwen-max"
    }
  },
  "channels": {
    "telegram": {
      "enabled": true,
      "token": "YOUR_TELEGRAM_BOT_TOKEN",
      "allowFrom": ["YOUR_TELEGRAM_USER_ID"],
      "proxy": "http://YOUR_PROXY:PORT"
    }
  },
  "providers": {
    "dashscope": {
      "apiKey": "YOUR_DASHSCOPE_API_KEY"
    }
  }
}
```

## 🔑 获取 API Keys

| 服务 | 获取地址 |
|------|----------|
| DashScope (Qwen) | https://dashscope.console.aliyun.com |
| Telegram Bot | @BotFather |

## 🔄 更新镜像

```bash
docker pull ghcr.io/nonewind/nanobot:latest
docker restart nanobot
```
