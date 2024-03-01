import traceback

from telegrinder import InlineKeyboard, InlineButton
from telegrinder import ABCMiddleware, Message
from telegrinder.types import Nothing
from telegrinder.modules import logger

from config import USERS_CHAT
from patterns import GREETING_JOIN_CHAT
from client import api, fmt
from operations import *
from tools import save_mess


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




