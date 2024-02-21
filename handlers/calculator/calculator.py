import traceback

from telegrinder.rules import CallbackDataEq
from telegrinder import CallbackQuery, Dispatch, InlineKeyboard, InlineButton
from telegrinder.modules import logger

from client import api, ctx
from tools import save_mess, delete_mess
from rules import Calculator

dp = Dispatch()

STRATEGY_KEYBOARD = (
    InlineKeyboard()
    .add(InlineButton("Автомобиль", callback_data="auto"))
    .add(InlineButton("Мотоцикл", callback_data="moto"))
).get_markup()


@dp.callback_query(CallbackDataEq("calculator"))
async def calculator_cq(cq: CallbackQuery) -> None:
    try:
        message = cq.message.unwrap().v

        ctx.set(f"calculator_{cq.from_.id}", {})

        await delete_mess(message.chat.id)
        response = await api.send_message(text="🔹Выберите тип транспортного средства:",
                                          chat_id=message.chat.id,
                                          reply_markup=STRATEGY_KEYBOARD)
        await save_mess(response.unwrap())

        await Calculator.set(message.chat.id, Calculator.STRATEGY)

    except Exception:
        logger.error(traceback.format_exc())





