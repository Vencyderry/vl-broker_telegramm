import traceback

from client import api
from tools import save_mess, delete_mess

from telegrinder.rules import CallbackDataEq
from telegrinder import CallbackQuery
from telegrinder import InlineKeyboard, InlineButton, Dispatch
from handlers.executor import ExecutorType, DispatchExecutor

dp = Dispatch()

USEFUL_KEYBOARD = (
    InlineKeyboard()
    .add(InlineButton("Процесс таможенного оформления", callback_data="useful_video_1")).row()
    .add(InlineButton("Перечень необходимых документов на ТО", callback_data="useful_video_2")).row()
    .add(InlineButton("Как оплатить через Сбербанк?", callback_data="useful_video_3")).row()
    .add(InlineButton("Как зарегистрироваться в СЭП?", callback_data="useful_video_4")).row()
    .add(InlineButton("Всё об утилизационном сборе", callback_data="useful_video_5")).row()
    .add(InlineButton("Причины \"перестоя\" на СВХ", callback_data="useful_video_6")).row()
    .add(InlineButton("Параллельный импорт в Россию", callback_data="useful_video_7")).row()
    .add(InlineButton("Как выбрать товары для импорта?", callback_data="useful_video_8")).row()
).get_markup()


executor_menu = DispatchExecutor(title="useful_menu",
                                 type_executor=ExecutorType.KEYBOARD
                                 )


@dp.callback_query(CallbackDataEq("useful_menu"))
async def useful_menu(cq: CallbackQuery) -> None:
    try:
        message = cq.message.unwrap().v

        await delete_mess(message.chat.id)
        response = await api.send_message(text=f"📌Полезные видео:",
                                          chat_id=message.chat.id,
                                          reply_markup=USEFUL_KEYBOARD)
        await save_mess(response.unwrap())

    except Exception:
        executor_menu.traceback = traceback.format_exc()
    finally:
        await executor_menu.logger(cq)

