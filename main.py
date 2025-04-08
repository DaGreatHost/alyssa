
# main.py
import logging
import asyncio
import json
import os
import random
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters
from config import BOT_TOKEN, OPENAI_API_KEY, PAYMENT_LINKS
import openai

# Init OpenAI
openai.api_key = OPENAI_API_KEY

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.info(f"✅ OPENAI KEY LOADED: {openai.api_key[:10]}...")

# Load prompt
with open("alyssa_prompt.txt", "r") as f:
    CHARACTER_PROMPT = f.read().strip()

# Data stores
if os.path.exists("users.json"):
    with open("users.json", "r") as f:
        user_data = json.load(f)
else:
    user_data = {}

if os.path.exists("vip_users.json"):
    with open("vip_users.json", "r") as f:
        vip_users = json.load(f)
else:
    vip_users = []

def save_data():
    with open("users.json", "w") as f:
        json.dump(user_data, f)
    with open("vip_users.json", "w") as f:
        json.dump(vip_users, f)

def get_typing_delay(text):
    return min(4, len(text) * 0.045 + random.uniform(0.6, 1.5))

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! I'm Alyssa Mae 💖
"
        "Your naughty HUMSS bad girl from Dasma 😏
"
        "Chat mo lang ako, I’ll keep you company 😚"
    )

# /vipdone command to mark user as VIP
async def vipdone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in vip_users:
        vip_users.append(user_id)
        save_data()
        await update.message.reply_text("Yieee salamat sa support 🥺 VIP ka na 😘")
    else:
        await update.message.reply_text("VIP ka na talaga 🫶")

# Handle incoming messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text

    if user_id not in user_data:
        user_data[user_id] = {"count": 0, "history": []}

    user_data[user_id]["count"] += 1
    user_data[user_id]["history"].append({"role": "user", "content": text})
    user_data[user_id]["history"] = user_data[user_id]["history"][-5:]
    save_data()

    # Compose chat with Alyssa
    messages = [{"role": "system", "content": CHARACTER_PROMPT}] + user_data[user_id]["history"]

    try:
        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.9
        )
        reply = chat["choices"][0]["message"]["content"]
    except Exception as e:
        import traceback
        logging.error("❌ GPT ERROR:")
        logging.error(traceback.format_exc())
        await update.message.reply_text("Oops, nagka-aberya 😅 Try mo ulit ha.")
        return

    await update.message.chat.send_action(ChatAction.TYPING)
    await asyncio.sleep(get_typing_delay(reply))
    await update.message.reply_text(reply)

    # Trigger monetization if not VIP
    count = user_data[user_id]["count"]
    if user_id not in vip_users:
        if count == 15 or count % 20 == 0:
            await asyncio.sleep(1.5)
            await update.message.reply_text(
                "Ay grabe, kulit mo 👀 Gusto mo ba makita 'yung exclusive content ko? 👀🔥
"
                "For VIP eyes only yan ha! ₱499 lang 💋

"
                f"💳 GCash/Maya/GoTyme:
👉 {PAYMENT_LINKS['GCASH_MAYA']}

"
                f"💎 Pay via TON:
👉 {PAYMENT_LINKS['TON']}"
            )
        if count == 30:
            await asyncio.sleep(1.5)
            await update.message.reply_text(
                "Ayieee 🥺 gusto mo ba makita si Alyssa live?
"
                "Pwede tayo mag video call for ₱200 lang, private 😚

"
                f"👉 {PAYMENT_LINKS['GCASH_MAYA']}"
            )

# Init bot
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("vipdone", vipdone))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logging.info("🚀 Alyssa is online...")
    app.run_polling()
