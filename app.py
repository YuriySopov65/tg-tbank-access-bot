import os
import time
import threading
from flask import Flask, request
import telebot
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))


bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)
@app.route("/", methods=["GET"])
def home():
    return "Bot is running", 200

paid_orders = set()

@app.route("/tbank", methods=["POST"])
def tbank_webhook():
    data = request.get_json(silent=True) or {}

    order_id = str(
        data.get("OrderId") or data.get("orderId") or data.get("ORDERID") or ""
    ).strip()

    status = str(
        data.get("Status") or data.get("status") or ""
    ).strip().upper()

    print("TBANK WEBHOOK:", data)

    if order_id and status in {"CONFIRMED", "AUTHORIZED"}:
        paid_orders.add(order_id)

    return "OK", 200
@bot.message_handler(commands=["start"])
def start_cmd(message):
    parts = (message.text or "").split(maxsplit=1)
    order_id = parts[1].strip() if len(parts) > 1 else ""

    if not order_id:
        bot.send_message(
            message.chat.id,
            "✅ Бот работает.\n"
            "Чтобы выдать доступ, мне нужен номер заказа.\n"
            "Нажмите кнопку после оплаты (там будет start с цифрами),\n"
            "или отправьте вручную: /start 12345"
        )
        return

    if order_id not in paid_orders:
        bot.send_message(
            message.chat.id,
            "⏳ Платёж пока не подтверждён по этому заказу.\n"
            "Подождите 1–2 минуты и нажмите /start ещё раз."
        )
        return

    try:
        invite = bot.create_chat_invite_link(
            chat_id=int(CHANNEL_ID),
            member_limit=1,
            expire_date=int(time.time()) + 1800
        )
        bot.send_message(message.chat.id, f"✅ Оплата подтверждена!\nВот ссылка:\n{invite.invite_link}")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при создании ссылки: {e}")


    try:
        invite = bot.create_chat_invite_link(
            chat_id=CHANNEL_ID,
            member_limit=1,
            expire_date=int(time.time()) + 1800
        )
        bot.send_message(message.chat.id, f"✅ Оплата найдена!\nВот ссылка для входа в канал:\n{invite.invite_link}")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при создании ссылки: {e}")


    invite = bot.create_chat_invite_link(
        chat_id=CHANNEL_ID,
        member_limit=1,
        expire_date=int(time.time()) + 1800
    )

    bot.send_message(message.chat.id, f"Оплата подтверждена ✅\nВот ссылка для входа:\n{invite.invite_link}")
@bot.message_handler(commands=["test"])
def test_cmd(message):
    try:
        invite = bot.create_chat_invite_link(
            chat_id=CHANNEL_ID,
            member_limit=1,
            expire_date=int(time.time()) + 1800
        )
        @bot.message_handler(commands=["start"])
def start_cmd(message):
    parts = message.text.split(maxsplit=1)
    order_id = parts[1].strip() if len(parts) > 1 else ""

    if not order_id:
        bot.send_message(
            message.chat.id,
            "⚠️ Ссылка пришла без номера заказа.\n"
            "Оплатите заново или перейдите по кнопке после оплаты — там будет правильная ссылка."
        )
        return

    if order_id not in paid_orders:
        bot.send_message(
            message.chat.id,
            "⏳ Платёж пока не подтверждён. Подождите 1–2 минуты и нажмите /start ещё раз."
        )
        return

    invite = bot.create_chat_invite_link(
        chat_id=int(CHANNEL_ID),
        member_limit=1,
        expire_date=int(time.time()) + 1800
    )
    bot.send_message(message.chat.id, f"✅ Оплата подтверждена.\nВот ссылка для входа:\n{invite.invite_link}")

def run_bot():
    bot.infinity_polling(skip_pending=True)

threading.Thread(target=run_bot).start()

@app.route("/")
def home():
    return "Bot is running"
