from client import api, tz
from config import *
from patterns import *
import datetime


async def chat_rules_loop():
    date = datetime.datetime.now(tz=tz) + datetime.timedelta(hours=7)
    if date.weekday() in [0, 3, 6]:
        if date.hour == RULES_NOTIFICATION_TIME['hours'] and date.minute == RULES_NOTIFICATION_TIME['minutes']:
            await api.send_message(text=MESSAGE_RULES,
                                   chat_id=USERS_CHAT)
