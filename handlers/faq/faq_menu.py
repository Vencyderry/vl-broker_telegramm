import traceback

from telegrinder.rules import CallbackDataEq
from telegrinder import CallbackQuery, Dispatch, InlineKeyboard, InlineButton

from client import api
from tools import save_mess, delete_mess
from handlers.executor import ExecutorType, DispatchExecutor
from .faq_patterns import TEXT_FAQ_MENU

dp = Dispatch()

FAQ_KEYBOARD = (
    InlineKeyboard()
    .add(InlineButton("1", callback_data="faq_#1"))
    .add(InlineButton("2", callback_data="faq_#2"))
    .add(InlineButton("3", callback_data="faq_#3"))
    .add(InlineButton("4", callback_data="faq_#4"))
    .add(InlineButton("5", callback_data="faq_#5")).row()
    .add(InlineButton("6", callback_data="faq_#6"))
    .add(InlineButton("7", callback_data="faq_#7"))
    .add(InlineButton("8", callback_data="faq_#8"))
    .add(InlineButton("9", callback_data="faq_#9"))
    .add(InlineButton("10", callback_data="faq_#10")).row()
    .add(InlineButton("11", callback_data="faq_#11"))
    .add(InlineButton("12", callback_data="faq_#12"))
    .add(InlineButton("13", callback_data="faq_#13"))
    .add(InlineButton("14", callback_data="faq_#14"))
    .add(InlineButton("15", callback_data="faq_#15")).row()
    .add(InlineButton("16", callback_data="faq_#16"))
    .add(InlineButton("17", callback_data="faq_#17"))
    .add(InlineButton("18", callback_data="faq_#18"))
    .add(InlineButton("19", callback_data="faq_#19"))
).get_markup()


executor_faq_menu = DispatchExecutor(title="faq_menu",
                                     type_executor=ExecutorType.KEYBOARD
                                     )


@dp.callback_query(CallbackDataEq("faq_menu"))
async def faq_menu(cq: CallbackQuery) -> None:
    try:
        message = cq.message.unwrap().v

        await delete_mess(message.chat.id)
        response = await api.send_message(text=TEXT_FAQ_MENU,
                                          chat_id=message.chat.id,
                                          reply_markup=FAQ_KEYBOARD)
        await save_mess(response.unwrap())


    except Exception:
        executor_faq_menu.traceback = traceback.format_exc()
    finally:
        await executor_faq_menu.logger(cq)
