# 🚀 Deploy to Replit - Step by Step Guide

## 📋 What This Does
- Protects your `.env` file (contains sensitive tokens)
- Makes it safe to upload to GitHub/Replit
- Keeps your bot running 24/7

## 🔧 Step 1: Prepare Your Project

### Files You Need to Upload:
```
League Randomizer/
├── bot.py
├── config.py
├── player_manager.py
├── team_randomizer.py
├── champion_randomizer.py
├── image_generator.py
├── riot_api.py
├── requirements.txt
├── .gitignore
├── data/
│   ├── league_players.json
│   ├── champion_roles.json
│   └── champion_cache.json
└── assets/
    └── summoners_rift.jpg
```

### Files NOT Uploaded (Protected by .gitignore):
- ❌ `.env` (contains your tokens - KEEP SECRET!)
- ❌ `__pycache__/` (Python cache)
- ❌ `.vscode/` (IDE files)

## 🚀 Step 2: Deploy to Replit

### Option A: Upload to GitHub First (Recommended)
1. **Create GitHub repository:**
   - Go to https://github.com
   - Click "New repository"
   - Name it "league-randomizer"
   - Make it **Private** (important!)

2. **Upload to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/league-randomizer.git
   git push -u origin main
   ```

3. **Import to Replit:**
   - Go to https://replit.com
   - Click "Create Repl"
   - Choose "Import from GitHub"
   - Paste your repository URL
   - Click "Import from GitHub"

### Option B: Direct Upload to Replit
1. **Go to:** https://replit.com
2. **Create account** and click "Create Repl"
3. **Choose "Python" template**
4. **Upload files:**
   - Drag and drop all your Python files
   - Create folders: `data/` and `assets/`
   - Upload `summoners_rift.jpg` to `assets/`

## 🔑 Step 3: Add Your Secrets (Tokens)

### In Replit:
1. **Click "Secrets" tab** (lock icon in left sidebar)
2. **Add these secrets:**
   ```
   DISCORD_TOKEN = your_discord_token_here
   RIOT_API_KEY = your_riot_api_key_here
   ```

### Your .env file is NOT uploaded (protected by .gitignore)
- Replit will use the Secrets instead
- Your tokens stay secure!

## ⚙️ Step 4: Install Dependencies

### In Replit Shell:
```bash
pip install -r requirements.txt
```

### Or install manually:
```bash
pip install discord.py pillow aiohttp python-dotenv
```

## 🎮 Step 5: Run Your Bot

1. **Click the green "Run" button**
2. **You should see:**
   ```
   Bot has connected to Discord!
   Synced X command(s)
   ```

## 🔄 Step 6: Keep Bot Running 24/7

### Free Tier (Limited):
- Bot stops after 1 hour of inactivity
- Keep the Replit tab open
- Use UptimeRobot to ping your bot

### Hacker Plan ($5/month):
- Bot runs 24/7 automatically
- No need to keep tab open
- Better performance

## 🛠️ Step 7: Configure for Production

### Update config.py for Replit:
```python
# Add this to config.py if needed
import os

# Replit uses different paths
if 'REPLIT_DB_URL' in os.environ:
    # Running on Replit
    DATA_DIR = "data"
    ASSETS_DIR = "assets"
else:
    # Running locally
    DATA_DIR = "data"
    ASSETS_DIR = "assets"
```

### Add keep-alive script (optional):
Create `keep_alive.py`:
```python
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
```

Then in `bot.py`, add:
```python
from keep_alive import keep_alive

# At the start of main()
keep_alive()
```

## 🔍 Troubleshooting

### Bot not connecting?
- Check your `DISCORD_TOKEN` in Secrets
- Make sure bot has proper permissions
- Check Replit console for errors

### Commands not working?
- Wait 1-2 minutes for slash commands to sync
- Try `/` in Discord to see if commands appear
- Check bot permissions in Discord server

### Images not loading?
- Make sure `summoners_rift.jpg` is in `assets/` folder
- Check file permissions in Replit

### Bot stops running?
- Free tier: Keep Replit tab open
- Upgrade to Hacker Plan for 24/7
- Use UptimeRobot to ping your bot

## 📱 Monitor Your Bot

### Replit Console:
- Shows bot logs
- Displays errors
- Real-time output

### Discord:
- Bot should appear online
- Commands should work
- Test with `/register @yourself`

## 🎯 Success Checklist

- ✅ Bot appears online in Discord
- ✅ Slash commands work (`/register`, `/randomize`)
- ✅ No errors in Replit console
- ✅ Bot responds to commands
- ✅ Images generate correctly

## 💡 Pro Tips

1. **Keep Replit tab open** (free tier)
2. **Use UptimeRobot** to ping your bot URL
3. **Monitor logs** for any errors
4. **Test commands** regularly
5. **Backup your data** (export from Replit)

Your bot is now running 24/7! 🎉
