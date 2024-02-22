from telegrinder import InlineKeyboard, InlineButton, Dispatch, Message
from telegrinder.rules import Text, IsPrivate

from client import api
from permissions_store import is_admin
from handlers.executor import ExecutorType, DispatchExecutor

dp = Dispatch()


@dp.message(Text("/pin"))
async def pin_message(message: Message) -> None:

    if not is_admin(message.from_.unwrap().id) and not is_sr_admin(message.from_.unwrap().id):
        await message.answer(ERROR_PERMISSION)
        return

    if "pattern1" in message.text:

        message_pin = "📌Оставить заявку на таможенное оформление:"
        keyboard_application = (
            InlineKeyboardBuilder()
            .add(URL("Оставить заявку", "https://t.me/vl_broker_bot"))
            .build()
        )

        message_to_bot = await api.send_message(text=message_pin,
                                                chat_id=message.chat.id,
                                                reply_markup=keyboard_application)

    else:
        message_pin = message.text.replace("/pin ", "")

        message_to_bot = await api.send_message(text=message_pin,
                                                chat_id=message.chat.id)

    await api.pin_chat_message(message_id=message_to_bot.message_id,
                               chat_id=message.chat.id
                               )


