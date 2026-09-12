"""
Hashira ATS - Telegram Diagnostic & Test Script
Verifies bot token, tests reachability, inspects updates, and tests delivery.
"""
import os
import sys
from dotenv import load_dotenv

# Force load latest .env
load_dotenv(dotenv_path="/home/cherry/hashira/.env", override=True)

from telegram_bot import (
    get_bot_info,
    auto_detect_chat_id,
    test_telegram_connection,
    send_telegram_message
)

def run_telegram_diag():
    print("==================================================")
    print("🤖 Hashira ATS - Telegram Diagnostic Tool")
    print("==================================================")

    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()

    print(f"• Loaded Token: {'*' * (len(token)-6) + token[-6:] if len(token) > 6 else 'NOT SET'}")
    print(f"• Target Chat ID: {chat_id if chat_id else 'NOT SET'}")
    print("--------------------------------------------------")

    if not token:
        print("❌ Error: TELEGRAM_BOT_TOKEN is missing in /home/cherry/hashira/.env")
        sys.exit(1)

    # 1. Test getMe
    print("\n[Step 1] Validating Bot Token with Telegram API...")
    ok_bot, bdata = get_bot_info(token)
    if not ok_bot:
        print(f"❌ Bot Token Validation Failed: {bdata.get('error')}")
        sys.exit(1)

    bot_name = bdata.get("first_name", "Bot")
    username = bdata.get("username", "Unknown")
    print(f"✅ Bot Token Validated Successfully!")
    print(f"   • Name: {bot_name}")
    print(f"   • Handle: @{username}")
    print(f"   • Direct Link: https://t.me/{username}")

    # 2. Check for recent incoming messages
    print("\n[Step 2] Checking for incoming messages (getUpdates)...")
    detected, cid, desc = auto_detect_chat_id(token)
    if detected:
        print(f"✅ Active conversation detected! {desc}")
        if cid != chat_id:
            print(f"ℹ️ Note: Detected chat ID ({cid}) differs from .env ({chat_id}).")
            chat_id = cid
    else:
        print(f"ℹ️ {desc}")

    # 3. Test sending a message
    if chat_id:
        print(f"\n[Step 3] Sending test ping to Chat ID: {chat_id}...")
        ok_msg, msg_resp = test_telegram_connection(token, chat_id)
        if ok_msg:
            print(f"🎉 SUCCESS: Message delivered to Telegram! ({msg_resp})")
        else:
            print(f"⚠️ Notice: {msg_resp}")
            print(f"\n👉 How to resolve in 10 seconds:")
            print(f"   1. Open Telegram on your phone or web browser.")
            print(f"   2. Search for: @{username} (or open https://t.me/{username})")
            print(f"   3. Tap START (or send a message: 'hi').")
            print(f"   4. Run this script again: python test_telegram.py")
    else:
        print("\n⚠️ No Chat ID specified. Please add TELEGRAM_CHAT_ID in .env.")

    print("\n==================================================")

if __name__ == "__main__":
    run_telegram_diag()
