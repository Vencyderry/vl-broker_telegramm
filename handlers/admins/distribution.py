import asyncio
import traceback
import time

from client import api, fmt, ctx
from handlers.executor import ExecutorType, DispatchExecutor
from permissions_store import is_admin
from patterns import ERROR_PERMISSION
from operations import get_system, get_users_all
from models import User
from typing import Any

from tools import digit, delete_mess, save_mess
from rules import CallbackDataStartsWith, Distribution

from telegrinder.tools import bold, escape, HTMLFormatter, link
from telegrinder import InlineKeyboard, InlineButton, Dispatch, Message, CallbackQuery
from telegrinder.rules import Text, IsPrivate, Command, Argument
from telegrinder.types import ReplyParameters

dp = Dispatch()


CONFIRM_KEYBOARD = (
    InlineKeyboard()
    .add(InlineButton("Подтверждаю", callback_data="distribution:1")).row()
    .add(InlineButton("Отмена", callback_data="distribution:0"))
).get_markup()

executor = DispatchExecutor(title="distribution",
                            permission="operations.admin",
                            type_executor=ExecutorType.COMMAND
                            )


@dp.message(Text("/рассылка"))
async def distribution(message: Message) -> None:
    try:
        if not is_admin(message.from_.unwrap().id):
            await message.answer(ERROR_PERMISSION)
            return

        response = await message.answer(text="📲 Пришлите сообщение для рассылки.")
        await save_mess(response.unwrap())

        await Distribution.set(message.chat.id, Distribution.TEXT)

    except Exception:
        executor.traceback = traceback.format_exc()
    finally:
        await executor.logger(message)


@dp.message(Distribution(Distribution.TEXT))
async def distribution_text(message: Message) -> None:
    try:
        users = get_users_all()
        ctx.set("distribution", {"message_id": message.message_id, "from_chat_id": message.chat.id})

        response = await message.answer(text=f"📌 Подтвердите отправку рассылки {digit(len(users))} пользователям.\n\n",
                                        reply_markup=CONFIRM_KEYBOARD)
        await save_mess(response.unwrap())

        await Distribution.delete(message.chat.id)

    except Exception:
        executor.traceback = traceback.format_exc()
    finally:
        await executor.logger(message, intermediate=True)


@dp.callback_query(CallbackDataStartsWith("distribution"))
async def calculator_auto_cancel(cq: CallbackQuery) -> None:
    try:
        confirm = int(cq.data.unwrap().replace("distribution:", ""))

        users = get_users_all()

        users = [7022086113, 7028770823, 113431]

        if confirm:
            message_id = ctx.get("distribution")["message_id"]
            from_chat_id = ctx.get("distribution")["from_chat_id"]

            count = await start_distribution(users, from_chat_id, message_id)

            await delete_mess(cq.message.unwrap().v.chat.id)
            message_result = f"✅ Рассылка успешно отправлена {digit(count)}/{digit(len(users))} пользователям."

        else:
            ctx.delete(f"distribution")
            message_result = f"✅ Рассылка отменена."

        await api.send_message(chat_id=cq.message.unwrap().v.chat.id,
                               text=message_result
                               )


    except Exception:
        executor.traceback = traceback.format_exc()
    finally:
        await executor.logger(cq, intermediate=True)


async def start_distribution(users: list[User], from_chat_id: int, message_id) -> int:
    counter = 0

    for user in users:

        if counter % 20 == 0:
            await asyncio.sleep(3)

        try:
            response = await send_distribution(user, from_chat_id, message_id)

            if not hasattr(response, "error"):
                counter += 1

        except Exception:
            pass

    return counter


async def send_distribution(user: User, from_chat_id: int, message_id) -> Any:
    response = await api.forward_message(chat_id=user,
                                         from_chat_id=from_chat_id,
                                         message_id=message_id
                                         )
    return response

# @dp.message(Command("рассылка", Argument("text_msg"), separator="-"))
# async def distribution(message: Message, text_msg) -> None:
#     try:
#         if not is_admin(message.from_.unwrap().id):
#             await message.answer(ERROR_PERMISSION)
#             return
#
#         msg = message.text.unwrap().replace("/рассылка ", "")
#
#         photo = message.photo.unwrap_or(None)
#
#         system = get_system()
#         users = get_users_all()
#
#         await delete_mess(message.chat.id)
#         response = await message.answer(text="📲 Ваше сообщение готово.\n"
#                                              f"📌 Подтвердите отправку рассылки {digit(len(users))} пользователям.\n\n"
#                                              f"{text_msg}",
#                                         reply_markup=CONFIRM_KEYBOARD,
#                                         document=document.file_id if document else document,
#                                         photo=photo.file_id if photo else photo)
#         await save_mess(response.unwrap())
#
#         ctx.set(f"distribution", text_msg)
#         ctx.set(f"distribution:attachments", {"photo": photo, "document": document})
#
#     except Exception:
#         executor.traceback = traceback.format_exc()
#     finally:
#         await executor.logger(message)
#
#
# @dp.callback_query(CallbackDataStartsWith("distribution"))
# async def calculator_auto_cancel(cq: CallbackQuery) -> None:
#     try:
#         confirm = int(cq.data.unwrap().replace("distribution:", ""))
#
#         # users = get_users_all()
#
#         users = [7022086113, 7028770823, 113431]
#         text_msg = ctx.get(f"distribution")
#
#         await delete_mess(cq.message.unwrap().v.chat.id)
#         if confirm:
#             count = await start_distribution(users, text_msg)
#             message_result = f"✅ Рассылка успешно отправлена {digit(count)}/{digit(len(users))} пользователям."
#         else:
#             ctx.delete(f"distribution")
#             message_result = (f"✅ Рассылка отменена."
#                               f"""
# {HTMLFormatter(bold("Что такое коносамент?"))}
#
# {HTMLFormatter(escape("🔹Коносамент — документ, выдаваемый перевозчиком груза грузовладельцу. Он удостоверяет право собственности на отгруженный товар."))}
#
# {HTMLFormatter(escape("📌А для чего нужен коносамент можно узнать в публикации: "))}{HTMLFormatter(link("https://t.me/vlbroker/270", "Коносамент "))}
# """)
#
#         await api.send_message(chat_id=cq.message.unwrap().v.chat.id,
#                                text=message_result)
#
#     except Exception:
#         executor.traceback = traceback.format_exc()
#     finally:
#         await executor.logger(cq, intermediate=True)
#
#
# async def start_distribution(users: list[User], text: str) -> int:
#     counter = 0
#     for user in users:
#
#         if counter % 20 == 0:
#             await asyncio.sleep(3)
#
#         try:
#             response = await api.send_message(chat_id=user,
#                                               text=text,
#                                               parse_mode=fmt.PARSE_MODE)
#
#             if not hasattr(response, "error"):
#                 counter += 1
#
#         except Exception:
#             pass
#
#     return counter


