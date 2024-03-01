import traceback

from telegrinder.rules import CallbackDataEq
from telegrinder import CallbackQuery, Dispatch

from patterns import MESSAGE_RULES
from client import api, fmt
from tools import save_mess, delete_mess
from handlers.executor import ExecutorType, DispatchExecutor
from operations import get_system

dp = Dispatch()


executor_get_price = DispatchExecutor(title="get_rules",
                                      type_executor=ExecutorType.KEYBOARD
                                      )


@dp.callback_query(CallbackDataEq("rules"))
async def rules_cq(cq: CallbackQuery) -> None:
    try:
        message = cq.message.unwrap().v

        await delete_mess(message.chat.id)
        response = await api.send_message(text=MESSAGE_RULES,
                                          chat_id=message.chat.id,
                                          parse_mode=fmt.PARSE_MODE)

        await save_mess(response.unwrap())

        system = get_system()

    except Exception:
        executor_get_price.traceback = traceback.format_exc()
    finally:
        await executor_get_price.logger(cq)
