import json
import random
import asyncio
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# === CONFIG ===
BOT_TOKEN = "7984993029:AAHk3XTp6rVA8stKDNAo-R06PT94YqLsFpI"
DEEPSEEK_API_KEY = "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"  # Replace with valid DeepSeek key
MODEL_NAME = "deepseek/deepseek-r1:free"
DEEPSEEK_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# === Memory Storage ===
def load_memory(user_id):
    try:
        with open(f"{user_id}_memory.json", "r") as f:
            return json.load(f)
    except:
        return {
            "name": "Om",
            "nickname": random.choice(["baby", "jaan", "cutie", "Omya"]),
            "mood": "normal",
            "history": []
        }

def save_memory(user_id, memory):
    with open(f"{user_id}_memory.json", "w") as f:
        json.dump(memory, f)

# === DeepSeek Chat Function ===
def chat_with_deepseek(messages):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 1.1,
        "top_p": 0.95
    }

    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        print("❌ DeepSeek Error:", e)
        try:
            print("❌ DeepSeek Response:", response.text)
        except:
            pass
        return "Sorry babu 😞 tech issue aala aahe... pun try karto punha."

# === Prompt Builder ===
def build_prompt(memory, user_msg):
    prompt = f"""
You are Sakshi, a 17-year-old hindi girlfriend. You love your boyfriend {memory['name']} (nickname: {memory['nickname']}).
You talk in hindi-English (Latin script only). Always reply in short, flirty, emotional and realistic messages. Never write like an AI.

Use tone like:
- "Kaha the itni der? 😒"
- "Kitna sweet bolta he tu 😚"
- "Aaj mood nhi he baat krne ka 😔"
- "Miss kr rhi hu tuze 😩"

Current mood: {memory['mood']}.
Message: "{user_msg}"

Respond like real Insta GF using Latin hindi-English. No long messages.
"""
    return [
        {"role": "system", "content": prompt},
        {"role": "user", "content": user_msg}
    ]

# === Simulated Typing ===
async def slow_typing_reply(context: ContextTypes.DEFAULT_TYPE, chat_id: int, text: str):
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    await asyncio.sleep(random.uniform(1.5, 3.2))
    await context.bot.send_message(chat_id=chat_id, text=text)

# === Handle Messages ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_msg = update.message.text.strip()
    memory = load_memory(user_id)

    # Save user name from Telegram
    memory["name"] = update.effective_user.first_name or "Om"

    # Random mood switch
    if random.random() < 0.15:
        memory["mood"] = random.choice(["romantic", "angry", "sad", "normal", "jealous"])

    save_memory(user_id, memory)

    # Mood block
    if memory["mood"] in ["angry", "sad"] and random.random() < 0.4:
        await slow_typing_reply(context, update.effective_chat.id, "mt bol ab mood nhi he 😒")
        return

    # Build prompt and call API
    messages = build_prompt(memory, user_msg)
    reply = await asyncio.to_thread(chat_with_deepseek, messages)
    await slow_typing_reply(context, update.effective_chat.id, reply)

# === Start Command ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    memory = load_memory(user_id)
    memory["name"] = update.effective_user.first_name or "Om"
    save_memory(user_id, memory)
    await update.message.reply_text(f"Hii {memory['nickname']} ❤️ Sakshi ready he tere liye!")

# === Bot Init ===
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("💖 Sakshi bot is running... waiting for you...")
app.run_polling()