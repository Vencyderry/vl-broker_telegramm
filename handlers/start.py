import traceback

from client import api
from operations import get_user
from models import User

from telegrinder import InlineKeyboard, InlineButton, Dispatch, Message, Keyboard, Button
from telegrinder.rules import Text, IsPrivate
from handlers.executor import ExecutorType, DispatchExecutor

dp = Dispatch()

kb = (
    InlineKeyboard()
    .add(InlineButton("Оставить заявку", callback_data="app")).row()
    .add(InlineButton("Открыть прайс-лист 2024", callback_data="get_price")).row()
    .add(InlineButton("Узнать о специальных предложениях", callback_data="promotions")).row()
    .add(InlineButton("Узнать информацию о СВХ", callback_data="svh_menu")).row()
    .add(InlineButton("Узнать дату выпуска авто", callback_data="date_production")).row()
    .add(InlineButton("Узнать курс валют", callback_data="currency")).row()
    .add(InlineButton("Открыть калькулятор", callback_data="calculator")).row()
    .add(InlineButton("Смотреть полезные видео", callback_data="useful_menu")).row()
    .add(InlineButton("Войти в личный кабинет", callback_data="personal_office")).row()
    .add(InlineButton("Узнать ответы на частые вопросы", callback_data="faq_menu")).row()
    .add(InlineButton("Правила чата VL-BROKER", callback_data="rules")).row()
    .add(InlineButton("Перейти в чат VL-BROKER", url="https://t.me/+k9w6qxLAOiEwMWJi"))
).get_markup()

# kb = (
#     Keyboard()
#     .add(Button("Оставить заявку")).row()
#     .add(Button("Открыть прайс-лист 2024")).row()
#     .add(Button("Узнать о специальных предложениях")).row()
#     .add(Button("Узнать информацию о СВХ")).row()
#     .add(Button("Узнать дату выпуска авто")).row()
#     .add(Button("Узнать курс валют")).row()
#     .add(Button("Открыть калькулятор")).row()
#     .add(Button("Смотреть полезные видео")).row()
#     .add(Button("Войти в личный кабинет")).row()
#     .add(Button("Узнать ответы на частые вопросы",)).row()
#     .add(Button("Правила чата VL-BROKER")).row()
#     .add(Button("Перейти в чат VL-BROKER"))
# ).get_markup()

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

