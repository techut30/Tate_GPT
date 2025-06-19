import os
import logging
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Load environment variables
load_dotenv()
API_URL = os.getenv("TATEGPT_API_URL")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not API_URL or not BOT_TOKEN:
    raise ValueError("Missing TATEGPT_API_URL or TELEGRAM_BOT_TOKEN in .env")

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to TateGPT. Ask me anything about Tate.")

# Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    chat_id = update.effective_chat.id
    print(f"Received from user: {user_input}")

    await context.bot.send_message(chat_id=chat_id, text="Thinking...")

    try:
        response = requests.post(API_URL, json={"question": user_input})
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")

        if response.status_code == 200:
            data = response.json()
            answer = data.get("answer", "No answer returned.")
            await context.bot.send_message(chat_id=chat_id, text=answer)
        else:
            await context.bot.send_message(chat_id=chat_id, text="Something went wrong with the backend.")

    except Exception as e:
        print(f"Error: {e}")
        await context.bot.send_message(chat_id=chat_id, text="Something went wrong.")

# App entrypoint
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Telegram bot is now polling...")
    app.run_polling()

if __name__ == "__main__":
    main()
