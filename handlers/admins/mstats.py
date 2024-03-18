import traceback

from client import api
from handlers.executor import ExecutorType, DispatchExecutor
from permissions_store import is_admin
from patterns import ERROR_PERMISSION
from operations import get_system, get_users_all, get_user
from models import User
from tools import digit
from config import USERS_CHAT
from telegrinder import InlineKeyboard, InlineButton, Dispatch, Message
from telegrinder.rules import Text, IsPrivate

dp = Dispatch()


executor = DispatchExecutor(title="mstatistics",
                            permission="operations.admin",
                            type_executor=ExecutorType.COMMAND
                            )


@dp.message(Text(["/mstats"]))
async def mstats(message: Message) -> None:
    try:

        if not is_admin(message.from_.unwrap().id):
            await message.answer(ERROR_PERMISSION)
            return

        system = get_system()
        users = get_users_all()
        stats = f"""
ℹ️ Информация о боте:
  
👥 Пользователей в базе: {digit(len(users))}

📨 Статистика обработки ивентов:
▶ Команд за сессию: {digit(system.commands_processed)}
▶ Сообщений за сессию: {digit(system.messages_processed)}
▶ Команд за все время: {digit(system.commands_processed_all)}
▶ Сообщений за все время: {digit(system.messages_processed_all)}

🤖 Статистика использования бота:
▶ Команда "/start": {digit(system.statistic_start)}
▶ Кнопка "Заполнить заявку": {digit(system.statistic_application)}
▶ Кнопка "Ознакомиться с услугами": {digit(system.statistic_price)}
▶ Кнопка "Узнать курс валют": {digit(system.statistic_currency)}
▶ Кнопка "Калькулятор": {digit(system.statistic_calculator)}

🕰️ Топ промежутков времени активного использования бота:
▶ Coming soon
"""
        # channel = await api.request_raw("getChannels", {"channel": USERS_CHAT}) #"-1001763293068"
        # print(channel)
        # dev = get_user(User.username, "vencyderry")
        # memb = await api.get_chat_member("-1001763293068", 5296228892)
        # memb = await api.get_chat_member("-1001763293068", 201492714)
        # await api.send_message(-1002065953010, "Test message in channel")
        # print(memb)
        await message.answer(stats)
    except Exception:
        executor.traceback = traceback.format_exc()
    finally:
        await executor.logger(message)
