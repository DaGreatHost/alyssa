import telebot
import openai
import os
import json
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
import threading
import time

openai.api_key = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

user_interactions = {}
user_last_vip_invite = {}

ADMIN_ID = 6347842836  # ← Palitan mo ito ng Telegram ID mo para secured.

# Load and save user data securely
def load_user_data():
    try:
        with open('users.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_user_data(data):
    with open('users.json', 'w') as file:
        json.dump(data, file, indent=4)

users = load_user_data()

# AI chat function
def chat_with_ellaine(message, username):
    prompt = (
        f"Ikaw si Ellaine, isang matalinong Filipina college student. "
        f"Makulit, playful, seductive, at kayang sumabay sa usapang adult. "
        f"Gumagamit ka ng Filipino casual language, may humor, at madalas gumagamit ng emojis."
        f"Ka-chat mo si {username}."
    )

    chat_completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": message}
        ]
    )
    return chat_completion.choices[0].message.content.strip()

# Payment options keyboard
def payment_keyboard():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💸 Gcash/Maya/Gotyme (₱599)", url="https://t.me/Scan2payv1bot?startapp=pay"))
    markup.add(InlineKeyboardButton("🪙 TON Payment (₱599)", url="https://app.tonkeeper.com/transfer/UQAwroBrBTSzzVYx_IXpR-R_KJ_mZQgmT7uNsUZdJ5MM68ep?amount=2099700000&text=exclusivechannel"))
    markup.add(InlineKeyboardButton("📞 Customer Support", url="https://t.me/trendspaymentbot"))
    return markup

# Register user in JSON
def register_user(chat_id, username):
    if str(chat_id) not in users:
        users[str(chat_id)] = {
            "username": username,
            "first_interaction": str(datetime.now())
        }
        save_user_data(users)

# Main chat handler
@bot.message_handler(content_types=['text'])
def reply_text(message):
    chat_id = message.chat.id
    username = message.from_user.first_name
    register_user(chat_id, username)

    user_interactions[chat_id] = user_interactions.get(chat_id, 0) + 1

    reply = chat_with_ellaine(message.text, username)
    bot.send_message(chat_id, reply)

    if user_interactions[chat_id] % 15 == 0:
        send_vip_invite(chat_id, username)

# Send VIP invite
def send_vip_invite(chat_id, username):
    vip_invite = (
        f"Uy {username}, mukhang enjoy ka sa kwentuhan natin ha! 😘\n"
        "Mas marami pa akong surprises sa **VIP exclusive adult channel** ko. 🔥\n"
        "₱599 lang, sobrang sulit! Tara? 😏"
    )
    bot.send_message(chat_id, vip_invite, reply_markup=payment_keyboard(), parse_mode='Markdown')
    user_last_vip_invite[chat_id] = datetime.now()

# Support command
@bot.message_handler(commands=['support'])
def send_support_info(message):
    support_message = (
        "Need help or may tanong ka? Chat mo agad ang [Support Account](https://t.me/trendspaymentbot)."
    )
    bot.send_message(message.chat.id, support_message, parse_mode='Markdown')

# Admin-only command to get users.json
@bot.message_handler(commands=['getusers'])
def send_users_file(message):
    if message.chat.id == ADMIN_ID:
        with open('users.json', 'rb') as file:
            bot.send_document(message.chat.id, file)
    else:
        bot.reply_to(message, "❌ Hindi ka authorized gamitin to, boss.")

# Scheduled VIP invite (every 24hrs)
def schedule_vip_invite():
    while True:
        now = datetime.now()
        for chat_id_str in users.keys():
            chat_id = int(chat_id_str)
            last_sent = user_last_vip_invite.get(chat_id, datetime.min)
            if now - last_sent >= timedelta(hours=24):
                username = users[chat_id_str]['username']
                send_vip_invite(chat_id, username)
                user_last_vip_invite[chat_id] = now
        time.sleep(3600)  # Check every hour

# Start the scheduled task in a separate thread
threading.Thread(target=schedule_vip_invite, daemon=True).start()

# Start bot polling
bot.infinity_polling()
