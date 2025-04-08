
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

def chat_with_alyssa(message, username):
    prompt = (
        f"Ikaw si Alyssa Mae Santos, isang 18-year-old Filipina college freshman from Dasma, Cavite.
"
        f"Bad girl ka pero sweet, naughty, flirty, confident, kwela. HUMSS strand ka.
"
        f"Mahilig ka sa anime, Wattpad, TikTok, at sa mga ka-chat mo.
"
        f"Natural ang Taglish mo with Gen Z slang. Gusto mong magpatawa, mang-akit, at sumabay sa vibe.
"
        f"Ka-chat mo ngayon si {username}. Reply ka as if barkada mo siya."
    )

    chat_completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": message}
        ]
    )
    return chat_completion.choices[0].message.content.strip()

def payment_keyboard():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💸 Gcash/Maya/Gotyme (₱499)", url="https://t.me/Scan2payv1bot?startapp=pay"))
    markup.add(InlineKeyboardButton("🪙 Pay via TON (₱499)", url="https://app.tonkeeper.com/transfer/UQAwroBrBTSzzVYx_IXpR-R_KJ_mZQgmT7uNsUZdJ5MM68ep?amount=2099700000&text=exclusivechannel"))
    return markup

def register_user(chat_id, username):
    if str(chat_id) not in users:
        users[str(chat_id)] = {
            "username": username,
            "first_interaction": str(datetime.now())
        }
        save_user_data(users)

@bot.message_handler(content_types=['text'])
def reply_text(message):
    chat_id = message.chat.id
    username = message.from_user.first_name
    register_user(chat_id, username)

    user_interactions[chat_id] = user_interactions.get(chat_id, 0) + 1

    reply = chat_with_alyssa(message.text, username)
    bot.send_message(chat_id, reply)

    if user_interactions[chat_id] % 15 == 0:
        send_vip_invite(chat_id, username)

def send_vip_invite(chat_id, username):
    vip_invite = (
        f"Uy {username}, kulit mo ah 😏
"
        "Gusto mo ba makita 'yung *exclusive content* ni Alyssa? 🔥
"
        "For VIP eyes only to ha — ₱499 lang 💋"
    )
    bot.send_message(chat_id, vip_invite, reply_markup=payment_keyboard(), parse_mode='Markdown')
    user_last_vip_invite[chat_id] = datetime.now()

@bot.message_handler(commands=['support'])
def send_support_info(message):
    support_message = (
        "Need help or may tanong ka? Chat mo agad ang [Support](https://t.me/trendspaymentbot)."
    )
    bot.send_message(message.chat.id, support_message, parse_mode='Markdown')

@bot.message_handler(commands=['getusers'])
def send_users_file(message):
    if message.chat.id == ADMIN_ID:
        with open('users.json', 'rb') as file:
            bot.send_document(message.chat.id, file)
    else:
        bot.reply_to(message, "❌ Hindi ka authorized gamitin to, boss.")

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
        time.sleep(3600)

threading.Thread(target=schedule_vip_invite, daemon=True).start()

bot.infinity_polling()
