import datetime
import traceback

from operations import get_system, get_user
from models import User, System
from client import ctx, tz
from tools import decode

from telegrinder import Message, CallbackQuery
from telegrinder.types import Nothing
from telegrinder.modules import logger


def target_search(target: str) -> str | None:
    if target:
        return target
    return None


class TargetCommandExecutor:
    def __init__(self,
                 event: Message | CallbackQuery,
                 target: str = None):

        self.event = event
        self.target = target if not target else target.replace("@", "").lower()

    def search(self) -> User | None:
        if self.target:
            user = get_user(User.username, self.target)
            return user
        elif self.event.reply_to_message is not Nothing:
            user = get_user(User.tgid, self.event.reply_to_message.unwrap().from_.unwrap().id)
            return user
        else:
            return None


class ExecutorType:

    KEYBOARD = "keyboard"
    COMMAND = "command"


class DispatchExecutor:

    def __init__(self, title: str, permission: str = "operation.default", type_executor: str = None):
        self.title = title
        self.permission = permission
        self.type_executor = type_executor
        self.traceback = None

    async def logger(self, data, intermediate: bool = False):
        try:
            chat_type: str = "UNKNOWN"

            if isinstance(data, Message):
                data: Message
                from_ = data.from_.unwrap()
                chat_type = data.chat.type

            elif isinstance(data, CallbackQuery):
                data: CallbackQuery
                from_ = data.from_
                message = data.message.unwrap().v
                chat_type = message.chat.type

            if not intermediate:

                user = get_user(User.tgid, from_.id)
                username = "Unknown"
                if user is not None:
                    username = user.username

                msg_logger = f"[{chat_type.upper()}] [{username}] [{from_.id}] "\
                             f"dispatched REPLACE_TYPE_DISPATCH {self.title} [{self.permission}]"

                if self.type_executor == "command":
                    msg_logger = msg_logger.replace("REPLACE_TYPE_DISPATCH", "command")

                elif self.type_executor == "keyboard":
                    msg_logger = msg_logger.replace("REPLACE_TYPE_DISPATCH", "keyboard / button")

                if self.traceback is not None:
                    logger.warning("Error in dispatcher")
                    print(self.traceback)
                    msg_logger += " with [ERROR]"

                logger.info(msg_logger)

                await self.mark_statistics(data)

            else:
                if self.traceback is not None:
                    logger.warning(f"Error in structure [{self.title}]")
                    print(self.traceback)

        except Exception:
            logger.warning(f"Error in executor {self.title} [logger]\n{str(traceback.format_exc())}")

    async def mark_statistics(self, data):
        try:
            if isinstance(data, Message):
                data: Message
                from_ = data.from_.unwrap()

            elif isinstance(data, CallbackQuery):
                data: CallbackQuery
                from_ = data.from_
            else:
                from_ = None

            system = get_system()

            match self.title:
                case "application":
                    system.statistic_application += 1
                    await time_statistics(from_.id, system)
                case "svh_menu":
                    system.statistic_svh += 1
                    await time_statistics(from_.id, system)
                case "useful_menu":
                    system.statistic_useful += 1
                    await time_statistics(from_.id, system)
                case "personal_office":
                    system.statistic_personal_office += 1
                    await time_statistics(from_.id, system)
                case "calculator_moto":
                    system.statistic_calculator += 1
                    await time_statistics(from_.id, system)
                case "calculator_auto":
                    system.statistic_calculator += 1
                    await time_statistics(from_.id, system)
                case "currency":
                    system.statistic_currency += 1
                    await time_statistics(from_.id, system)
                case "get_price":
                    system.statistic_price += 1
                    await time_statistics(from_.id, system)
                case "start":
                    system.statistic_start += 1
                    await time_statistics(from_.id, system)
                case "faq_menu":
                    system.statistic_faq += 1
                    await time_statistics(from_.id, system)
                case "date_production":
                    system.statistic_date_production += 1
                    await time_statistics(from_.id, system)

            system.commands_processed += 1
            system.commands_processed_all += 1

            system.save()

        except Exception:
            logger.warning(f"Error in executor {self.title} [mark_statistics]\n{traceback.format_exc()}")


async def time_statistics(user_id: int, system: System):

    hour_stats = ctx.get("hour_stats")
    if not hour_stats:
        hour_stats = {}

    date = datetime.datetime.now(tz=tz) + datetime.timedelta(hours=7)
    hour = str(date.hour)

    if len(hour_stats) == 0:
        hour_stats[hour] = []

    if hour in hour_stats:
        if user_id not in hour_stats[hour]:
            hour_stats[hour].append(user_id)
    else:
        all_hours_stats = decode(system.statistic_time)

        for interval in all_hours_stats:
            all_hours_stats[interval][hour] += len(hour_stats[hour])

        system.statistic_time = all_hours_stats

        ctx.set("hour_stats", {})

