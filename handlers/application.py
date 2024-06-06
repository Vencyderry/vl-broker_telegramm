import traceback

from telegrinder.rules import CallbackDataEq, IsPrivate, FuncRule
from telegrinder import CallbackQuery, Dispatch, Message
from telegrinder.types import Nothing
from telegrinder import InlineKeyboard, InlineButton

from client import api, ctx
from tools import save_mess, delete_mess, decode
from handlers.executor import ExecutorType, DispatchExecutor
from rules import Application
from operations import get_system
from config import *

dp = Dispatch()

CANCEL_KEYBOARD = (
    InlineKeyboard()
    .add(InlineButton("Вернуться назад", callback_data="application_cancel"))
).get_markup()

executor_application = DispatchExecutor(title="application",
                                        type_executor=ExecutorType.COMMAND
                                        )


@dp.callback_query(CallbackDataEq("application_cancel"))
async def application_cancel(cq: CallbackQuery) -> None:
    try:
        ctx_state_cancel = await Application.get(cq.message.unwrap().v.chat.id)
        stages = Application.STAGES

        state_cancel = ctx_state_cancel
        state = stages[stages.index(state_cancel) - 1]

        await Application.set(cq.message.unwrap().v.chat.id, state)
        match state:
            case Application.NAME:
                cq.message.unwrap().v.message_id = -1
                await start_application_cq.func(cq)
            case Application.COUNTRY:
                cq.message.unwrap().v.message_id = -1
                await part_name.func(cq.message.unwrap().v)
            case Application.CARGO:
                cq.message.unwrap().v.message_id = -1
                await part_country.func(cq.message.unwrap().v)

    except Exception:
        executor_application.traceback = traceback.format_exc()
    finally:
        await executor_application.logger(cq, intermediate=True)


@dp.callback_query(CallbackDataEq("app"))
async def start_application_cq(cq: CallbackQuery) -> None:
    try:

        if cq.message.unwrap().v.message_id > 0:
            ctx.set(f"application_{cq.from_.id}", {})

        message = cq.message.unwrap().v

        await delete_mess(message.chat.id)
        response1 = await api.send_message(text="🔹Бот VL-BROKER поможет Вам заполнить заявку и автоматически отправит её нашим специалистам!"
                                           "\n\n📌Данная заявка является предварительной и ни к чему Вас не обязывает. ",
                                           chat_id=message.chat.id)
        response2 = await api.send_message(text=f"1. Как Вас зовут?",
                                           chat_id=message.chat.id)

        await save_mess(response1.unwrap())
        await save_mess(response2.unwrap())

        await Application.set(message.chat.id, Application.NAME)

    except Exception:
        executor_application.traceback = traceback.format_exc()
    finally:
        await executor_application.logger(cq, intermediate=True)


@dp.message(Application(Application.NAME))
async def part_name(message: Message) -> None:
    try:
        await save_mess(message)
        await delete_mess(message.chat.id)

        from_ = message.from_.unwrap()

        if message.message_id > 0:
            application = ctx.get(f"application_{from_.id}")
            application["name"] = message.text.unwrap()
            ctx.set(f"application_{from_.id}", application)

        await delete_mess(message.chat.id)
        response = await api.send_message(text=f"2. Из какого Вы города?",
                                          reply_markup=CANCEL_KEYBOARD,
                                          chat_id=message.chat.id)
        await save_mess(response.unwrap())

        await Application.set(message.chat.id, Application.COUNTRY)

    except Exception:
        executor_application.traceback = traceback.format_exc()
    finally:
        await executor_application.logger(message, intermediate=True)


@dp.message(Application(Application.COUNTRY))
async def part_country(message: Message) -> None:
    try:
        await save_mess(message)
        await delete_mess(message.chat.id)

        from_ = message.from_.unwrap()

        if message.message_id > 0:
            application = ctx.get(f"application_{from_.id}")
            application["country"] = message.text.unwrap()
            ctx.set(f"application_{from_.id}", application)

        await delete_mess(message.chat.id)
        response = await api.send_message(text=f"3. Тезисно опишите груз:",
                                          reply_markup=CANCEL_KEYBOARD,
                                          chat_id=message.chat.id)
        await save_mess(response.unwrap())

        await Application.set(from_.id, Application.CARGO)

    except Exception:
        executor_application.traceback = traceback.format_exc()
    finally:
        await executor_application.logger(message, intermediate=True)


@dp.message(Application(Application.CARGO))
async def part_cargo(message: Message) -> None:
    try:

        await save_mess(message)
        await delete_mess(message.chat.id)

        from_ = message.from_.unwrap()

        application = ctx.get(f"application_{from_.id}")
        application["cargo"] = message.text.unwrap()
        ctx.set(f"application_{from_.id}", application)

        await delete_mess(message.chat.id)
        response = await api.send_message(text=f"4. Укажите Ваш номер телефона:",
                                          reply_markup=CANCEL_KEYBOARD,
                                          chat_id=message.chat.id)
        await save_mess(response.unwrap())

        await Application.set(from_.id, Application.NUMBER)

    except Exception:
        executor_application.traceback = traceback.format_exc()
    finally:
        await executor_application.logger(message, intermediate=True)


@dp.message(Application(Application.NUMBER))
async def part_number(message: Message) -> None:
    try:

        await save_mess(message)
        await delete_mess(message.chat.id)

        from_ = message.from_.unwrap()

        application = ctx.get(f"application_{from_.id}")
        application["number"] = message.text.unwrap()
        ctx.delete(f"application_{from_.id}")

        await delete_mess(message.chat.id)
        response = await message.answer("Наш специалист обязательно свяжется с Вами!"
                                        "\nРаботаем по владивостокскому времени (МСК+7)."
                                        "\n\nБлагодарим, что выбрали VL-BROKER!"
                                        "\n\n📌Уважаемый партнёр, чтобы оставить ещё одну заявку нажмите «Оставить заявку».")
        await save_mess(response.unwrap())

        accept_keyboard = (
            InlineKeyboard()
            .add(InlineButton("Принять заявку", callback_data="app_accept")).row()
        ).get_markup()

        if from_.username == Nothing:
            username = from_.full_name
        else:
            username = "@" + from_.username.unwrap()

        await api.send_message(text=f"❗️ Новая заявка от {from_.first_name}!"
                                    f"\n▶ Имя: {application['name']}"
                                    f"\n▶ Город: {application['country']}"
                                    f"\n▶ Описание груза: {application['cargo']}"
                                    f"\n▶ Номер телефона: {application['number']}"
                                    f"\n\n✈️ Telegram:"
                                    f"\n▶ Name: {from_.first_name}"
                                    f"\n▶ Username: {username}",
                               chat_id=ADMIN_CHAT,
                               reply_markup=accept_keyboard
                               )

        await Application.delete(from_.id)

    except Exception:
        executor_application.traceback = traceback.format_exc()
    finally:
        await executor_application.logger(message)


executor_application_accept = DispatchExecutor(title="application_accept",
                                               type_executor=ExecutorType.COMMAND
                                               )


@dp.callback_query(CallbackDataEq("app_accept"))
async def edit_application_cq(cq: CallbackQuery) -> None:
    try:

        if cq.from_.username == Nothing:
            username = cq.from_.full_name
        else:
            username = "@" + cq.from_.username.unwrap()

        message = cq.message.unwrap().v
        text_application = message.text.unwrap()
        await api.edit_message_text(text=text_application.replace("Новая з", "З").replace("❗️", "✔️") + f"\n\n✅ Заявка принята в работу менеджером {username}",
                                    message_id=message.message_id,
                                    chat_id=ADMIN_CHAT)

    except KeyError:
        await cq.answer("❌ Заявка не найдена.")
    except Exception:
        executor_application_accept.traceback = traceback.format_exc()
    finally:
        await executor_application_accept.logger(cq)
