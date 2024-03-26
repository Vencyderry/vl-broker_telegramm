import traceback

from telegrinder import CallbackQuery, Dispatch, InlineKeyboard, InlineButton

from client import api
from tools import save_mess, delete_mess
from rules import CallbackDataStartsWith
from handlers.executor import ExecutorType, DispatchExecutor
from .svh_patterns import texts

dp = Dispatch()

BACK_KEYBOARD = (
    InlineKeyboard()
    .add(InlineButton("Вернуться назад", callback_data="svh_menu")).row()
).get_markup()

executor_info_svh = DispatchExecutor(title="info",
                                     type_executor=ExecutorType.KEYBOARD
                                     )


@dp.callback_query(CallbackDataStartsWith("info_svh_"))
async def svh_info(cq: CallbackQuery) -> None:
    try:
        message = cq.message.unwrap().v

        svh_text = texts[cq.data.unwrap()]

        if svh_text is None:
            svh_text = "📌Информация о данном СВХ ещё не загружена в бот."

        await delete_mess(message.chat.id)
        response = await api.send_message(text=svh_text,
                                          chat_id=message.chat.id,
                                          reply_markup=BACK_KEYBOARD)
        await save_mess(response.unwrap())


    except Exception:
        executor_info_svh.traceback = traceback.format_exc()
    finally:
        await executor_info_svh.logger(cq)
