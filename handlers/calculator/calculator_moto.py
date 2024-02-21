import traceback

import telegrinder
from telegrinder.rules import CallbackDataEq
from telegrinder import CallbackQuery, Dispatch, InlineKeyboard, InlineButton, Message
from telegrinder.tools import italic, escape, HTMLFormatter
from json import JSONDecodeError

from client import api, ctx, client, fmt
from tools import save_mess, delete_mess, decode, digit
from rules import Calculator, CallbackDataEqs, CallbackDataStartsWith
from handlers.executor import ExecutorType, DispatchExecutor
from handlers.calculator.calculator import calculator_cq
from operations import get_user, User

dp = Dispatch()

CANCEL_KEYBOARD = (
    InlineKeyboard()
    .add(InlineButton("Вернуться назад", callback_data="calculator_moto_cancel"))
).get_markup()

FIZ_KEYBOARD = (
    InlineKeyboard()
    .add(InlineButton("Физлицо", callback_data="fiz_face"))
    .add(InlineButton("Юрлицо", callback_data="yr_face")).row()
    .add(InlineButton("Вернуться назад", callback_data="calculator_moto_cancel"))
).get_markup()

CURRENCY_KEYBOARD = (
    InlineKeyboard()
    .add(InlineButton("Евро", callback_data="currency_eur")).row()
    .add(InlineButton("Российский рубль", callback_data="currency_rub")).row()
    .add(InlineButton("Доллар США", callback_data="currency_usd")).row()
    .add(InlineButton("Японская иена", callback_data="currency_jpy")).row()
    .add(InlineButton("Южнокорейская вона", callback_data="currency_krw")).row()
    .add(InlineButton("Вернуться назад", callback_data="calculator_moto_cancel"))
).get_markup()

executor = DispatchExecutor(title="calculator_moto",
                            type_executor=ExecutorType.KEYBOARD
                            )


@dp.callback_query(CallbackDataEq("calculator_moto_cancel"))
async def calculator_moto_cancel(cq: CallbackQuery) -> None:
    try:
        ctx_state_cancel = await Calculator.get(cq.message.unwrap().v.chat.id)
        moto_stages = Calculator.MOTO_STAGES

        state_cancel = ctx_state_cancel
        state = moto_stages[moto_stages.index(state_cancel) - 1]

        await Calculator.set(cq.message.unwrap().v.chat.id, state, Calculator.MOTO)
        match state:
            case Calculator.STRATEGY:
                await calculator_cq.func(cq)
            case Calculator.FIZ:
                await calculator_moto_fiz.func(cq)
            case Calculator.CURRENCY:
                await calculator_moto_currency.func(cq)
            case Calculator.PRICE:
                await calculator_moto_price.func(cq)
            case Calculator.YEAR:
                cq.message.unwrap().v.message_id = -1
                await calculator_moto_year.func(cq.message.unwrap())
            case Calculator.VOLUME:
                cq.message.unwrap().v.message_id = -1
                await calculator_moto_volume.func(cq.message.unwrap())
            case Calculator.POWER:
                cq.message.unwrap().v.message_id = -1
                await calculator_moto_power.func(cq.message.unwrap())


    except Exception:
        executor.traceback = traceback.format_exc()
    finally:
        await executor.logger(cq, intermediate=True)


@dp.callback_query(CallbackDataEq("moto") & Calculator.CallbackQuery(Calculator.STRATEGY, Calculator.MOTO))
async def calculator_moto_fiz(cq: CallbackQuery) -> None:
    try:
        message = cq.message.unwrap().v

        calculator = ctx.get(f"calculator_{cq.from_.id}")
        calculator["strategy"] = cq.data.unwrap() + "_japan"
        ctx.set(f"calculator_{cq.from_.id}", calculator)

        await delete_mess(message.chat.id)
        response = await api.send_message(text="🔹Укажите тип лица:",
                                          chat_id=message.chat.id,
                                          reply_markup=FIZ_KEYBOARD)
        await save_mess(response.unwrap())

        await Calculator.set(message.chat.id, Calculator.FIZ, Calculator.MOTO)

    except Exception:
        executor.traceback = traceback.format_exc()
    finally:
        await executor.logger(cq, intermediate=True)


@dp.callback_query(CallbackDataEqs(["fiz_face", "yr_face"]) & Calculator.CallbackQuery(Calculator.FIZ, Calculator.MOTO))
async def calculator_moto_currency(cq: CallbackQuery) -> None:
    try:

        calculator = ctx.get(f"calculator_{cq.from_.id}")
        calculator["fiz"] = 1 if cq.data.unwrap() == "fiz_face" else 0
        ctx.set(f"calculator_{cq.from_.id}", calculator)

        await delete_mess(cq.message.unwrap().v.chat.id)
        response = await api.send_message(text="🔹Выберите валюту:",
                                          chat_id=cq.message.unwrap().v.chat.id,
                                          reply_markup=CURRENCY_KEYBOARD)
        await save_mess(response.unwrap())

        await Calculator.set(cq.message.unwrap().v.chat.id, Calculator.CURRENCY, Calculator.MOTO)

    except Exception:
        executor.traceback = traceback.format_exc()
    finally:
        await executor.logger(cq, intermediate=True)


@dp.callback_query(CallbackDataStartsWith("currency") & Calculator.CallbackQuery(Calculator.CURRENCY, Calculator.MOTO))
async def calculator_moto_price(cq: CallbackQuery) -> None:
    try:
        message = cq.message.unwrap().v

        calculator = ctx.get(f"calculator_{cq.from_.id}")
        calculator["currency"] = cq.data.unwrap().replace("currency_", "").upper()
        ctx.set(f"calculator_{cq.from_.id}", calculator)

        await delete_mess(message.chat.id)
        response = await api.send_message(text=Calculator.MSG_PRICE,
                                          chat_id=message.chat.id,
                                          reply_markup=CANCEL_KEYBOARD,
                                          parse_mode=fmt.PARSE_MODE)
        await save_mess(response.unwrap())

        await Calculator.set(message.chat.id, Calculator.PRICE, Calculator.MOTO)

    except Exception:
        executor.traceback = traceback.format_exc()
    finally:
        await executor.logger(cq, intermediate=True)


@dp.message(Calculator.Message(Calculator.PRICE, Calculator.MOTO))
async def calculator_moto_year(message: Message) -> None:
    try:
        if message.message_id > 0:
            if not message.text.unwrap().isdigit():

                await delete_mess(message.chat.id)
                response = await api.send_message(text=Calculator.MSG_PRICE,
                                                  chat_id=message.chat.id,
                                                  reply_markup=CANCEL_KEYBOARD,
                                                  parse_mode=fmt.PARSE_MODE)
                await save_mess(response.unwrap())
                return

            calculator = ctx.get(f"calculator_{message.from_.unwrap().id}")
            calculator["price"] = int(message.text.unwrap())
            ctx.set(f"calculator_{message.from_.unwrap().id}", calculator)

        await delete_mess(message.chat.id)
        response = await api.send_message(text=Calculator.MSG_YEAR,
                                          chat_id=message.chat.id,
                                          reply_markup=CANCEL_KEYBOARD,
                                          parse_mode=fmt.PARSE_MODE)
        await save_mess(response.unwrap())

        await Calculator.set(message.chat.id, Calculator.YEAR, Calculator.MOTO)

    except Exception:
        executor.traceback = traceback.format_exc()
    finally:
        await executor.logger(message, intermediate=True)


@dp.message(Calculator.Message(Calculator.YEAR, Calculator.MOTO))
async def calculator_moto_volume(message: Message) -> None:
    try:
        if message.message_id > 0:
            if not message.text.unwrap().isdigit():

                await delete_mess(message.chat.id)
                response = await api.send_message(text=Calculator.MSG_YEAR,
                                                  chat_id=message.chat.id,
                                                  reply_markup=CANCEL_KEYBOARD,
                                                  parse_mode=fmt.PARSE_MODE)
                await save_mess(response.unwrap())
                return

            calculator = ctx.get(f"calculator_{message.from_.unwrap().id}")
            calculator["year"] = int(message.text.unwrap())
            ctx.set(f"calculator_{message.from_.unwrap().id}", calculator)

        await delete_mess(message.chat.id)
        response = await api.send_message(text=Calculator.MSG_VOLUME,
                                          chat_id=message.chat.id,
                                          reply_markup=CANCEL_KEYBOARD,
                                          parse_mode=fmt.PARSE_MODE)
        await save_mess(response.unwrap())

        await Calculator.set(message.chat.id, Calculator.VOLUME, Calculator.MOTO)

    except Exception:
        executor.traceback = traceback.format_exc()
    finally:
        await executor.logger(message, intermediate=True)


@dp.message(Calculator.Message(Calculator.VOLUME, Calculator.MOTO))
async def calculator_moto_power(message: Message) -> None:
    try:
        if message.message_id > 0:
            if not message.text.unwrap().isdigit():
                await delete_mess(message.chat.id)
                response = await api.send_message(text=Calculator.MSG_VOLUME,
                                                  chat_id=message.chat.id,
                                                  reply_markup=CANCEL_KEYBOARD,
                                                  parse_mode=fmt.PARSE_MODE)
                await save_mess(response.unwrap())
                return

            calculator = ctx.get(f"calculator_{message.from_.unwrap().id}")
            calculator["volume"] = int(message.text.unwrap())
            ctx.set(f"calculator_{message.from_.unwrap().id}", calculator)

        await delete_mess(message.chat.id)
        response = await api.send_message(text=Calculator.MSG_POWER,
                                          chat_id=message.chat.id,
                                          reply_markup=CANCEL_KEYBOARD,
                                          parse_mode=fmt.PARSE_MODE)
        await save_mess(response.unwrap())

        await Calculator.set(message.chat.id, Calculator.POWER, Calculator.MOTO)

    except Exception:
        executor.traceback = traceback.format_exc()
    finally:
        await executor.logger(message, intermediate=True)


@dp.message(Calculator.Message(Calculator.POWER, Calculator.MOTO))
async def calculator_moto_finish(message: Message) -> None:
    try:
        if not message.text.unwrap().isdigit():

            await delete_mess(message.chat.id)
            response = await api.send_message(text=Calculator.MSG_POWER,
                                              chat_id=message.chat.id,
                                              reply_markup=CANCEL_KEYBOARD,
                                              parse_mode=fmt.PARSE_MODE)
            await save_mess(response.unwrap())
            return

        calculator = ctx.get(f"calculator_{message.from_.unwrap().id}")
        calculator["power"] = int(message.text.unwrap())
        ctx.set(f"calculator_{message.from_.unwrap().id}", calculator)

        dev = get_user(User.username, "vencyderry")

        response_api = await client.request_text(f"https://vlb-broker.ru/bitrix/templates/main/classes/calculator/actions/api.php?"
                                                 f"strategy={calculator['strategy']}&"
                                                 f"fiz={calculator['fiz']}&"
                                                 f"price={calculator['price']}&"
                                                 f"currency={calculator['currency']}&"
                                                 f"year={calculator['year']}&"
                                                 f"v={calculator['volume']}&"
                                                 f"p={calculator['power']}&"
                                                 )

        await delete_mess(message.chat.id)
        if response_api:
            try:
                response_api = decode(response_api)
                response = await api.send_message(text=f"Расчёт таможенных платежей:\n\n"
                                                       f"🔹Сборы за таможенное оформление: {digit(response_api['fees'])} ₽\n"
                                                       f"🔹Пошлина: {digit(response_api['duty'])} ₽\n"
                                                       f"🔹НДС: {digit(response_api['nds'])} ₽\n"
                                                       f"🔹Итог: {digit(response_api['custom'])} ₽\n\n"f"📌 Расчёты являются предварительными и необходимы для того, чтобы "
                                                       f"сориентировать Вас. За более достоверным расчётом оставьте заявку или обратитесь к нашему менеджеру.\n\n"
                                                       f"Наши специалисты проконсультируют Вас!",
                                                  chat_id=message.chat.id)
            except JSONDecodeError:

                response = await api.send_message(text="❌ При расчете таможенных платежей произошла ошибка, попробуйте снова.",
                                                  chat_id=message.chat.id)

                await api.send_message(text=f"При расчете данных в калькуляторе, произошла ошибка.\n\n"
                                            f"{calculator}\n\n{response_api}",
                                       chat_id=dev.tgid)
        else:
            response = await api.send_message(
                text=f"❌ При расчете таможенных платежей произошла ошибка, попробуйте снова.",
                chat_id=message.chat.id)
            await api.send_message(text=f"При расчете данных в калькуляторе, произошла ошибка.\n\n"
                                        f"{calculator}\n\n{response_api}",
                                   chat_id=dev.tgid)

        await save_mess(response.unwrap())

        await Calculator.delete(message.chat.id)

    except Exception:
        executor.traceback = traceback.format_exc()
    finally:
        await executor.logger(message)

