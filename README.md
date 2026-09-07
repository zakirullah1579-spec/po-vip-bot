# \U0001f916 Pocket Option VIP Signal Telegram Bot

## \U0001f4cb Features
- \U0001f511 Get Signals button → Registration required first
- 4 Main Buttons: Start Registration, Instruction, Test Signals, Reviews
- \U0001f4c8 Synthetic Signal Engine (EMA 9/21 + RSI)
- \U0001f468‍\U0001f4bb Admin Panel for user verification & signal broadcasting
- Free signals (limited) + VIP signals (after registration verification)

## \U0001f680 Free Hosting Setup (Railway.app)

### Step 1: Create Account
1. Go to https://railway.app
2. Click **Start a New Project**
3. Sign up with your **GitHub** account

### Step 2: Upload Bot Code
1. Go to https://github.com and create a **New Repository** (e.g. `po-vip-bot`)
2. Upload ALL files from the ZIP to this repository:
   - bot.py
   - requirements.txt
   - Procfile
   - runtime.txt
   - .env.example (rename to .env on Railway — see Step 3)
   - README.md

### Step 3: Deploy on Railway
1. Go to https://railway.app → **New Project**
2. Select **Deploy from GitHub repo**
3. Choose your `po-vip-bot` repository
4. Click on the project → **Variables** tab
5. Add these environment variables:
   - `BOT_TOKEN` = `8275592154:AAGJ2rW1a-Y0O1RzBcf8_gdk4HlpbMg0b-0`
   - `ADMIN_ID` = `93372553`
   - `POCKET_OPTION_REG_LINK` = `https://pocketoption.com/register?gid=YOUR_AFFILIATE_ID`
6. Click **Deploy** → Bot will start automatically!
7. Check **Logs** tab to confirm bot is running

### Step 4: Test
1. Open Telegram → search @povipsignal2026_bot
2. Send `/start`
3. Click buttons to test!

## \U0001f468‍\U0001f4bb Admin Commands
| Command | Description |
|---------|-------------|
| `/admin` | Open admin panel |
| `/adduser <chat_id> <po_id>` | Verify a user |
| `/removeuser <chat_id>` | Remove a user |
| `/signal EUR/USD CALL M5 85%` | Broadcast VIP signal |
| `/broadcast <message>` | Message all users |
| `/listusers` | List all users |
| `/stats` | Bot statistics |

## \U0001f527 Alternative Free Hosting

### Option 2: Render.com
1. Go to https://render.com → Sign up
2. New → Background Worker
3. Connect GitHub repo
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `python bot.py`
6. Add env vars same as Railway
7. Deploy!

### Option 3: PythonAnywhere (Limited)
1. Go to https://pythonanywhere.com → Free account
2. Upload files
3. Open Bash console → `pip install -r requirements.txt`
4. Run `python bot.py` (free account has time limits)

## ⚠️ Important Notes
- Update `POCKET_OPTION_REG_LINK` with your actual affiliate link
- Admin ID (93372553) is YOUR Telegram user ID
- Bot token is already configured
- Keep .env file SECRET — never share bot token!
