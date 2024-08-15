import traceback
import datetime

from telegrinder.rules import CallbackDataEq
from telegrinder import CallbackQuery, Dispatch, InlineKeyboard, InlineButton, Message
from json import JSONDecodeError

from client import api, ctx, client, fmt, tz
from tools import save_mess, delete_mess, decode, digit
from rules import Calculator, CallbackDataEqs, CallbackDataStartsWith
from handlers.executor import ExecutorType, DispatchExecutor
from handlers.calculator.calculator import calculator_cq
from operations import get_user, User

dp = Dispatch()

CANCEL_KEYBOARD = (
    InlineKeyboard()
    .add(InlineButton("Вернуться назад", callback_data="calculator_auto_cancel"))
).get_markup()

FIZ_KEYBOARD = (
    InlineKeyboard()
    .add(InlineButton("Физлицо", callback_data="fiz_face"))
    .add(InlineButton("Юрлицо", callback_data="yr_face")).row()
    .add(InlineButton("Вернуться назад", callback_data="calculator_auto_cancel"))
).get_markup()

CURRENCY_KEYBOARD = (
    InlineKeyboard()
    .add(InlineButton("Евро", callback_data="currency_eur")).row()
    .add(InlineButton("Российский рубль", callback_data="currency_rub")).row()
    .add(InlineButton("Доллар США", callback_data="currency_usd")).row()
    .add(InlineButton("Японская иена", callback_data="currency_jpy")).row()
    .add(InlineButton("Южнокорейская вона", callback_data="currency_krw")).row()
    .add(InlineButton("Вернуться назад", callback_data="calculator_auto_cancel"))
).get_markup()

ENGINE_KEYBOARD = (
    InlineKeyboard()
    .add(InlineButton("Бензин", callback_data="engine_b")).row()
    .add(InlineButton("Дизель", callback_data="engine_d")).row()
    .add(InlineButton("Электро", callback_data="engine_e")).row()
    .add(InlineButton("Бензин + электро", callback_data="engine_be")).row()
    .add(InlineButton("Дизель + электро", callback_data="engine_de")).row()
    .add(InlineButton("Вернуться назад", callback_data="calculator_auto_cancel"))
).get_markup()

HYBRID_KEYBOARD = (
    InlineKeyboard()
    .add(InlineButton("Параллельный гибрид", callback_data="hybrid_1")).row()
    .add(InlineButton("Последовательный гибрид", callback_data="hybrid_0")).row()
).get_markup()

YEAR_ADDITION_KEYBOARD = (
    InlineKeyboard()
    .add(InlineButton("Да", callback_data="year_yes"))
    .add(InlineButton("Нет", callback_data="year_no")).row()
    .add(InlineButton("Вернуться назад", callback_data="calculator_auto_cancel"))
).get_markup()


executor = DispatchExecutor(title="calculator_auto",
                            type_executor=ExecutorType.KEYBOARD
                            )


@dp.callback_query(CallbackDataEq("calculator_auto_cancel"))
async def calculator_auto_cancel(cq: CallbackQuery) -> None:
    try:
        ctx_state_cancel = await Calculator.get(cq.message.unwrap().v.chat.id)
        auto_stages = Calculator.AUTO_STAGES

        state_cancel = ctx_state_cancel
        state = auto_stages[auto_stages.index(state_cancel) - 1]

        await Calculator.set(cq.message.unwrap().v.chat.id, state, Calculator.AUTO)
        match state:
            case Calculator.STRATEGY:
                await calculator_cq.func(cq)
            case Calculator.FIZ:
                await calculator_auto_fiz.func(cq)
            case Calculator.CURRENCY:
                await calculator_auto_currency.func(cq)
            case Calculator.PRICE:
                await calculator_auto_price.func(cq)
            case Calculator.ENGINE:
                cq.message.unwrap().v.message_id = -1
                await calculator_auto_engine.func(cq.message.unwrap().v)
            case Calculator.YEAR:
                await calculator_auto_year.func(cq)
            case Calculator.VOLUME:
                cq.message.unwrap().v.message_id = -1
                await calculator_auto_volume.func(cq.message.unwrap().v)
            case Calculator.POWER:
                cq.message.unwrap().v.message_id = -1
                await calculator_auto_power.func(cq.message.unwrap().v)
    except Exception:
        executor.traceback = traceback.format_exc()
    finally:
        await executor.logger(cq, intermediate=True)


@dp.callback_query(CallbackDataEq("auto") & Calculator.CallbackQuery(Calculator.STRATEGY, Calculator.AUTO))
async def calculator_auto_fiz(cq: CallbackQuery) -> None:
    try:
        message = cq.message.unwrap().v

        calculator = ctx.get(f"calculator_{cq.from_.id}")
        calculator["strategy"] = "auto_japan"
        ctx.set(f"calculator_{cq.from_.id}", calculator)

        await delete_mess(message.chat.id)
        response = await api.send_message(text="🔹Укажите тип лица:",
                                          chat_id=message.chat.id,
                                          reply_markup=FIZ_KEYBOARD)
        await save_mess(response.unwrap())

        await Calculator.set(message.chat.id, Calculator.FIZ, Calculator.AUTO)

    except Exception:
        executor.traceback = traceback.format_exc()
    finally:
        await executor.logger(cq, intermediate=True)


@dp.callback_query(CallbackDataEqs(["fiz_face", "yr_face"]) & Calculator.CallbackQuery(Calculator.FIZ, Calculator.AUTO))
async def calculator_auto_currency(cq: CallbackQuery) -> None:
    try:

        calculator = ctx.get(f"calculator_{cq.from_.id}")
        if cq.data.unwrap() in ["fiz_face", "yr_face"]:
            calculator["fiz"] = 1 if cq.data.unwrap() == "fiz_face" else 0
        ctx.set(f"calculator_{cq.from_.id}", calculator)

        await delete_mess(cq.message.unwrap().v.chat.id)
        response = await api.send_message(text="🔹Выберите валюту:",
                                          chat_id=cq.message.unwrap().v.chat.id,
                                          reply_markup=CURRENCY_KEYBOARD)
        await save_mess(response.unwrap())

        await Calculator.set(cq.message.unwrap().v.chat.id, Calculator.CURRENCY, Calculator.AUTO)

    except Exception:
        executor.traceback = traceback.format_exc()
    finally:
        await executor.logger(cq, intermediate=True)


@dp.callback_query(CallbackDataStartsWith("currency") & Calculator.CallbackQuery(Calculator.CURRENCY, Calculator.AUTO))
async def calculator_auto_price(cq: CallbackQuery) -> None:
    try:
        message = cq.message.unwrap().v

        calculator = ctx.get(f"calculator_{cq.from_.id}")
        if "currency_" in cq.data.unwrap():
            calculator["currency"] = cq.data.unwrap().replace("currency_", "").upper()
        ctx.set(f"calculator_{cq.from_.id}", calculator)

        await delete_mess(message.chat.id)
        response = await api.send_message(text=Calculator.MSG_PRICE,
                                          chat_id=message.chat.id,
                                          reply_markup=CANCEL_KEYBOARD,
                                          parse_mode=fmt.PARSE_MODE)
        await save_mess(response.unwrap())

        await Calculator.set(message.chat.id, Calculator.PRICE, Calculator.AUTO)

    except Exception:
        executor.traceback = traceback.format_exc()
    finally:
        await executor.logger(cq, intermediate=True)


@dp.message(Calculator.Message(Calculator.PRICE, Calculator.AUTO))
async def calculator_auto_engine(message: Message) -> None:
    try:
        # if hasattr(message, "message_id"):
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
        response = await api.send_message(text="🔹Выберите тип двигателя:",
                                          chat_id=message.chat.id,
                                          reply_markup=ENGINE_KEYBOARD)
        await save_mess(response.unwrap())

        await Calculator.set(message.chat.id, Calculator.ENGINE, Calculator.AUTO)

    except Exception:
        executor.traceback = traceback.format_exc()
    finally:
        await executor.logger(message, intermediate=True)


@dp.callback_query(CallbackDataEqs(["engine_be", "engine_de"]) & Calculator.CallbackQuery(Calculator.ENGINE, Calculator.AUTO))
async def calculator_auto_hybrid_type(cq: CallbackQuery) -> None:
    try:
        message = cq.message.unwrap().v

        calculator = ctx.get(f"calculator_{cq.from_.id}")
        if "engine_" in cq.data.unwrap():
            calculator["engine"] = cq.data.unwrap().replace("engine_", "")
        ctx.set(f"calculator_{cq.from_.id}", calculator)

        await delete_mess(message.chat.id)
        response = await api.send_message(text="🔹Выберите вид гибридного авто:",
                                          chat_id=cq.message.unwrap().v.chat.id,
                                          reply_markup=HYBRID_KEYBOARD,
                                          parse_mode=fmt.PARSE_MODE)
        await save_mess(response.unwrap())

        await Calculator.set(message.chat.id, Calculator.HYBRID, Calculator.AUTO)

    except Exception:
        executor.traceback = traceback.format_exc()
    finally:
        await executor.logger(cq, intermediate=True)


@dp.callback_query((CallbackDataStartsWith("engine") & Calculator.CallbackQuery(Calculator.ENGINE, Calculator.AUTO))
                   |
                   (CallbackDataStartsWith("hybrid") & Calculator.CallbackQuery(Calculator.HYBRID, Calculator.AUTO))
                   )
async def calculator_auto_year(cq: CallbackQuery) -> None:
    try:
        message = cq.message.unwrap().v

        calculator = ctx.get(f"calculator_{cq.from_.id}")

        if "engine_" in cq.data.unwrap():
            calculator["engine"] = cq.data.unwrap().replace("engine_", "")

        if "hybrid_" in cq.data.unwrap():
            calculator["hybrid"] = int(cq.data.unwrap().replace("hybrid_", ""))

        if "hybrid" not in calculator:
            calculator["hybrid"] = 2

        ctx.set(f"calculator_{cq.from_.id}", calculator)

        await delete_mess(message.chat.id)
        response = await api.send_message(text=Calculator.MSG_YEAR,
                                          chat_id=cq.message.unwrap().v.chat.id,
                                          reply_markup=CANCEL_KEYBOARD,
                                          parse_mode=fmt.PARSE_MODE)
        await save_mess(response.unwrap())

        await Calculator.set(message.chat.id, Calculator.YEAR, Calculator.AUTO)

    except Exception:
        executor.traceback = traceback.format_exc()
    finally:
        await executor.logger(cq, intermediate=True)


@dp.message(Calculator.Message(Calculator.YEAR, Calculator.AUTO))
async def calculator_auto_volume(message: Message) -> None:
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

            # проходные года

            date = datetime.datetime.now(tz=tz) + datetime.timedelta(hours=7)
            min_year = date.year - 5
            max_year = date.year - 3
            if int(message.text.unwrap()) == min_year:

                await delete_mess(message.chat.id)
                response = await api.send_message(text="🔹Укажите, автомобиль младше 5 лет?",
                                                  chat_id=message.chat.id,
                                                  reply_markup=YEAR_ADDITION_KEYBOARD)
                await save_mess(response.unwrap())
                await Calculator.set(message.chat.id, Calculator.YEAR_ADDITION, Calculator.AUTO)
                return

            elif int(message.text.unwrap()) == max_year:

                await delete_mess(message.chat.id)
                response = await api.send_message(text="🔹Укажите, автомобиль старше 3 лет?",
                                                  chat_id=message.chat.id,
                                                  reply_markup=YEAR_ADDITION_KEYBOARD)
                await save_mess(response.unwrap())
                await Calculator.set(message.chat.id, Calculator.YEAR_ADDITION, Calculator.AUTO)
                return

        calculator = ctx.get(f"calculator_{message.from_.unwrap().id}")
        calculator["ymin"] = 0
        ctx.set(f"calculator_{message.from_.unwrap().id}", calculator)

        await delete_mess(message.chat.id)
        response = await api.send_message(text=Calculator.MSG_VOLUME,
                                          chat_id=message.chat.id,
                                          reply_markup=CANCEL_KEYBOARD,
                                          parse_mode=fmt.PARSE_MODE)
        await save_mess(response.unwrap())

        await Calculator.set(message.chat.id, Calculator.VOLUME, Calculator.AUTO)

    except Exception:
        executor.traceback = traceback.format_exc()
    finally:
        await executor.logger(message, intermediate=True)


@dp.callback_query(Calculator.CallbackQuery(Calculator.YEAR_ADDITION, Calculator.AUTO))
async def calculator_auto_year_additional(cq: CallbackQuery) -> None:
    try:
        cq_data = cq.data.unwrap()
        calculator = ctx.get(f"calculator_{cq.from_.id}")
        calculator["ymin"] = 1 if "yes" in cq_data else 0
        ctx.set(f"calculator_{cq.from_.id}", calculator)

        await delete_mess(cq.message.unwrap().v.chat.id)
        response = await api.send_message(text=Calculator.MSG_VOLUME,
                                          chat_id=cq.message.unwrap().v.chat.id,
                                          reply_markup=CANCEL_KEYBOARD,
                                          parse_mode=fmt.PARSE_MODE)
        await save_mess(response.unwrap())

        await Calculator.set(cq.message.unwrap().v.chat.id, Calculator.VOLUME, Calculator.AUTO)

    except Exception:
        executor.traceback = traceback.format_exc()
    finally:
        await executor.logger(cq, intermediate=True)


@dp.message(Calculator.Message(Calculator.VOLUME, Calculator.AUTO))
async def calculator_auto_power(message: Message) -> None:
    try:
        calculator = ctx.get(f"calculator_{message.from_.unwrap().id}")

        if message.message_id > 0:
            if not message.text.unwrap().isdigit():
                await delete_mess(message.chat.id)
                response = await api.send_message(text=Calculator.MSG_VOLUME,
                                                  chat_id=message.chat.id,
                                                  reply_markup=CANCEL_KEYBOARD,
                                                  parse_mode=fmt.PARSE_MODE)
                await save_mess(response.unwrap())
                return

            calculator["volume"] = int(message.text.unwrap())
            ctx.set(f"calculator_{message.from_.unwrap().id}", calculator)

        await delete_mess(message.chat.id)
        if calculator["engine"] in ["e", "de", "be"]:
            response = await api.send_message(text=Calculator.MSG_POWER_SUM,
                                              chat_id=message.chat.id,
                                              parse_mode=fmt.PARSE_MODE)
            await Calculator.set(message.chat.id, Calculator.POWER_SUM, Calculator.AUTO)
        else:
            response = await api.send_message(text=Calculator.MSG_POWER,
                                              chat_id=message.chat.id,
                                              reply_markup=CANCEL_KEYBOARD,
                                              parse_mode=fmt.PARSE_MODE)
            await Calculator.set(message.chat.id, Calculator.POWER, Calculator.AUTO)

        await save_mess(response.unwrap())

    except Exception:
        executor.traceback = traceback.format_exc()
    finally:
        await executor.logger(message, intermediate=True)


@dp.message(Calculator.Message(Calculator.POWER_SUM, Calculator.AUTO))
async def calculator_auto_power_sum(message: Message) -> None:
    try:
        calculator = ctx.get(f"calculator_{message.from_.unwrap().id}")

        if not message.text.unwrap().isdigit():
            await delete_mess(message.chat.id)
            response = await api.send_message(text=Calculator.MSG_POWER_SUM,
                                              chat_id=message.chat.id,
                                              parse_mode=fmt.PARSE_MODE)
            await save_mess(response.unwrap())
            return

        calculator["power_sum"] = int(message.text.unwrap())
        ctx.set(f"calculator_{message.from_.unwrap().id}", calculator)

        if calculator["hybrid"]:
            await delete_mess(message.chat.id)
            response = await api.send_message(text=Calculator.MSG_POWER,
                                              chat_id=message.chat.id,
                                              reply_markup=CANCEL_KEYBOARD,
                                              parse_mode=fmt.PARSE_MODE)
            await save_mess(response.unwrap())
            await Calculator.set(message.chat.id, Calculator.POWER, Calculator.AUTO)
        else:
            await calculator_auto_finish.func(message)

    except Exception:
        executor.traceback = traceback.format_exc()
    finally:
        await executor.logger(message, intermediate=True)


@dp.message(Calculator.Message(Calculator.POWER, Calculator.AUTO))
async def calculator_auto_finish(message: Message) -> None:
    try:
        calculator = ctx.get(f"calculator_{message.from_.unwrap().id}")

        if not message.text.unwrap().isdigit() and message.text.unwrap() != "" and (calculator['hybrid'] or calculator['hybrid'] == 2):
            await delete_mess(message.chat.id)
            response = await api.send_message(text=Calculator.MSG_POWER,
                                              chat_id=message.chat.id,
                                              reply_markup=CANCEL_KEYBOARD,
                                              parse_mode=fmt.PARSE_MODE)
            await save_mess(response.unwrap())
            return

        calculator["power"] = int(message.text.unwrap())
        ctx.set(f"calculator_{message.from_.unwrap().id}", calculator)

        dev = get_user(User.username, "vencyderry")

        response_api = await client.request_text(f"https://vlb-broker.ru/bitrix/templates/main/classes/calculator/actions/api.php?"
                                                 f"strategy={calculator['strategy']}&"
                                                 f"fiz={calculator['fiz']}&"
                                                 f"price={calculator['price']}&"
                                                 f"currency={calculator['currency']}&"
                                                 f"m={calculator['engine']}&"
                                                 f"year={calculator['year']}&"
                                                 f"v={1 if calculator['volume'] == 0 else calculator['volume']}&"
                                                 f"p={calculator['power'] if calculator['hybrid'] or calculator['hybrid'] == 2 else calculator['power_sum']}&"
                                                 f"ymin={calculator['ymin']}&"
                                                 f"emin={calculator['hybrid']}&"
                                                 )

        await delete_mess(message.chat.id)
        if response_api:
            try:
                response_api = decode(response_api)
                response = await api.send_message(text=f"Расчёт таможенных платежей:\n"
                                                       f"🔹Сборы за таможенное оформление: {digit(response_api['fees'])} ₽\n"
                                                       f"🔹Пошлина: {digit(response_api['duty'])} ₽\n"
                                                       f"🔹НДС: {digit(response_api['nds'])} ₽\n"
                                                       f"🔹Итог: {digit(response_api['custom'])} ₽\n\n"
                                                       f"🔹Утилизационный сбор: {digit(response_api['util'])} ₽\n"
                                                       f"🔹Итог с утильсбором: {digit(round(response_api['custom'] + response_api['util']))} ₽\n\n"
                                                       f"📌 Расчёты являются предварительными и необходимы для того, чтобы "
                                                       f"сориентировать Вас. За более достоверным расчётом оставьте заявку или обратитесь к нашему менеджеру.\n\n"
                                                       f"Наши специалисты проконсультируют Вас!",
                                                  chat_id=message.chat.id)
            except KeyError:
                response = await api.send_message(
                    text=f"❌ При расчете таможенных платежей произошла ошибка, попробуйте снова.",
                    chat_id=message.chat.id)
                await api.send_message(text=f"При расчете данных в калькуляторе, произошла ошибка.\n\n"
                                            f"{calculator}\n\n{response_api}\n\n",
                                       chat_id=dev.tgid)
            except JSONDecodeError:
                response = await api.send_message(
                    text=f"❌ При расчете таможенных платежей произошла ошибка, попробуйте снова.",
                    chat_id=message.chat.id)
                await api.send_message(text=f"При расчете данных в калькуляторе, произошла ошибка.\n\n"
                                            f"{calculator}\n\n{response_api}\n\n",
                                       chat_id=dev.tgid)
        else:
            response = await api.send_message(
                text="❌ При расчете таможенных платежей произошла ошибка, попробуйте снова.",
                chat_id=message.chat.id)
            await api.send_message(text=f"При расчете данных в калькуляторе, произошла ошибка.\n\n"
                                        f"{calculator}\n\n{response_api}\n\n",
                                   chat_id=dev.tgid)
        await save_mess(response.unwrap())

        await Calculator.delete(message.chat.id)

    except Exception:
        executor.traceback = traceback.format_exc()
    finally:
        await executor.logger(message)
