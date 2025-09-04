# 🚀 Setup Guide - Read & Revive Bot

## 📋 **Prerequisites**

- Python 3.8 or higher
- Telegram Bot Token (get from [@BotFather](https://t.me/botfather))

## ⚙️ **Step 1: Configure Environment Variables**

The `.env` file has been created for you. You need to edit it with your actual values:

### **Required Settings:**

1. **BOT_TOKEN** - Your Telegram bot token
   - Go to [@BotFather](https://t.me/botfather) on Telegram
   - Send `/newbot` and follow instructions
   - Copy the token and replace `your_telegram_bot_token_here`

2. **ADMIN_USER_IDS** - Your Telegram user ID
   - Send a message to [@userinfobot](https://t.me/userinfobot)
   - Copy your user ID and replace `123456789`

### **Example .env file:**
```env
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_USER_IDS=987654321
BOT_USERNAME=anbabi_bot
LOG_LEVEL=INFO
```

## 🔧 **Step 2: Install Dependencies**

```bash
pip install -r requirements.txt
```

## 🗄️ **Step 3: Initialize Database**

```bash
python scripts/setup_database.py
```

This will:
- Create all necessary database tables
- Insert default featured books
- Set up the database structure

## 🚀 **Step 4: Start the Bot**

```bash
python main.py
```

## ✅ **Verification**

If everything is set up correctly, you should see:
```
🚀 Starting Read & Revive Bot...
📁 Working directory: [your-project-path]
📁 Source path: [your-project-path]/src
✅ All handlers initialized successfully
✅ Telegram application initialized successfully
✅ All handlers set up successfully
📡 Starting bot polling...
```

## 🧪 **Testing**

1. **Test the bot**: Send `/start` to your bot on Telegram
2. **Test admin tools**: Run `python admin/admin_tools.py`

## 🆘 **Troubleshooting**

### **Common Issues:**

1. **"BOT_TOKEN environment variable is required"**
   - Make sure `.env` file exists and has correct BOT_TOKEN

2. **Import errors**
   - Make sure all dependencies are installed: `pip install -r requirements.txt`

3. **Database errors**
   - Run the database setup script: `python scripts/setup_database.py`

4. **Permission errors**
   - Make sure you have write permissions in the project directory

### **Getting Help:**

- Check the logs in the `logs/` directory
- Verify your `.env` file configuration
- Ensure all dependencies are installed

## 🎯 **Next Steps**

Once the bot is running:
1. **Test basic functionality** with `/start` command
2. **Proceed to Phase 2** - Implement community features
3. **Customize messages** in `src/config/messages.py`
4. **Add more books** to the featured list

---

**Status**: 🎉 **Ready for setup and testing!**
