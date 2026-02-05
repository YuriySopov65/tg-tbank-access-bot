import os
import time
import threading
from flask import Flask, request
import telebot

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

paid_orders = set()

@app.route("/tbank", methods=["POST"])
def tbank_webhook():
    data = request.get_json(silent=True) or {}
    order_id = str(data.get("OrderId", "")).strip()
    status = str(data.get("Status", "")).strip()

    if order_id and status == "CONFIRMED":
        paid_orders.add(order_id)

    return "OK", 200

@bot.message_handler(commands=["start"])
def start_cmd(message):
    parts = message.text.split()
    order_id = parts[1].strip() if len(parts) > 1 else ""

    if order_id not in paid_orders:
        bot.send_message(message.chat.id, "Платёж пока не найден. Попробуйте через 1 минуту.")
        return

    invite = bot.create_chat_invite_link(
        chat_id=CHANNEL_ID,
        member_limit=1,
        expire_date=int(time.time()) + 1800
    )

    bot.send_message(message.chat.id, f"Оплата подтверждена ✅\nВот ссылка для входа:\n{invite.invite_link}")

def run_bot():
    bot.infinity_polling(skip_pending=True)

threading.Thread(target=run_bot).start()

@app.route("/")
def home():
    return "Bot is running"
