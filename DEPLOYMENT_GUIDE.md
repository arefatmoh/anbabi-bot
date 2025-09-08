# 🚀 Deployment Guide - Read & Revive Bot

## 🎯 **Recommended Platform: Railway**

Railway is the best choice for your bot because it:
- Provides persistent storage for your SQLite database
- Offers easy GitHub integration
- Has reliable uptime
- Includes $5 monthly credit (usually sufficient for small bots)

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

## 🚀 **Railway Deployment Steps**

### Step 1: Prepare Repository
1. Commit all files to your GitHub repository
2. Ensure `.env` is in `.gitignore` (never commit secrets!)

### Step 2: Deploy on Railway
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your `anbabi-bot` repository
5. Railway will automatically detect it's a Python app

### Step 3: Configure Environment Variables
1. Go to your project dashboard
2. Click on "Variables" tab
3. Add these variables:
   ```
   BOT_TOKEN=your_actual_bot_token
   ADMIN_USER_IDS=your_telegram_user_id
   BOT_USERNAME=anbabi_bot
   LOG_LEVEL=INFO
   ```

### Step 4: Deploy
1. Railway will automatically build and deploy
2. Check the logs to ensure successful startup
3. Your bot should be running!

## 🔄 **Alternative Platforms**

### **Render** (Second Choice)
- **Pros**: Free PostgreSQL, 750 hours/month
- **Cons**: Sleeps after 15 min inactivity
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

### Railway Free Tier Limits:
- $5 credit per month
- Usually sufficient for small bots
- Monitor usage in dashboard

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
