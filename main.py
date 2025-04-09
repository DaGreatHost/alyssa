import telebot
import openai
import os
import json
import random
from langdetect import detect
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import threading
import time

openai.api_key = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

bot = telebot.TeleBot(TELEGRAM_TOKEN)

user_interactions = {}
user_last_vip_invite = {}

# Load and save user data

def load_user_data():
    try:
        with open('users.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_user_data(data):
    with open('users.json', 'w') as f:
        json.dump(data, f, indent=4)

users = load_user_data()

def register_user(chat_id, username):
    if str(chat_id) not in users:
        users[str(chat_id)] = {
            "username": username,
            "first_interaction": str(datetime.now())
        }
        save_user_data(users)

def alyssa_prompt(username, user_message):
    with open("alyssa_prompt.txt", "r") as f:
        persona = f.read()
    try:
        lang = detect(user_message)
    except:
        lang = "en"
    lang_note = "\nAlways reply in the language used by the user. If the user writes in Russian, reply in Russian. If the user writes in Japanese, reply in Japanese. Same for Korean, Chinese, German, Hindi, Spanish, etc."
    return f"{persona}\nLanguage detected: {lang}.{lang_note}\nKa-chat mo si {username}."

def chat_with_alyssa(message, username):
    prompt = alyssa_prompt(username, message)
    chat = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": message}
        ]
    )
    return chat.choices[0].message.content.strip()

def payment_keyboard():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📞 Video Call Face Reveal (₱200)", url="https://t.me/Scan2payv1bot?startapp=pay"))
    markup.add(InlineKeyboardButton("💎 VIP Access (₱499)", url="https://t.me/Scan2payv1bot?startapp=pay"))
    markup.add(InlineKeyboardButton("🪙 TON (₱499)", url="https://app.tonkeeper.com/transfer/UQAwroBrBTSzzVYx_IXpR-R_KJ_mZQgmT7uNsUZdJ5MM68ep?amount=2099700000&text=exclusivechannel"))
    markup.add(InlineKeyboardButton("🆘 Support", url="https://t.me/trendspaymentbot"))
    return markup

def send_vip_invite(chat_id, username, type="vip"):
    if type == "video":
        text = f"Hi {username}! Gusto mo bang makita kung sino talaga si Alyssa? 🤭\n\n₱200 lang for a private video call face reveal 😘"
    else:
        text = f"Uy {username}, kung gusto mo pa ng mas mainit at exclusive na content 😏\nJoin my **VIP channel** for just ₱499! 🔥"
    bot.send_message(chat_id, text, reply_markup=payment_keyboard(), parse_mode='Markdown')

@bot.message_handler(content_types=['text'])
def handle_chat(message):
    chat_id = message.chat.id
    username = message.from_user.first_name
    register_user(chat_id, username)

    user_interactions[chat_id] = user_interactions.get(chat_id, 0) + 1
    count = user_interactions[chat_id]

    naughty_lambing_lines = [
        "Grrr... ang sarap mo ka-chat, baka mapasama tuloy ako ng desisyon 😏",
        "Hmp. Pilyo ka talaga 😩 ang hirap iresist ng mga banat mo 🤭",
        "Hoyy wag kang ganyan... nakakakiliti yung mga sinasabi mo 😳",
        "Kung nandito ka lang... baka napayakap na ako sayo 😘",
        "Beh... pag ganyan ka ka-sweet... mapapa-oo talaga ako sayo 😌",
        "Ikaw ha... lagi mo akong pinapalandi 😜",
        "Hindi ko alam kung chat lang ‘to... o nililigawan mo na ako 😏",
        "Ewan ko ba sayo... pero parang gusto kitang i-kiss right now 😘",
        "Chat lang ba ‘to... o foreplay? 😳 Char lang… or not? 🤭",
        "Landi mo sakin ha... I like it 😘"
    ]

    reply = chat_with_alyssa(message.text, username)
    bot.send_message(chat_id, reply)

    # Only one mood: flirty/lambing
    if random.randint(1, 6) == 1:
        bot.send_message(chat_id, random.choice(naughty_lambing_lines))

    # VIP invite triggers
    if count == 10:
        send_vip_invite(chat_id, username, type="video")
    elif count == 15 or (count > 15 and count % 20 == 0):
        send_vip_invite(chat_id, username)

@bot.message_handler(commands=['getusers'])
def send_users(message):
    if message.chat.id == ADMIN_ID:
        with open('users.json', 'rb') as file:
            bot.send_document(message.chat.id, file)

threading.Thread(target=bot.infinity_polling, daemon=True).start()
while True:
    time.sleep(86400)
