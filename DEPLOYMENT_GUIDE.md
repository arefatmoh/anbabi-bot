# 🚀 Deployment Guide - Read & Revive Bot

## 🎯 **Recommended Platform: Render**

Render is the best choice for your bot because it:
- **Completely FREE forever** - no payment required
- Provides persistent storage for your SQLite database
- Offers easy GitHub integration
- Has reliable uptime
- 750 hours/month (enough for 24/7 operation)

## 📋 **Pre-Deployment Checklist**

### 1. **Environment Variables Setup**
You'll need to set these in your deployment platform:

```env
BOT_TOKEN=your_telegram_bot_token_here
ADMIN_USER_IDS=your_telegram_user_id
BOT_USERNAME=anbabi_bot
LOG_LEVEL=INFO
DATABASE_PATH=/app/reading_tracker.db
```

### 2. **Required Files** ✅
- `Procfile` - Tells Railway how to run your bot
- `railway.json` - Railway-specific configuration
- `runtime.txt` - Specifies Python version
- `requirements.txt` - Python dependencies (already exists)

## 🚀 **Render Deployment Steps**

### Step 1: Prepare Repository
1. Commit all files to your GitHub repository
2. Ensure `.env` is in `.gitignore` (never commit secrets!)

### Step 2: Deploy on Render
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Connect your `anbabi-bot` repository
5. Render will automatically detect it's a Python app

### Step 3: Configure Service Settings
1. **Name**: `anbabi-bot` (or any name you prefer)
2. **Environment**: `Python 3`
3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: `python main.py`
5. **Plan**: Select **Free** plan

### Step 4: Configure Environment Variables
1. Scroll down to "Environment Variables"
2. Add these variables:
   ```
   BOT_TOKEN=your_actual_bot_token
   ADMIN_USER_IDS=your_telegram_user_id
   BOT_USERNAME=anbabi_bot
   LOG_LEVEL=INFO
   DATABASE_PATH=/opt/render/project/src/reading_tracker.db
   ```

**Note**: Your SQLite database will be automatically created and persisted on Render. No migration needed!

### Step 5: Deploy
1. Click "Create Web Service"
2. Render will build and deploy automatically
3. Check the logs to ensure successful startup
4. Your bot should be running!

## 🔄 **Alternative Platforms**

### **Railway** (Paid Option)
- **Cost**: $1-3/month after 30-day trial
- **Pros**: No sleeping, more resources
- **Cons**: Requires payment after trial
- **Setup**: Connect GitHub → Set environment variables → Deploy

### **Fly.io** (For Always-On)
- **Pros**: Always-on, no sleeping, persistent storage
- **Cons**: More complex setup
- **Setup**: Install flyctl → `fly launch` → Configure

### **Heroku** (Paid Option)
- **Cost**: $5/month Eco plan
- **Pros**: Very reliable, mature platform
- **Setup**: Connect GitHub → Set config vars → Deploy

## 🛠️ **Post-Deployment**

### 1. **Test Your Bot**
- Send `/start` to your bot on Telegram
- Verify all features work correctly
- Check logs for any errors

### 2. **Monitor Performance**
- Check Railway dashboard for resource usage
- Monitor logs for errors
- Set up alerts if needed

### 3. **Database Backup**
- Your SQLite database will persist on Railway
- Consider setting up automated backups for important data

## 🆘 **Troubleshooting**

### Common Issues:

1. **Bot not responding**
   - Check BOT_TOKEN is correct
   - Verify bot is running (check logs)
   - Ensure webhook is not set (bot uses polling)

2. **Database errors**
   - Check DATABASE_PATH is set correctly
   - Verify database file permissions

3. **Import errors**
   - Ensure all dependencies are in requirements.txt
   - Check Python version compatibility

## 📊 **Resource Monitoring**

### Render Free Tier Limits:
- 750 hours per month (enough for 24/7)
- Sleeps after 15 minutes of inactivity
- Wakes up automatically when needed
- No payment required ever

### Optimization Tips:
- Use efficient logging (avoid DEBUG in production)
- Optimize database queries
- Monitor memory usage

## 🔐 **Security Best Practices**

1. **Never commit secrets** to Git
2. **Use environment variables** for all sensitive data
3. **Regular updates** of dependencies
4. **Monitor logs** for suspicious activity
5. **Backup database** regularly

## 📞 **Support**

If you encounter issues:
1. Check Railway logs first
2. Verify environment variables
3. Test locally with same configuration
4. Check Railway documentation
5. Contact Railway support if needed

---

**Happy Deploying! 🎉**

Your Read & Revive Bot should be running smoothly on Railway!
