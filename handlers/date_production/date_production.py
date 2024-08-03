import traceback
import re

from telegrinder.tools import bold, escape, HTMLFormatter, link
from telegrinder.rules import CallbackDataEq, Command
from telegrinder import CallbackQuery, Dispatch, InlineKeyboard, InlineButton, Message

from client import api, client, ctx, fmt
from tools import save_mess, delete_mess
from handlers.executor import ExecutorType, DispatchExecutor
from rules import DateProduction, CallbackDataStartsWith

dp = Dispatch()

KEYBOARD_BRAND = (
    InlineKeyboard()
    .add(InlineButton("Toyota", callback_data="date_production_brand_4")).row()
    .add(InlineButton("Nissan", callback_data="date_production_brand_1")).row()
    .add(InlineButton("Mazda", callback_data="date_production_brand_8")).row()
    .add(InlineButton("Mitsubishi", callback_data="date_production_brand_2")).row()
    .add(InlineButton("Honda", callback_data="date_production_brand_9")).row()
    .add(InlineButton("Suzuki", callback_data="date_production_brand_5")).row()
    .add(InlineButton("Subaru", callback_data="date_production_brand_6")).row()
    .add(InlineButton("Isuzu", callback_data="date_production_brand_3")).row()
    .add(InlineButton("Daihatsu", callback_data="date_production_brand_7")).row()
).get_markup()


executor = DispatchExecutor(title="date_production",
                            type_executor=ExecutorType.KEYBOARD
                            )


@dp.callback_query(CallbackDataEq("date_production") | CallbackDataEq("date_production_cancel"))
async def date_production_menu(cq: CallbackQuery) -> None:

    try:
        message = cq.message.unwrap().v

        await delete_mess(message.chat.id)
        response = await api.send_message(text="Выберите марку автомобиля:",
                                          chat_id=message.chat.id,
                                          reply_markup=KEYBOARD_BRAND)
        await save_mess(response.unwrap())

        await DateProduction.set(cq.message.unwrap().v.chat.id, DateProduction.BRAND)

    except Exception:
        executor.traceback = traceback.format_exc()
    finally:
        await executor.logger(cq)


@dp.callback_query(CallbackDataStartsWith("date_production_brand") & DateProduction.CallbackQuery(DateProduction.BRAND))
async def date_production_brand(cq: CallbackQuery) -> None:
    try:
        message = cq.message.unwrap().v

        date_production = {'brand': cq.data.unwrap()}
        ctx.set(f"date_production_{cq.from_.id}", date_production)

        await delete_mess(message.chat.id)
        response = await api.send_message(text="Введите серию и номер кузова в формате \"GK3-3322969\"",
                                          chat_id=cq.message.unwrap().v.chat.id)
        await save_mess(response.unwrap())

        await DateProduction.set(cq.message.unwrap().v.chat.id, DateProduction.VIN_NUMBER)

    except Exception:
        executor.traceback = traceback.format_exc()
    finally:
        await executor.logger(cq, intermediate=True)

KEYBOARD_CANCEL = (
    InlineKeyboard()
    .add(InlineButton("Вернуться назад", callback_data="date_production_cancel")).row()
).get_markup()


def message_unfound(brand: str = None) -> str:
    mess = "🔹Дата выпуска автомобиля FORMAT отсутствует в каталоге."

    if brand:
        mess = mess.replace("FORMAT", brand)
    else:
        mess = mess.replace("FORMAT ", "")

    return f"{HTMLFormatter(escape(mess))}"


def message_found(brand: str, date: str) -> str:

    dd_mm_yyyy = bool(re.match(r'^\d{2}\.\d{2}\.\d{4}$', date))
    mm_yyyy = bool(re.match(r'^\d{2}\.\d{4}$', date))
    yyyy = bool(re.match(r'^\d{4}$', date))

    mess = "DEFAULT"

    if dd_mm_yyyy:
        mess = f"""
{HTMLFormatter(escape(f"🔹Дата выпуска автомобиля {brand}: "))}{HTMLFormatter(bold(f"{date}"))}
{HTMLFormatter(escape(f"📌В таможенных органах для расчёта таможенных платежей будут отталкиваться от: "))}{HTMLFormatter(bold(date))}
"""
    elif mm_yyyy:
        mess = f"""
{HTMLFormatter(escape(f"🔹Дата выпуска автомобиля {brand}: "))}{HTMLFormatter(bold(f"{date}"))}
{HTMLFormatter(escape(f"📌В таможенных органах для расчёта таможенных платежей будут отталкиваться от: "))}{HTMLFormatter(bold('15.' + date))}
"""
    elif yyyy:
        mess = f"""
{HTMLFormatter(escape(f"🔹Год выпуска автомобиля {brand}: "))}{HTMLFormatter(bold(f"{date}"))}
"""

    return mess


async def message_send_honda(message: Message, ) -> None:

    text = f"""
{HTMLFormatter(escape("📌В видео-инструкции пошагово показано "))}{HTMLFormatter(bold("«Как узнать дату выпуска автомобиля Honda по каталогу?»"))}.

{HTMLFormatter(link("https://grade.customer.honda.co.jp/apps/grade/hccg0010201/search", "🔹Перейти в каталог"))}
"""

    await delete_mess(message.chat.id)

    response = await api.send_video(chat_id=message.chat.id,
                                    video="BAACAgIAAx0Cf0QyWAACAUNmOd7CaslXhtzJJ1o9oScHDDRPxwACH0cAAv28mEmZZDGc4QGJ9jUE")
    await save_mess(response.unwrap())

    response = await api.send_message(text=text,
                                      chat_id=message.chat.id,
                                      reply_markup=KEYBOARD_CANCEL,
                                      parse_mode=fmt.PARSE_MODE)
    await save_mess(response.unwrap())


@dp.message(DateProduction.Message(DateProduction.VIN_NUMBER))
async def date_production_vin(message: Message) -> None:
    try:
        brand = ctx.get(f"date_production_{message.chat.id}")['brand']

        response = await DateProduction.request(message.text.unwrap(), brand)
        print(response)
        if response:

            if response[0] != '' and response[0] is not None:
                mess = message_found(response[1], response[0])
            else:
                mess = message_unfound(response[1])
        else:
            mess = message_unfound()

        await delete_mess(message.chat.id)
        response = await api.send_message(text=mess,
                                          chat_id=message.chat.id,
                                          reply_markup=KEYBOARD_CANCEL,
                                          parse_mode=fmt.PARSE_MODE)
        await save_mess(response.unwrap())

        await DateProduction.delete(message.chat.id)

    except Exception:
        executor.traceback = traceback.format_exc()
    finally:
        await executor.logger(message, intermediate=True)

#NCP25-0018353
#MXUA85-0009214

