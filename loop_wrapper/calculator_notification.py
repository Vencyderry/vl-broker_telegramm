import datetime

from client import tz, api
from config import *
from telegrinder import InlineKeyboard, InlineButton

keyboard_calculator = (
    InlineKeyboard()
    .add(InlineButton("Открыть калькулятор", url="https://t.me/vl_broker_bot", callback_data="calculator")).row()
).get_markup()


async def calculator_loop():
    date = datetime.datetime.now(tz=tz) + datetime.timedelta(hours=7)

    hours = CALCULATOR_NOTIFICATION_TIME["hours"]
    minutes = CALCULATOR_NOTIFICATION_TIME["minutes"]
    interval = CALCULATOR_NOTIFICATION_TIME["interval"]

    if (date.hour == hours or date.hour == hours + interval) and date.minute == minutes:
        await api.send_message(text="📌Рассчитать таможенные платежи, не покидая Telegram:",
                               chat_id=USERS_CHAT,
                               reply_markup=keyboard_calculator)
