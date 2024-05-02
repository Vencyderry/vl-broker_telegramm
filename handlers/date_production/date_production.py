import traceback

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
    .add(InlineButton("Toyota & Nissan", callback_data="date_production_brand_1")).row()
    .add(InlineButton("Honda", callback_data="date_production_brand_2")).row()
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

        if cq.data.unwrap() == DateProduction.HONDA:
            await date_production_vin.func(message)
            return

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
    mess = f"""
{HTMLFormatter(escape(f"🔹Дата выпуска автомобиля {brand}: "))}{HTMLFormatter(bold(f"{date} г."))}
{HTMLFormatter(escape(f"📌В таможенных органах для расчёта таможенных платежей будут отталкиваться от: "))}{HTMLFormatter(bold(f"15.{date} г."))}
"""
    return mess


async def message_send_honda(message: Message, ) -> None:

    text = f"""
{HTMLFormatter(escape("📌В видео-инструкции пошагово показано "))}{HTMLFormatter(bold("«Как узнать дату выпуска автомобиля Honda по каталогу?»"))}.

{HTMLFormatter(link("https://grade.customer.honda.co.jp/apps/grade/hccg0010201/search", "🔹Перейти в каталог"))}
"""

    await delete_mess(message.chat.id)
    response = await api.send_message(text=text,
                                      chat_id=message.chat.id,
                                      reply_markup=KEYBOARD_CANCEL,
                                      parse_mode=fmt.PARSE_MODE)
    await save_mess(response.unwrap())

    response = await api.send_video(chat_id=message.chat.id,
                                    video="BAACAgIAAx0Cf0QyWAACATdmMuLJVFz7aT4Rn9J0F_KQgYXtlQACH0cAAv28mEmFguhCJM_G6jQE")
    await save_mess(response.unwrap())


@dp.message(DateProduction.Message(DateProduction.VIN_NUMBER))
async def date_production_vin(message: Message) -> None:
    try:
        brand = ctx.get(f"date_production_{message.chat.id}")['brand']

        if brand == DateProduction.HONDA:
            await message_send_honda(message)
            return
        else:

            response = await DateProduction.request(message.text.unwrap())
            if response:

                if response[1] == 'HONDA':

                    await message_send_honda(message)
                    return

                elif response[0] != '' and response[0] is not None:
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

