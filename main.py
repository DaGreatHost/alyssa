
import telebot
import os
import json
import random
import time
import threading
from vc_lines import vc_lines
from reply_lines import static_replies
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

bot = telebot.TeleBot(TELEGRAM_TOKEN)
users_file = "users.json"

try:
    with open(users_file, "r") as f:
        users = json.load(f)
except:
    users = {}

def save_users():
    with open(users_file, "w") as f:
        json.dump(users, f, indent=2)

# Payment button
def payment_button():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📹 Video Call ₱200", url="https://t.me/Scan2payv1bot?startapp=pay"))
    return markup

# Register user
@bot.message_handler(commands=["start"])
def start(message):
    cid = str(message.chat.id)
    if cid not in users:
        users[cid] = {"username": message.from_user.first_name}
        save_users()
    bot.send_message(message.chat.id, "Hi! 😘 I'm Alyssa, your naughty AI girlfriend. G ka ba sa kiliti?")

# Admin: get user file
@bot.message_handler(commands=["getusers"])
def get_users(message):
    if message.chat.id == ADMIN_ID:
        with open(users_file, "rb") as f:
            bot.send_document(message.chat.id, f)

# AI girlfriend mode — simple non-GPT responses
@bot.message_handler(func=lambda m: True)
def reply_static(message):
    cid = str(message.chat.id)
    if cid not in users:
        users[cid] = {"username": message.from_user.first_name}
        save_users()

    user_text = message.text.lower().strip()
    reply_found = False

    for key, responses in static_replies.items():
        if key in user_text:
            bot.send_message(message.chat.id, random.choice(responses))
            reply_found = True
            break

    if not reply_found:
        fallback_lines = [
            "Hmm? Ang tahimik mo... lambingin mo naman ako 😘",
            "Awww 🥺 wala ka bang kwento sakin today?",
            "Landi mo ha... gusto kita lalo 😏",
            "Sabihin mo nga totoo... crush mo na ko diba? 🤭",
            "Puro ka pa-cute... kiss mo nalang kaya ako 😚"
        ]
        bot.send_message(message.chat.id, random.choice(fallback_lines))

# Auto VC message every 10 minutes
def auto_vc_sender():
    while True:
        for cid in users.keys():
            try:
                bot.send_message(int(cid), random.choice(vc_lines), reply_markup=payment_button())
            except Exception as e:
                print(f"[ERROR] VC send to {cid}: {e}")
        time.sleep(600)

threading.Thread(target=auto_vc_sender, daemon=True).start()
bot.infinity_polling()
