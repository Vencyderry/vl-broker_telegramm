import traceback

from telegrinder.rules import CallbackDataEq
from telegrinder import CallbackQuery, Dispatch, InlineKeyboard, InlineButton

from client import api
from tools import save_mess, delete_mess
from handlers.executor import ExecutorType, DispatchExecutor

dp = Dispatch()

SVH_KEYBOARD = (
    InlineKeyboard()
    .add(InlineButton("СВХ «КМТС»", callback_data="info_svh_1")).row()
    .add(InlineButton("СВХ «Автоимпорт-ДВ»", callback_data="info_svh_2")).row()
    .add(InlineButton("СВХ «ДальВЭД»", callback_data="info_svh_3")).row()
    .add(InlineButton("СВХ «ФЕМСТА»", callback_data="info_svh_4")).row()
    .add(InlineButton("СВХ «ВМРП»", callback_data="info_svh_5")).row()
    .add(InlineButton("СВХ «ВАТ»", callback_data="info_svh_6")).row()
    .add(InlineButton("СВХ «Влад Пром»", callback_data="info_svh_7")).row()
    .add(InlineButton("СВХ «ВМС»", callback_data="info_svh_8")).row()
    .add(InlineButton("СВХ «Мортэк-ДВ»", callback_data="info_svh_9")).row()
    .add(InlineButton("СВХ «ДАЛЬКОМХОЛОД»", callback_data="info_svh_10")).row()
    .add(InlineButton("СВХ «Пасифик Лоджистик»", callback_data="info_svh_11")).row()
    .add(InlineButton("СВХ «ЧЭМК»", callback_data="info_svh_12")).row()
    .add(InlineButton("СВХ «Соллерс»", callback_data="info_svh_13"))
).get_markup()


executor_svh_menu = DispatchExecutor(title="svh_menu",
                                     type_executor=ExecutorType.KEYBOARD
                                     )


@dp.callback_query(CallbackDataEq("svh_menu"))
async def svh_menu(cq: CallbackQuery) -> None:
    try:
        message = cq.message.unwrap().v

        await delete_mess(message.chat.id)
        response = await api.send_message(text="🔹Выберите интересующий СВХ:",
                                          chat_id=message.chat.id,
                                          reply_markup=SVH_KEYBOARD)
        await save_mess(response.unwrap())


    except Exception:
        executor_svh_menu.traceback = traceback.format_exc()
    finally:
        await executor_svh_menu.logger(cq)
