import telebot
from telebot import types
import requests
import json
import os

# ========== ЧИТАЕМ ПЕРЕМЕННЫЕ ==========
BOT_TOKEN = os.environ.get("8483855085:AAH9Vi8JZTdm2yOLnYQyn8Bt0YKZCSIGzzE")
QWEN_API_KEY = os.environ.get("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjBhMmI5MDJjLWY4OTYtNDBmMy04ZDcxLTg4NTkxOGY4MjczMCIsImxhc3RfcGFzc3dvcmRfY2hhbmdlIjoxNzc2MTQ3ODI2LCJleHAiOjE3Nzg3Mzk4NTF9.IuaAN-_qfp9XSybHIAInv8nSY84o_pq039VmV31MXnY")

# Проверка, что переменные загрузились
if not BOT_TOKEN:
    print("❌ ОШИБКА: BOT_TOKEN не найден в переменных окружения!")
    exit(1)

if not QWEN_API_KEY:
    print("❌ ОШИБКА: QWEN_API_KEY не найден в переменных окружения!")
    exit(1)

print(f"✅ BOT_TOKEN загружен: {BOT_TOKEN[:20]}...")
print(f"✅ QWEN_API_KEY загружен: {QWEN_API_KEY[:20]}...")

bot = telebot.TeleBot(BOT_TOKEN)
history = {}

def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("💬 Чат с AI", "🎨 Создать картинку")
    markup.add("🧹 Очистить память", "ℹ️ О боте")
    return markup

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, f"🤖 Привет! Я Qwen AI бот!", reply_markup=main_keyboard())

@bot.message_handler(func=lambda m: m.text == "💬 Чат с AI")
def chat_mode(m):
    bot.send_message(m.chat.id, "💬 Напиши мне что-нибудь!")

@bot.message_handler(func=lambda m: m.text == "🎨 Создать картинку")
def image_mode(m):
    bot.send_message(m.chat.id, "🎨 Отправь команду: /image описание")

@bot.message_handler(func=lambda m: m.text == "🧹 Очистить память")
def clear_memory(m):
    history[m.from_user.id] = []
    bot.send_message(m.chat.id, "🧹 Память очищена!")

@bot.message_handler(func=lambda m: m.text == "ℹ️ О боте")
def about_bot(m):
    bot.send_message(m.chat.id, "🤖 Qwen AI бот\n• Бесплатно\n• Помнит диалог")

@bot.message_handler(commands=["image"])
def generate_image(m):
    prompt = m.text.replace("/image ", "").strip()
    if not prompt:
        bot.send_message(m.chat.id, "❌ Напиши описание после /image")
        return
    url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}"
    bot.send_photo(m.chat.id, url, caption=f"🎨 {prompt}")

@bot.message_handler(func=lambda m: True)
def handle_message(m):
    uid = m.from_user.id
    text = m.text
    
    if text.startswith("/") or text in ["💬 Чат с AI", "🎨 Создать картинку", "🧹 Очистить память", "ℹ️ О боте"]:
        return
    
    bot.send_chat_action(m.chat.id, "typing")
    
    if uid not in history:
        history[uid] = []
    history[uid].append({"role": "user", "content": text})
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {QWEN_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "qwen/qwen-2.5-72b-instruct",
        "messages": history[uid],
        "max_tokens": 500
    }
    
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=60)
        if r.status_code == 200:
            answer = r.json()["choices"][0]["message"]["content"]
            history[uid].append({"role": "assistant", "content": answer})
            bot.send_message(m.chat.id, answer, reply_markup=main_keyboard())
        else:
            bot.send_message(m.chat.id, f"❌ Ошибка: {r.status_code}")
    except Exception as e:
        bot.send_message(m.chat.id, f"❌ Ошибка: {e}")

print("🤖 Qwen бот запущен!")
bot.infinity_polling()
