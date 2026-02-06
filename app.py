import os
import time
from flask import Flask, request
import telebot

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

paid_orders = set()

@app.get("/")
def home():
    return "OK", 200

@app.post("/tbank")
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
        print("PAID_ORDERS NOW:", list(paid_orders))

    return "OK", 200

@bot.message_handler(commands=["start"])
def start_cmd(message):
    parts = (message.text or "").split(maxsplit=1)
    order_id = parts[1].strip() if len(parts) > 1 else ""

    if not order_id:
        bot.send_message(
            message.chat.id,
            "✅ Бот работает.\n"
            "Нужен номер заказа.\n"
            "Напишите так: /start TEST123"
        )
        return

    if order_id not in paid_orders:
        bot.send_message(
            message.chat.id,
            "⏳ Платёж по этому заказу пока не подтверждён.\n"
            "Подождите 1–2 минуты и нажмите /start ещё раз.\n"
            f"(Я вижу оплаченные: {len(paid_orders)})"
        )
        return

    invite = bot.create_chat_invite_link(
        chat_id=CHANNEL_ID,
        member_limit=1,
        expire_date=int(time.time()) + 1800
    )
    bot.send_message(message.chat.id, f"✅ Оплата подтверждена!\nВот ссылка:\n{invite.invite_link}")

@bot.message_handler(commands=["start"])
def start_cmd(message):
    ...
    invite = bot.create_chat_invite_link(
        chat_id=CHANNEL_ID,
        member_limit=1,
        expire_date=int(time.time()) + 1800
    )
    bot.send_message(message.chat.id, f"✅ Оплата подтверждена!\nВот ссылка:\n{invite.invite_link}")


@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    bot.send_message(
        message.chat.id,
        "Спасибо! Ваша заявка получена.\n"
        "Мы проверим оплату и пришлём ссылку для входа в канал."
    )

    admin_chat_id = 1870956548  # ← сюда вставим ваш Telegram ID
    try:
        bot.forward_message(admin_chat_id, message.chat.id, message.message_id)
    except Exception as e:
        print("Ошибка пересылки админу:", e)
