import traceback

from client import api
from tools import save_mess, delete_mess

from telegrinder.rules import CallbackDataEq
from telegrinder import CallbackQuery
from telegrinder import InlineKeyboard, InlineButton, Dispatch
from handlers.executor import ExecutorType, DispatchExecutor

dp = Dispatch()

PROMO_KEYBOARD = (
    InlineKeyboard()
    .add(InlineButton("Новогоднее предложение от VL-BROKER", callback_data="promo_0")).row()
    .add(InlineButton("Подарок ко дню рождения", callback_data="promo_1")).row()
).get_markup()


executor_menu = DispatchExecutor(title="promo_menu",
                                 type_executor=ExecutorType.KEYBOARD
                                 )


@dp.callback_query(CallbackDataEq("promotions"))
async def promo_menu(cq: CallbackQuery) -> None:
    try:
        message = cq.message.unwrap().v

        await delete_mess(message.chat.id)
        response = await api.send_message(text=f"📌Специальные предложения:",
                                          chat_id=message.chat.id,
                                          reply_markup=PROMO_KEYBOARD)
        await save_mess(response.unwrap())

    except Exception:
        executor_menu.traceback = traceback.format_exc()
    finally:
        await executor_menu.logger(cq)

