import traceback

from client import api
from operations import get_user
from models import User
from tools import save_mess, delete_mess

from telegrinder.rules import CallbackDataEq, Command
from telegrinder import CallbackQuery, Dispatch, Message
from telegrinder import InlineKeyboard, InlineButton, Dispatch, Message
from telegrinder.rules import Text, IsPrivate
from handlers.executor import ExecutorType, DispatchExecutor

dp = Dispatch()

executor = DispatchExecutor(title="useful",
                            type_executor=ExecutorType.COMMAND
                            )


@dp.callback_query(CallbackDataEq("useful"))
async def useful(cq: CallbackQuery) -> None:
    try:
        message = cq.message.unwrap().v

        await delete_mess(message.chat.id)
        response = await api.send_message(text=f"📌Полезные опции:\nhttps://youtu.be/nS-PQmCEB_k",
                                          chat_id=message.chat.id)
        await save_mess(response.unwrap())

    except Exception:
        executor.traceback = traceback.format_exc()
    finally:
        await executor.logger(cq)

