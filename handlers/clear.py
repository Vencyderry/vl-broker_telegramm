import traceback

from telegrinder import Dispatch, Message
from telegrinder.rules import Text, IsPrivate

from client import api
from handlers.executor import ExecutorType, DispatchExecutor
from handlers.start import start

dp = Dispatch()

executor = DispatchExecutor(title="clear",
                            type_executor=ExecutorType.COMMAND,
                            permission="operations.admin"
                            )
#
#
# @dp.message(Text(["/clear"], ignore_case=True) & IsPrivate())
# async def clear(message: Message) -> None:
#     try:
#         chat = await api.get_chat(chat_id=message.from_.unwrap().id)
#         await message.answer(chat.unwrap())
#         print(message.message_id)
#         for msg_id in range(message.message_id, 1, -1):
#             try:
#                 await api.delete_message(chat_id=message.chat.id,
#                                          message_id=msg_id)
#             except:
#                 pass
#             print(msg_id)
#         await start.func(message)
#
#     except Exception:
#         executor.traceback = traceback.format_exc()
#     finally:
#         await executor.logger(message)
#
