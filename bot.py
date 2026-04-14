import telebot
from telebot import 
BOT_TOKEN = "8164135376:AAGDuNAB_NTk1OPq-oZeP326F_Zd_fTjoJQ"
QWEN_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjBhMmI5MDJjLWY4OTYtNDBmMy04ZDcxLTg4NTkxOGY4MjczMCIsImxhc3RfcGFzc3dvcmRfY2hhbmdlIjoxNzc2MTQ3ODI2LCJleHAiOjE3Nzg3Mzk4NTF9.IuaAN-_qfp9XSybHIAInv8nSY84o_pq039VmV31MXnY"

bot = telebot.TeleBot(BOT_TOKEN)
history = {}

def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("💬 Чат с AI", "🎨 Создать картинку")
    markup.add("🧹 Очистить память", "ℹ️ О боте")
    return markup

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        f"🤖 Привет, {message.from_user.first_name}!\n\nЯ Qwen — мощный AI помощник!\n\nВыбери действие на кнопках 👇",
        reply_markup=main_keyboard()
    )

@bot.message_handler(func=lambda m: m.text == "💬 Чат с AI")
def chat_mode(m):
    bot.send_message(m.chat.id, "💬 Напиши свой вопрос!")

@bot.message_handler(func=lambda m: m.text == "🎨 Создать картинку")
def image_mode(m):
    bot.send_message(m.chat.id, "🎨 Отправь команду:\n/image описание", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🧹 Очистить память")
def clear_memory(m):
    history[m.from_user.id] = []
    bot.send_message(m.chat.id, "🧹 Память очищена!", reply_markup=main_keyboard())

@bot.message_handler(func=lambda m: m.text == "ℹ️ О боте")
def about_bot(m):
    bot.send_message(m.chat.id, "🤖 Qwen AI\n• Модель: Qwen (Alibaba)\n• Помнит диалог\n• Бесплатно", reply_markup=main_keyboard())

@bot.message_handler(commands=["image"])
def generate_image(m):
    prompt = m.text.replace("/image ", "").strip()
    if not prompt:
        bot.send_message(m.chat.id, "❌ Пример: /image кот в космосе", parse_mode="Markdown")
        return
    
    bot.send_chat_action(m.chat.id, "upload_photo")
    url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=1024&height=1024"
    bot.send_photo(m.chat.id, url, caption=f"🖼️ {prompt}", reply_markup=main_keyboard())

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
    
    if len(history[uid]) > 10:
        history[uid] = history[uid][-10:]
    
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
            bot.send_message(m.chat.id, f"❌ Ошибка: {r.status_code}", reply_markup=main_keyboard())
    except Exception as e:
        bot.send_message(m.chat.id, f"❌ Ошибка: {e}", reply_markup=main_keyboard())

print("🤖 QWEN БОТ ЗАПУЩЕН!")
bot.infinity_polling()
