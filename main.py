import os
import threading
from flask import Flask
from telegram.ext import Updater, CommandHandler
import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

app = Flask(__name__)

@app.get("/")
def root():
    return "ok", 200

def run_web():
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=False)

def start(update, context):
    update.message.reply_text("Бот запущен!")

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    updater.start_polling()
    updater.idle()


