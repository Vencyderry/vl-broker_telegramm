from client import api
from telegrinder import InlineKeyboard, InlineButton, Dispatch, Message
from telegrinder.rules import Text, IsPrivate
from tools import ExecutorType, DispatchExecutor

dp = Dispatch()


@dp.message(Command(["pin"]))
async def start(message: Message, args: list[str] = None) -> None:

    if not await is_admin(message.from_.id):
        await message.answer(ERROR_PERMISSION)
        return

    pattern = args if args is None else args[0]


    if pattern == "pattern1":

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


