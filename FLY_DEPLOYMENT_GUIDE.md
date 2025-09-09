# 🚀 Fly.io Deployment Guide - Read & Revive Bot

## 🎯 **Why Fly.io?**

Fly.io is the best **truly free** option because:
- ✅ **Completely FREE forever** - no payment required
- ✅ **No credit card needed**
- ✅ **Always-on** - no sleeping like Render
- ✅ **Persistent storage** for your SQLite database
- ✅ **Perfect for Telegram bots**

## 📋 **Prerequisites**

1. **Install flyctl** (Fly.io CLI):
   ```bash
   # Windows (PowerShell)
   iwr https://fly.io/install.ps1 -useb | iex
   
   # Or download from: https://fly.io/docs/hands-on/install-flyctl/
   ```

2. **Create Fly.io account**: Go to [fly.io](https://fly.io) and sign up

## 🚀 **Deployment Steps**

### Step 1: Prepare Your Project

1. **Create a `fly.toml` file** in your project root:
   ```toml
   app = "anbabi-bot"
   primary_region = "iad"

   [build]

   [env]
     BOT_TOKEN = ""
     ADMIN_USER_IDS = ""
     BOT_USERNAME = "anbabi_bot"
     LOG_LEVEL = "INFO"
     DATABASE_PATH = "/data/reading_tracker.db"

   [[mounts]]
     source = "anbabi_data"
     destination = "/data"

   [processes]
     app = "python main.py"

   [[services]]
     http_checks = []
     internal_port = 8080
     processes = ["app"]
     protocol = "tcp"
     script_checks = []

     [services.concurrency]
       hard_limit = 25
       soft_limit = 20
       type = "connections"

     [[services.ports]]
       force_https = true
       handlers = ["http"]
       port = 80

     [[services.ports]]
       handlers = ["tls", "http"]
       port = 443

     [[services.tcp_checks]]
       grace_period = "1s"
       interval = "15s"
       restart_limit = 0
       timeout = "2s"
   ```

### Step 2: Deploy to Fly.io

1. **Login to Fly.io**:
   ```bash
   fly auth login
   ```

2. **Initialize your app**:
   ```bash
   fly launch
   ```
   - Choose your app name (e.g., `anbabi-bot`)
   - Select region (e.g., `iad` for US East)
   - Don't deploy yet (we'll set env vars first)

3. **Set environment variables**:
   ```bash
   fly secrets set BOT_TOKEN=your_actual_bot_token
   fly secrets set ADMIN_USER_IDS=your_telegram_user_id
   ```

4. **Create persistent volume**:
   ```bash
   fly volumes create anbabi_data --region iad --size 1
   ```

5. **Deploy your bot**:
   ```bash
   fly deploy
   ```

### Step 3: Verify Deployment

1. **Check app status**:
   ```bash
   fly status
   ```

2. **View logs**:
   ```bash
   fly logs
   ```

3. **Test your bot**: Send `/start` to your bot on Telegram

## 🛠️ **Management Commands**

### **View Logs**:
```bash
fly logs
```

### **Restart App**:
```bash
fly restart
```

### **Update Environment Variables**:
```bash
fly secrets set BOT_TOKEN=new_token
```

### **SSH into App**:
```bash
fly ssh console
```

### **Scale App**:
```bash
fly scale count 1
```

## 🔧 **Troubleshooting**

### **Common Issues:**

1. **App won't start**:
   - Check logs: `fly logs`
   - Verify environment variables: `fly secrets list`

2. **Database issues**:
   - Ensure volume is mounted: `fly volumes list`
   - Check database path in environment variables

3. **Bot not responding**:
   - Verify BOT_TOKEN is correct
   - Check if app is running: `fly status`

## 📊 **Fly.io Free Tier Limits**

- **3 shared-cpu VMs** with 256MB RAM each
- **1GB persistent volume** (enough for your SQLite database)
- **160GB bandwidth** per month
- **No time limits** - always on

## 🎉 **Benefits of Fly.io**

- ✅ **Truly free** - no payment required
- ✅ **Always-on** - no sleeping
- ✅ **Persistent storage** - your data is safe
- ✅ **Global deployment** - fast worldwide
- ✅ **Easy management** - simple CLI commands

## 🆘 **Support**

If you encounter issues:
1. Check Fly.io documentation: https://fly.io/docs/
2. View app logs: `fly logs`
3. Check app status: `fly status`
4. Contact Fly.io support if needed

---

**Happy Deploying! 🎉**

Your Read & Revive Bot will run 24/7 on Fly.io for free!
