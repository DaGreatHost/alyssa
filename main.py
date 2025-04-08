# main.py
import logging
import asyncio
import json
import os
import random
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters
import openai

# Load environment variables (TOKEN, OPENAI KEY)
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Debug log: Confirm if key is loading
print("✅ OPENAI KEY LOADED:", openai.api_key[:10], "...")

# Load or initialize user message counters
if os.path.exists("users.json"):
    with open("users.json", "r") as f:
        user_data = json.load(f)
else:
    user_data = {}

# Load VIP users
if os.path.exists("vip_users.json"):
    with open("vip_users.json", "r") as f:
        vip_users = json.load(f)
else:
    vip_users = []

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

CHARACTER_PROMPT = """You are Alyssa Mae Santos, an 18-year-old college freshman from Dasma, Cavite. You're sweet, naughty, and flirty with a kwela and confident personality. You love drawing anime, writing Wattpad stories, and scrolling TikTok. You speak in natural Taglish, like a Gen Z Filipina. You're talking to someone in Telegram, reply naturally and playfully. Don't overuse emojis."""

def save_user_data():
    with open("users.json", "w") as f:
        json.dump(user_data, f)

def save_vip_users():
    with open("vip_users.json", "w") as f:
        json.dump(vip_users, f)

def get_typing_delay(text):
    return min(4, len(text) * 0.04 + random.uniform(0.5, 1.5))

# Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! I'm Alyssa Mae 💖 Your college bestie from Dasma 😘\n\n"
        "I love anime, TikTok, and kwentuhan. Just send me a message, chikahan na!"
    )

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👧 Alyssa Mae Santos\n"
        "📍 Dasma, Cavite\n"
        "🎓 College Freshman, HUMSS\n"
        "🖌️ Artist | ✨ Wattpad writer | 🌀 TikTok queen\n"
        "Ready kang kulitin all day 💕"
    )

async def vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Gusto mo ng access sa *exclusive content* ni Alyssa? 😏\n\n"
        "💸 PHP 499 lang\n"
        "📥 Pay via GCash / Maya / GoTyme:\nhttps://t.me/Scan2payv1bot?startapp=pay\n"
        "💎 Or via TON:\nhttps://app.tonkeeper.com/transfer/UQAwroBrBTSzzVYx_IXpR-R_KJ_mZQgmT7uNsUZdJ5MM68ep?amount=2099700000&text=exclusivechannel",
        parse_mode='Markdown'
    )

async def call(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Pwede tayo mag *video call* for PHP 200 lang! 🔥\nSame payment link lang ha 😚",
        parse_mode='Markdown'
    )

async def vipdone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in vip_users:
        vip_users.append(user_id)
        save_vip_users()
        await update.message.reply_text("Salamat! VIP ka na now. 🔥")
    else:
        await update.message.reply_text("VIP ka na talaga, hindi mo na kailangan ulitin 💖")

async def confess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send mo na secret mo 😳 Promise hindi ako chismosa haha")

# Main chat handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_message = update.message.text

    if user_id not in user_data:
        user_data[user_id] = {"message_count": 0, "history": []}

    user_data[user_id]["message_count"] += 1
    user_data[user_id]["history"].append({"role": "user", "content": user_message})
    user_data[user_id]["history"] = user_data[user_id]["history"][-5:]
    save_user_data()

    messages = [{"role": "system", "content": CHARACTER_PROMPT}] + user_data[user_id]["history"]

    try:
        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.9,
        )
        response = chat["choices"][0]["message"]["content"]
    except Exception as e:
        logging.error(e)
        await update.message.reply_text("Oops, naputol. Try mo ulit 💭")
        return

    await update.message.chat.send_action(action=ChatAction.TYPING)
    await asyncio.sleep(get_typing_delay(response))
    await update.message.reply_text(response)

    count = user_data[user_id]["message_count"]
    if user_id not in vip_users:
        if count == 15 or count % 20 == 0:
            await asyncio.sleep(1.5)
            await update.message.reply_text(
                "Heyy 👀 gusto mo ba makita 'yung exclusive content ko? For VIP eyes only to — PHP 499 lang.\n"
                "💳 GCash/Maya/GoTyme: https://t.me/Scan2payv1bot?startapp=pay\n"
                "💎 TON: https://app.tonkeeper.com/transfer/UQAwroBrBTSzzVYx_IXpR-R_KJ_mZQgmT7uNsUZdJ5MM68ep?amount=2099700000&text=exclusivechannel"
            )
        if count == 30:
            await asyncio.sleep(1.5)
            await update.message.reply_text(
                "Pwede tayo mag *video call* for PHP 200 lang! 😉 Same payment links lang yun."
            )

# Launch app
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("vip", vip))
    app.add_handler(CommandHandler("call", call))
    app.add_handler(CommandHandler("vipdone", vipdone))
    app.add_handler(CommandHandler("confess", confess))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Alyssa is online...")
    app.run_polling()
