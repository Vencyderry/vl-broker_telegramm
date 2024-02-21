import datetime

from client import tz, api
from config import *
from telegrinder import InlineKeyboard, InlineButton

keyboard_application = (
    InlineKeyboard()
    .add(InlineButton("Оставить заявку", url="https://t.me/vl_broker_bot")).row()
).get_markup()


async def application_loop():
    date = datetime.datetime.now(tz=tz) + datetime.timedelta(hours=7)

    if date.weekday() in [day for day in range(0, 4)]:
        hours = APPLICATION_NOTIFICATION_TIME["weekdays"]["hours"]
        minutes = APPLICATION_NOTIFICATION_TIME["weekdays"]["minutes"]
    else:
        hours = APPLICATION_NOTIFICATION_TIME["weekend"]["hours"]
        minutes = APPLICATION_NOTIFICATION_TIME["weekend"]["minutes"]

    if date.hour == hours and date.minute == minutes:
        await api.send_message(text="📌Оставить заявку на таможенное оформление:",
                               chat_id=USERS_CHAT,
                               reply_markup=keyboard_application)
