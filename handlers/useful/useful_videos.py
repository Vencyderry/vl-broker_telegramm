import traceback

from client import api, fmt
from operations import get_user
from models import User
from tools import save_mess, delete_mess
from rules import CallbackDataStartsWith
from .useful_patterns import *

from telegrinder.rules import CallbackDataEq, Command
from telegrinder import CallbackQuery, Dispatch, Message
from telegrinder import InlineKeyboard, InlineButton, Dispatch, Message
from telegrinder.rules import Text, IsPrivate
from handlers.executor import ExecutorType, DispatchExecutor

dp = Dispatch()

BACK_KEYBOARD = (
    InlineKeyboard()
    .add(InlineButton("Вернуться назад", callback_data="useful_menu")).row()
).get_markup()

executor_videos = DispatchExecutor(title="useful_videos",
                                   type_executor=ExecutorType.KEYBOARD
                                   )


@dp.callback_query(CallbackDataStartsWith("useful_video_"))
async def useful_videos(cq: CallbackQuery) -> None:
    try:
        message = cq.message.unwrap().v

        msg = UsefulVideos.get_message(cq.data.unwrap())

        await delete_mess(message.chat.id)
        response = await api.send_message(text=msg,
                                          chat_id=message.chat.id,
                                          parse_mode=fmt.PARSE_MODE,
                                          reply_markup=BACK_KEYBOARD)
        await save_mess(response.unwrap())

    except Exception:
        executor_videos.traceback = traceback.format_exc()
    finally:
        await executor_videos.logger(cq)