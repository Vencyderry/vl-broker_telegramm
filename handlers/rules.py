import time
import traceback
import asyncio

from telegrinder.rules import CallbackDataEq, Text
from telegrinder import CallbackQuery, Dispatch, Message, Keyboard, Button, keyboard_remove

from patterns import MESSAGE_RULES
from client import api, fmt
from tools import save_mess, delete_mess
from handlers.executor import ExecutorType, DispatchExecutor
from permissions_store import is_admin
from patterns import ERROR_PERMISSION, ERROR_COOLDOWN_RULES
from operations import get_user
from models import User

dp = Dispatch()


executor_get_rules_cq = DispatchExecutor(title="get_rules",
                                         type_executor=ExecutorType.KEYBOARD
                                         )


@dp.callback_query(CallbackDataEq("rules"))
async def rules_cq(cq: CallbackQuery) -> None:
    try:
        message = cq.message.unwrap().only()

        await delete_mess(message.chat.id)
        response = await api.send_message(text=MESSAGE_RULES,
                                          chat_id=message.chat.id,
                                          parse_mode=fmt.PARSE_MODE)

        await save_mess(response.unwrap())


    except Exception:
        executor_get_rules_cq.traceback = traceback.format_exc()
    finally:
        await executor_get_rules_cq.logger(cq)


executor_get_rules_message = DispatchExecutor(title="get_rules",
                                              type_executor=ExecutorType.COMMAND
                                              )


@dp.message(Text("📌Правила чата VL-BROKER"))
async def rules_message(message: Message) -> None:
    try:
        user = get_user(User.tgid, message.from_.unwrap().id)
        now = time.time()
        if now < user.cooldown_rules:
            response = await message.answer(ERROR_COOLDOWN_RULES)
            await asyncio.sleep(1.5)
            response_dlt = await api.delete_message(chat_id=message.chat.id,
                                                    message_ids=message.message_id) #response.unwrap().message_id
            print(response_dlt)
            return
        response = await api.send_message(text=MESSAGE_RULES,
                                          chat_id=message.chat.id,
                                          parse_mode=fmt.PARSE_MODE)
        user.cooldown_rules = time.time() + 60 * 60
        user.save()
    except Exception:
        executor_get_rules_message.traceback = traceback.format_exc()
    finally:
        await executor_get_rules_message.logger(message)


RULE_KEYBOARD = (
    Keyboard()
    .add(Button("📌Правила чата VL-BROKER"))
).get_markup()

executor_update_keyboard = DispatchExecutor(title="update_keyboard",
                                            permission="operation.admin",
                                            type_executor=ExecutorType.COMMAND
                                            )


@dp.message(Text(["/updkeyboard"]))
async def update_keyboard(message: Message) -> None:
    try:
        if not is_admin(message.from_.unwrap().id):
            await message.answer(ERROR_PERMISSION)
            return

        await message.answer(text="✅ Клавитура чата обновлена.",
                             reply_markup=RULE_KEYBOARD)



    except Exception:
        executor_update_keyboard.traceback = traceback.format_exc()
    finally:
        await executor_update_keyboard.logger(message)

RULE_KEYBOARD_EMPTY = (Keyboard()).empty()


executor_delete_keyboard = DispatchExecutor(title="delete_keyboard",
                                            permission="operation.admin",
                                            type_executor=ExecutorType.COMMAND
                                            )


@dp.message(Text(["/dltkeyboard"]))
async def delete_keyboard(message: Message) -> None:
    try:
        if not is_admin(message.from_.unwrap().id):
            await message.answer(ERROR_PERMISSION)
            return

        await message.answer(text="✅ Клавитура чата удалена.",
                             reply_markup=keyboard_remove())



    except Exception:
        executor_delete_keyboard.traceback = traceback.format_exc()
    finally:
        await executor_delete_keyboard.logger(message)
