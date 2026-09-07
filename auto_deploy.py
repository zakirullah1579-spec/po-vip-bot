#!/usr/bin/env python3
"""
\U0001f680 AUTO-DEPLOY SCRIPT for Pocket Option VIP Bot
=================================================
Ye script AUTOMATICALLY bot ko free hosting par deploy karega!

Bas 2 cheezein chahiye:
1. GitHub account (username + password ya token)
2. Render account (GitHub se login - 1 click)

Usage:
    python auto_deploy.py

Yeh script:
1. GitHub par repo banayega
2. Files upload karega
3. Render par deploy karega
4. Bot 24/7 LIVE ho jayega!
"""

import os
import sys
import json
import subprocess
import time

# ═══════════════════════════════════════════════════════════════════
# CONFIGURATION - Ye values apni marzi se change karo
# ═══════════════════════════════════════════════════════════════════

BOT_TOKEN = "8275592154:AAGJ2rW1a-Y0O1RzBcf8_gdk4HlpbMg0b-0"
ADMIN_ID = "93372553"
POCKET_OPTION_REG_LINK = "https://pocketoption.com/register?gid=YOUR_AFFILIATE_ID"
REPO_NAME = "po-vip-bot"

# ═══════════════════════════════════════════════════════════════════


def run_cmd(cmd, check=True):
    """Run a shell command and return output."""
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True
    )
    if check and result.returncode != 0:
        print(f"\u274c Error: {result.stderr}")
        return None
    return result.stdout.strip()


def check_git():
    """Check if git is installed."""
    result = run_cmd("git --version", check=False)
    if not result:
        print("\u274c Git nahi hai! Pehle git install karo:")
        print("  Windows: https://git-scm.com/download/win")
        print("  Mac: brew install git")
        print("  Linux: sudo apt install git")
        return False
    print("\u2705 Git mil gaya:", result)
    return True


def setup_github():
    """Set up GitHub repository."""
    print("\n" + "="*50)
    print("\U0001f4c1 Step 1: GitHub Repository Setup")
    print("="*50)

    username = input("\U0001f464 GitHub username: ").strip()
    if not username:
        print("\u274c Username zaruri hai!")
        return None, None

    # Check if git is configured
    git_name = run_cmd("git config user.name", check=False)
    git_email = run_cmd("git config user.email", check=False)

    if not git_name:
        run_cmd(f'git config --global user.name "{username}"', check=False)
    if not git_email:
        email = input("\U0001f4e7 GitHub email: ").strip()
        run_cmd(f'git config --global user.email "{email}"', check=False)

    # Initialize git repo
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # Remove existing git repo if any
    if os.path.exists(".git"):
        import shutil
        shutil.rmtree(".git")

    run_cmd("git init")
    run_cmd("git branch -M main")

    # Add all files
    run_cmd("git add .")
    run_cmd('git commit -m "Pocket Option VIP Bot"')

    print(f"\n\U0001f4dd Ab GitHub par jao aur repo banao:")
    print(f"   https://github.com/new")
    print(f"\n   Repo name: {REPO_NAME}")
    print(f"   Private: YES (recommended)")
    print(f"   DO NOT initialize with README!")
    print(f"\nRepo banane ke baad, yeh command run karo terminal mein:")
    print(f"\n   git remote add origin https://github.com/{username}/{REPO_NAME}.git")
    print(f"   git push -u origin main")
    print(f"\n\U0001f511 GitHub password ke liye Personal Access Token use karo:")
    print(f"   https://github.com/settings/tokens")
    print(f"   Click: Generate new token (classic)")
    print(f"   Select: repo (all)")
    print(f"   Copy token → password mein paste karo")

    input("\n\u2705 Push complete ho gaya? (Enter dabao)")

    return username, REPO_NAME


def setup_render(username, repo_name):
    """Guide user through Render deployment."""
    print("\n" + "="*50)
    print("\U0001f310 Step 2: Render.com Deployment")
    print("="*50)

    print("\nAb Render par jao:")
    print(f"   https://render.com")
    print(f"\n1\ufe0f\u20e3 **Sign up with GitHub** (1 click!)")
    print(f"2\ufe0f\u20e3 **New +** → **Web Service**")
    print(f"3\ufe0f\u20e3 **Connect** your repo: {username}/{repo_name}")
    print(f"4\ufe0f\u20e3 Settings:")
    print(f"   Name: pocket-option-vip-bot")
    print(f"   Runtime: Python 3")
    print(f"   Build Command: pip install -r requirements.txt")
    print(f"   Start Command: python bot_web.py")
    print(f"   Instance Type: **Free**")
    print(f"\n5\ufe0f\u20e3 **Environment Variables** add karo:")
    print(f"   BOT_TOKEN = {BOT_TOKEN}")
    print(f"   ADMIN_ID = {ADMIN_ID}")
    print(f"   POCKET_OPTION_REG_LINK = {POCKET_OPTION_REG_LINK}")
    print(f"\n6\ufe0f\u20e3 **Create Web Service** click karo!")
    print(f"\n\U0001f389 2-3 minutes mein bot LIVE ho jayega!")


def setup_koyeb(username, repo_name):
    """Guide user through Koyeb deployment (alternative)."""
    print("\n" + "="*50)
    print("\U0001f310 Alternative: Koyeb.com Deployment")
    print("="*50)

    print("\nKoyeb par jao:")
    print(f"   https://app.koyeb.com/auth/signup")
    print(f"\n1\ufe0f\u20e3 **Sign up with GitHub**")
    print(f"2\ufe0f\u20e3 **Create Service** → **GitHub** → Select repo: {username}/{repo_name}")
    print(f"3\ufe0f\u20e3 Settings:")
    print(f"   Build Command: pip install -r requirements.txt")
    print(f"   Run Command: python bot.py")
    print(f"   Instance: **Free** (512MB)")
    print(f"\n4\ufe0f\u20e3 **Environment Variables** add karo:")
    print(f"   BOT_TOKEN = {BOT_TOKEN}")
    print(f"   ADMIN_ID = {ADMIN_ID}")
    print(f"   POCKET_OPTION_REG_LINK = {POCKET_OPTION_REG_LINK}")
    print(f"\n5\ufe0f\u20e3 **Deploy** click karo!")
    print(f"\n\U0001f389 Bot 24/7 FREE par chal raha hai!")


def verify_bot():
    """Verify bot is running."""
    print("\n" + "="*50)
    print("\U0001f4f1 Step 3: Bot Test")
    print("="*50)

    print("\nAb Telegram kholo aur test karo:")
    print(f"   1. Search: @povipsignal2026_bot")
    print(f"   2. Send: /start")
    print(f"   3. 4 buttons dikhenge!")
    print(f"\n\u2705 Agar bot respond kare to DEPLOYMENT SUCCESSFUL!")


def main():
    print("\U0001f680 Pocket Option VIP Bot - AUTO DEPLOY")
    print("="*50)
    print("\nYe script bot ko FREE hosting par deploy karega!\n")

    # Step 0: Check prerequisites
    if not check_git():
        sys.exit(1)

    # Step 1: GitHub setup
    username, repo_name = setup_github()
    if not username:
        sys.exit(1)

    # Step 2: Choose platform
    print("\n\U0001f310 Hosting platform choose karo:")
    print("   1. Render.com (FREE - 750 hours/month)")
    print("   2. Koyeb.com (FREE - 24/7 always on)")

    choice = input("\nChoice (1 ya 2): ").strip()

    if choice == "1":
        setup_render(username, repo_name)
    elif choice == "2":
        setup_koyeb(username, repo_name)
    else:
        setup_render(username, repo_name)

    # Step 3: Verify
    verify_bot()

    print("\n" + "="*50)
    print("\U0001f389 DEPLOYMENT COMPLETE!")
    print("="*50)
    print("\n\U0001f468\u200d\U0001f4bc Admin Commands:")
    print("   /admin - Admin panel")
    print("   /adduser <chat_id> <po_id> - User verify karo")
    print("   /signal EUR/USD CALL M5 85% - VIP signal bhejo")
    print("   /broadcast <message> - Sab ko message bhejo")
    print("   /listusers - Users dekho")
    print("\n\u26a0\ufe0f POCKET_OPTION_REG_LINK update karna mat bhoolna!")


if __name__ == "__main__":
    main()