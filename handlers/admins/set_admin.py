import traceback

from client import api
from handlers.executor import (ExecutorType,
                               DispatchExecutor,
                               target_search,
                               TargetCommandExecutor)
from patterns import *
from permissions_store import is_admin, is_sr_admin

from telegrinder import InlineKeyboard, InlineButton, Dispatch, Message
from telegrinder.rules import Text, IsPrivate, Command, Argument
from operations import get_system
from tools import decode

dp = Dispatch()

executor = DispatchExecutor(title="set_admin",
                            permission="operation.admin",
                            type_executor=ExecutorType.COMMAND
                            )


@dp.message(Command(["setadmin"], Argument("target", [target_search], optional=True)))
async def set_admin(message: Message, target: str = None) -> None:
    try:
        user = TargetCommandExecutor(message, target).search()
        system = get_system()
        admins = decode(system.administrators)

        if user is None:
            await message.answer(ERROR_TARGET)
            return
        if not is_admin(message.from_.unwrap().id) and not is_sr_admin(message.from_.unwrap().id):
            await message.answer(ERROR_PERMISSION)
            return

        if is_admin(user.tgid):
            user.group = "Default"
            msg = "больше не админ."
            admins.remove(user.tgid)
        else:
            user.group = "Admin"
            msg = "теперь админ."
            admins.append(user.tgid)

        system.administrators = admins
        system.save()
        user.save()
        await message.answer(f"✅ Пользователь @{user.username} {msg}",
                             disable_notification=True)

    except Exception:
        executor.traceback = traceback.format_exc()
    finally:
        await executor.logger(message)

