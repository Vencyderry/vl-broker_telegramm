import traceback
import time

from telegrinder import InlineKeyboard, InlineButton
from telegrinder import ABCMiddleware, Message
from telegrinder.types import Nothing, ChatType
from telegrinder.modules import logger

from config import USERS_CHAT, LOG_SWEAR_CHAT, MAIN_CHATS
from patterns import GREETING_JOIN_CHAT
from client import api, fmt
from operations import *
from tools import save_mess, detector_swear, decode
from handlers.admins.punishment import Punishment


class JoinChatMiddleware(ABCMiddleware[Message]):
    async def pre(self, event: Message, ctx: Context) -> None:

        if event.chat.type in ["supergroup", "group"]:
            if event.chat.id == int(USERS_CHAT):
                if event.new_chat_members is not Nothing:
                    user_join = event.new_chat_members.unwrap()[0]
                    if not user_join.is_bot:

                        try:
                            keyboard_rules = (
                                InlineKeyboard()
                                .add(InlineButton("Правила чата", callback_data="rules"))
                            ).get_markup()

                            await api.send_message(text=GREETING_JOIN_CHAT,
                                                   chat_id=user_join.id,
                                                   parse_mode=fmt.PARSE_MODE,
                                                   reply_markup=keyboard_rules
                                                   )
                        except:
                            pass

                        user = get_user(User.tgid, user_join.id)
                        if user is not None:
                            user.join_chat_date = time.time()
                            user.save()


class MessageRouterMiddleware(ABCMiddleware[Message]):
    async def pre(self, event: Message, ctx: Context) -> None:
        try:

            system = get_system()

            system.messages_processed += 1
            system.messages_processed_all += 1

            system.save()

        except Exception:
            logger.error(f"Error in middleware <MessageRouterMiddleware>\n{traceback.format_exc()}")


class RegistrationMiddleware(ABCMiddleware[Message]):
    async def pre(self, event: Message, ctx: Context) -> bool:
        try:
            if event.from_ is not Nothing:
                user = get_user(User.tgid, event.from_.unwrap().id)

                if not user:

                    if event.from_.unwrap().username == Nothing:
                        username = event.from_.unwrap().id
                    else:
                        username = event.from_.unwrap().username.unwrap().lower()

                    User(
                        tgid=event.from_.unwrap().id,
                        username=username,
                        registration_date=time.time()
                    ).save()

                    user = get_user(User.tgid, event.from_.unwrap().id)

                    if username != event.from_.unwrap().id:
                        msg = f"[{username}|{event.from_.unwrap().id}]"
                    else:
                        msg = f"[{username}]"

                    logger.info(f"[REGISTRATION] User [{event.from_.unwrap().first_name}] "
                                f"{msg} is registered with ID [{user.id}]")
                return True

        except Exception:
            logger.error(f"Error in middleware <RegistrationMiddleware>\n{traceback.format_exc()}")


class MessageDeleteMiddleware(ABCMiddleware[Message]):
    async def pre(self, event: Message, ctx: Context) -> bool:
        try:
            if event.chat.type == "private":
                await save_mess(event)
            return True
        except Exception:
            logger.error(f"Error in middleware <MessageDeleteMiddleware>\n{traceback.format_exc()}")


class SwearFilterMiddleware(ABCMiddleware[Message]):

    async def post(self, event: Message, responses: list, ctx: Context):
        try:
            if str(event.chat.id) in MAIN_CHATS:
                if event.text is not Nothing:
                    detect = detector_swear(event.text.unwrap().lower())
                    if detect['result']:

                        if event.from_.unwrap().username == Nothing:
                            username = event.from_.unwrap().full_name
                        else:
                            username = "@" + event.from_.unwrap().username.unwrap()

                        await api.delete_message(message_id=event.message_id, chat_id=event.chat.id)

                        text = f"""🔹Сообщение от пользователя {username} удалено по причине нарушения правила, запрещающего мат как прямой, так и завуалированный.\n\n"""


                        user = get_user(User.tgid, event.from_.unwrap().id)
                        punishment = Punishment(user.punishment)

                        if punishment.is_free() or punishment.is_kick():
                            user.punishment = Punishment.WARN
                            text += "📌Пользователь, повторно нарушивший правила чата, будет заблокирован."
                            log_swear = "WARN"

                        elif punishment.is_warn():
                            system = get_system()
                            admins = decode(system.administrators)
                            if event.from_.unwrap().id not in admins:
                                await api.ban_chat_member(chat_id=event.chat.id,
                                                          user_id=event.from_.unwrap().id,
                                                          until_date=time.time() + 60 * 60 * 24 * 30)
                            user.punishment = Punishment.KICK
                            text += "📌Пользователь заблокирован на 30 дней."
                            log_swear = "BAN"

                        await api.send_message(text=text,
                                               chat_id=event.chat.id)

                        user.save()

                    elif detect['only_warn']:

                        if event.from_.unwrap().username == Nothing:
                            username = event.from_.unwrap().full_name
                        else:
                            username = "@" + event.from_.unwrap().username.unwrap()

                        await api.delete_message(message_id=event.message_id, chat_id=event.chat.id)

                        await api.send_message(text=f"🔹Сообщение от пользователя {username} удалено по причине нарушения правила, запрещающего мат как прямой, так и завуалированный.\n\n"
                                                    f"📌Пользователь, повторно нарушивший правила чата, будет заблокирован.",
                                               chat_id=event.chat.id)

                        log_swear = "WARN"

                    else:
                        return

                    await api.send_message(
                        text=f"LogSwear | <{log_swear}> | {username} | Найден фрагмент \"{detect['fragment']}\" похожий на \"{detect['word']}\" ",
                        chat_id=LOG_SWEAR_CHAT)

        except Exception:
            logger.error(f"Error in middleware <SwearFilterMiddleware>\n{traceback.format_exc()}")




