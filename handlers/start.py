import traceback

from client import api
from operations import get_user
from models import User

from telegrinder import InlineKeyboard, InlineButton, Dispatch, Message
from telegrinder.rules import Text, IsPrivate
from handlers.executor import ExecutorType, DispatchExecutor

dp = Dispatch()

kb = (
    InlineKeyboard()
    .add(InlineButton("Оставить заявку", callback_data="app")).row()
    .add(InlineButton("Открыть прайс-лист 2024", callback_data="get_price")).row()
    .add(InlineButton("Узнать информацию о СВХ", callback_data="svh_menu")).row()
    .add(InlineButton("Узнать курс валют", callback_data="currency")).row()
    .add(InlineButton("Открыть калькулятор", callback_data="calculator")).row()
    .add(InlineButton("Смотреть полезные видео", callback_data="useful_menu")).row()
    .add(InlineButton("Войти в личный кабинет", callback_data="personal_office")).row()
    .add(InlineButton("Перейти в чат VL-BROKER", url="https://t.me/+k9w6qxLAOiEwMWJi"))
).get_markup()

executor = DispatchExecutor(title="start",
                            type_executor=ExecutorType.COMMAND
                            )


@dp.message(Text(["/start", "/menu"], ignore_case=True) & IsPrivate())
async def start(message: Message) -> None:
    try:
        response = await message.answer(
            text=f"🔹Здравствуйте, {message.from_.unwrap().first_name}!\nВы можете воспользоваться следующими опциями:",
            reply_markup=kb)

        response = response.unwrap()
        await api.pin_chat_message(message_id=response.message_id, chat_id=response.chat.id)
    except Exception:
        executor.traceback = traceback.format_exc()
    finally:
        await executor.logger(message)

