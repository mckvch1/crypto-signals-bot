import os
import threading
from flask import Flask

# --- Мини-веб для keep-alive на Render ---
app = Flask(__name__)

@app.get("/")
def root():
    return "ok", 200

def run_web():
    # Render обычно прокидывает PORT, но на всякий случай 8080 по умолчанию
    port = int(os.environ.get("PORT", "8080"))
    # host=0.0.0.0 обязательен для внешнего доступа
    app.run(host="0.0.0.0", port=port, debug=False)

import os, threading, time, requests, pandas as pd, numpy as np, schedule
from io import BytesIO
from flask import Flask
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram import Update, BotCommand

# --- Secrets из переменных окружения ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = int(os.environ.get("CHAT_ID", "0"))

# --- Монеты ---
PAIRS = ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT","DOGEUSDT","LTCUSDT","SUIUSDT"]

# --- Keep-alive HTTP, чтобы Render видел сервис живым ---
app = Flask(__name__)
@app.get("/") 
def root(): return "ok", 200
def run_web(): app.run(host="0.0.0.0", port=8080)

# --- Простейшие хелперы (оставим только нужное для старта) ---
def send_text(msg:str):
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                      data={"chat_id": CHAT_ID, "text": msg, "parse_mode":"Markdown"}, timeout=20)
    except: pass

def get_ticker(symbol):
    return requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}", timeout=20).json()

def cmd_start(update: Update, context: CallbackContext):
    update.message.reply_text("✅ Бот на Render работает. Команда /report отправит обзор.")

def cmd_report(update: Update, context: CallbackContext):
    msg = "📊 *Отчёт по монетам:*\n\n"
    for p in PAIRS:
        d = get_ticker(p)
        price = float(d.get("lastPrice",0) or 0)
        ch = float(d.get("priceChangePercent",0) or 0)
        sign = "📈" if ch>=0 else "📉"
        msg += f"*{p}*: {price:.4f} USDT ({sign} {ch:.2f}%)\n"
    update.message.reply_text(msg, parse_mode="Markdown")

def start_bot():
    up = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = up.dispatcher
    dp.add_handler(CommandHandler("start", cmd_start))
    dp.add_handler(CommandHandler("report", cmd_report))
    up.bot.set_my_commands([
        BotCommand("start","Список команд"),
        BotCommand("report","Отчёт по монетам"),
    ])
    up.start_polling()
    send_text("🚀 Бот запущен на Render.")

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()   # keep-alive веб
    start_bot()                                             # Telegram polling
    while True: time.sleep(60)                              # не выходим

