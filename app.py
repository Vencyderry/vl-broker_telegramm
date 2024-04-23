import traceback

from client import bot, client, ctx
from handlers import handlers
from tools import decode
from loop_wrapper import rules_notification, application_notification, calculator_notification
from operations import *
from models import *
from middlewares import (RegistrationMiddleware,
                         MessageDeleteMiddleware,
                         MessageRouterMiddleware,
                         JoinChatMiddleware,
                         SwearFilterMiddleware
                         )

from telegrinder.modules import logger

logger.info("Bot in processed")

# Запуск базы данных
if __name__ == "__main__":
    try:
        db.connect()
        System.create_table()
        User.create_table()
    except InternalError as px:
        print(str(px))


for dp in handlers:
    bot.dispatch.message.handlers.extend(dp.message.handlers)
    bot.dispatch.default_handlers.extend(dp.default_handlers)
    bot.dispatch.callback_query.handlers.extend(dp.callback_query.handlers)
    # logger.info(f"<{dp.__}> dispatchers was loaded")


@bot.loop_wrapper.interval(seconds=1)
async def start_bot() -> None:
    bot_status = ctx.get("bot")
    if not bot_status:

        system = get_system()
        system.messages_processed = 0
        system.commands_processed = 0
        system.save()

        ctx.set("bot", 1)
        logger.info("Bot started")


@bot.loop_wrapper.interval(minutes=20)
async def currency_handler() -> None:
    response = await client.request_text("https://www.cbr-xml-daily.ru/latest.js", "get")
    response_json = decode(response)
    ctx.set("currency", response_json)


@bot.loop_wrapper.interval(seconds=60)
async def rules_notification_handler() -> None:
    await rules_notification.chat_rules_loop()


@bot.loop_wrapper.interval(seconds=60)
async def calculator_notification_handler() -> None:
    await calculator_notification.calculator_loop()


@bot.loop_wrapper.interval(seconds=60)
async def application_notification_handler() -> None:
    await application_notification.application_loop()

bot.on.message.middlewares.append(MessageRouterMiddleware())
bot.on.message.middlewares.append(RegistrationMiddleware())
bot.on.message.middlewares.append(MessageDeleteMiddleware())
bot.on.message.middlewares.append(JoinChatMiddleware())
# bot.on.message.middlewares.append(SwearFilterMiddleware())

bot.run_forever()
