import asyncio
import traceback
import time

from client import api, fmt, ctx
from handlers.executor import ExecutorType, DispatchExecutor
from permissions_store import is_admin
from patterns import ERROR_PERMISSION
from operations import get_system, get_users_all, get_users
from models import User
from typing import Any

from tools import digit, delete_mess, save_mess, time_converter
from rules import CallbackDataStartsWith, Distribution

from telegrinder.tools import bold, escape, HTMLFormatter, link
from telegrinder import InlineKeyboard, InlineButton, Dispatch, Message, CallbackQuery
from telegrinder.rules import Text, IsPrivate, Command, Argument
from telegrinder.types import ReplyParameters

dp = Dispatch()


ADD_MESSAGE_KEYBOARD = (
    InlineKeyboard()
    .add(InlineButton("Оставить заявку", callback_data="add_message:2")).row()
    .add(InlineButton("Оставить отзыв", callback_data="add_message:1")).row()
    .add(InlineButton("❌", callback_data="add_message:0"))
).get_markup()

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
        ctx.set("distribution", {"message_id": message.message_id, "from_chat_id": message.chat.id})

        response = await message.answer(text=f"🧾 Выберите дополнительное сообщение или его отсутствие.\n\n",
                                        reply_markup=ADD_MESSAGE_KEYBOARD)
        await save_mess(response.unwrap())

        # удаление пересланного сообщения
        messages_storage = ctx.get(f"messages_{message.chat.id}")
        messages_storage.remove(message.message_id)
        ctx.set(f"messages_{message.chat.id}", messages_storage)

        await Distribution.set(message.chat.id, Distribution.ADD_MESSAGE)

    except Exception:
        executor.traceback = traceback.format_exc()
    finally:
        await executor.logger(message, intermediate=True)


@dp.callback_query(CallbackDataStartsWith("add_message"))
async def distribution_add_message(cq: CallbackQuery) -> None:
    try:
        users = get_users_all()
        distribution = ctx.get("distribution")

        type_add_message = int(cq.data.unwrap().replace("add_message:", ""))
        distribution["type_add_message"] = type_add_message

        ctx.set("distribution", distribution)

        response = await api.send_message(chat_id=cq.message.unwrap().v.chat.id,
                                          text=f"📌 Подтвердите отправку рассылки {digit(len(users))} пользователям.\n\n",
                                          reply_markup=CONFIRM_KEYBOARD
                                          )
        await save_mess(response.unwrap())

        await Distribution.delete(cq.message.unwrap().v.chat.id)

    except Exception:
        executor.traceback = traceback.format_exc()
    finally:
        await executor.logger(cq, intermediate=True)


@dp.callback_query(CallbackDataStartsWith("distribution"))
async def distribution_confirm(cq: CallbackQuery) -> None:
    try:
        confirm = int(cq.data.unwrap().replace("distribution:", ""))

        users = get_users_all()
        # users = get_users("group", "Admin")

        # users = [7022086113, 7028770823, 113431]

        if confirm:
            distribution_ = ctx.get("distribution")
            message_id = distribution_["message_id"]
            from_chat_id = distribution_["from_chat_id"]
            type_add_message = distribution_["type_add_message"]

            await delete_mess(cq.message.unwrap().v.chat.id)

            time = time_converter(((len(users) // 20) * 3 + len(users) * 0.5), 0)
            await api.send_message(chat_id=cq.message.unwrap().v.chat.id,
                                   text=f"⏱️ Рассылка запущена, примерный расчет полной отправки рассылки ~{time}"
                                   )

            count = await start_distribution(users, from_chat_id, message_id, type_add_message)

            message_result = f"✅ Рассылка успешно отправлена {digit(count)}/{digit(len(users))} пользователям."

        else:
            message_result = f"✅ Рассылка отменена."

        ctx.delete(f"distribution")

        await api.send_message(chat_id=cq.message.unwrap().v.chat.id,
                               text=message_result
                               )

    except Exception:
        executor.traceback = traceback.format_exc()
    finally:
        await executor.logger(cq, intermediate=True)


async def start_distribution(users: list[User], from_chat_id: int, message_id, type_add_message) -> int:
    counter = 0

    for user in users:

        if counter % 20 == 0:
            await asyncio.sleep(3)

        try:
            response = await send_distribution(user, from_chat_id, message_id, type_add_message)

            if not hasattr(response, "error"):
                counter += 1

        except Exception:
            pass

    return counter

ADD_MESSAGE_KEYBOARD_2 = (
    InlineKeyboard()
    .add(InlineButton("Оставить заявку", callback_data="app"))
).get_markup()

ADD_MESSAGE_KEYBOARD_1 = (
    InlineKeyboard()
    .add(InlineButton("Оставить отзыв", url="https://vk.com/reviews-211743331"))
).get_markup()


async def send_distribution(user: User, from_chat_id: int, message_id, type_add_message) -> Any:
    responses = []
    message_log = f"[{user.tgid}] | "

    response = await api.forward_message(chat_id=user.tgid,
                                         from_chat_id=from_chat_id,
                                         message_id=message_id
                                         )

    message_log += f"{response.unwrap().message_id} | "

    if type_add_message == 2:
        response_ = await api.send_message(chat_id=user.tgid,
                                           text=HTMLFormatter(bold("Воспользуйтесь выгодным предложением:")),
                                           parse_mode=fmt.PARSE_MODE,
                                           reply_markup=ADD_MESSAGE_KEYBOARD_2
                                           )
        message_log += f"{response_.unwrap().message_id} | "

    elif type_add_message == 1:
        response_ = await api.send_message(chat_id=user.tgid,
                                           text=HTMLFormatter(bold("Участвуйте в розыгрыше 10 000 рублей!")),
                                           parse_mode=fmt.PARSE_MODE,
                                           reply_markup=ADD_MESSAGE_KEYBOARD_1
                                           )
        message_log += f"{response_.unwrap().message_id}"

    print(message_log)

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
