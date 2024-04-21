import traceback
import pandas as pd

from telegrinder.rules import CallbackDataEq
from telegrinder import CallbackQuery, Dispatch, InlineKeyboard, InlineButton

from client import api, client
from tools import save_mess, delete_mess
from handlers.executor import ExecutorType, DispatchExecutor

dp = Dispatch()

KEYBOARD = (
    InlineKeyboard()
    .add(InlineButton("Test", callback_data="date_production_1")).row()
).get_markup()


executor = DispatchExecutor(title="date_production",
                            type_executor=ExecutorType.KEYBOARD
                            )


@dp.callback_query(CallbackDataEq("date_production"))
async def date_production(cq: CallbackQuery) -> None:

    try:
        message = cq.message.unwrap().v
#https://www.toyodiy.com/parts/q?vin=NCP25-0018353
        response_api = await client.request_text(
            "https://emex.ru/catalogs/original2/modifications?vin=MXUA85-0009214"
        )
        list_frame = pd.read_html(response_api)
        for frame in list_frame:
            print(frame)
            print("\n\n")
        await delete_mess(message.chat.id)
        response = await api.send_message(text="11",
                                          chat_id=message.chat.id)
        await save_mess(response.unwrap())


    except Exception:
        executor.traceback = traceback.format_exc()
    finally:
        await executor.logger(cq)

