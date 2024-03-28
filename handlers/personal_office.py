import traceback

from client import api
from tools import save_mess, delete_mess

from telegrinder.rules import CallbackDataEq
from telegrinder import CallbackQuery
from telegrinder import InlineKeyboard, InlineButton, Dispatch
from handlers.executor import ExecutorType, DispatchExecutor

dp = Dispatch()

LOGIN_KEYBOARD = (
    InlineKeyboard()
    .add(InlineButton("Войти в личный кабинет", url="https://lk.vlb-broker.ru/?login=yes"))
).get_markup()


executor = DispatchExecutor(title="personal_office",
                            type_executor=ExecutorType.KEYBOARD
                            )


@dp.callback_query(CallbackDataEq("personal_office"))
async def personal_office(cq: CallbackQuery) -> None:
    try:
        message = cq.message.unwrap().v

        await delete_mess(message.chat.id)
        response = await api.send_message(text="""
🔹Напоминаем, что личный кабинет доступен только нашим партнёрам и клиентам.

📌Если Вам необходимо восстановить логин или пароль от своего личного кабинета, то отправьте запрос на почту: skripkina.vlb@gmail.com — в любой форме.""",
                                          chat_id=message.chat.id,
                                          reply_markup=LOGIN_KEYBOARD)
        await save_mess(response.unwrap())

    except Exception:
        executor.traceback = traceback.format_exc()
    finally:
        await executor.logger(cq)

