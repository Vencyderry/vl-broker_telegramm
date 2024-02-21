import datetime
import traceback

from telegrinder.rules import CallbackDataEq
from telegrinder import CallbackQuery, Dispatch

from client import ctx, api
from tools import save_mess, delete_mess
from handlers.executor import ExecutorType, DispatchExecutor

dp = Dispatch()


executor_currency = DispatchExecutor(title="currency",
                                     type_executor=ExecutorType.KEYBOARD
                                     )


@dp.callback_query(CallbackDataEq("currency"))
async def currency_cq(cq: CallbackQuery) -> None:
    try:
        message = cq.message.unwrap().v

        currency = ctx.get("currency")

        await delete_mess(message.chat.id)
        if currency:
            date_c = datetime.datetime.utcfromtimestamp(currency["timestamp"] - 3600 * 7)
            response = await api.send_message(text=f"""
🔹Курс валют от {date_c.day}.{date_c.month}.{date_c.year}, на {date_c.hour}:{"00" if not date_c.minute else date_c.minute} (МСК) 

🇨🇳Китайский юань ¥: {round((1 / currency["rates"]["CNY"]), 2)} ₽
🇯🇵Японская иена ¥: {round((1 / currency["rates"]["JPY"]), 2)} ₽
🇰🇷Корейская вона ₩: {round((1 / currency["rates"]["KRW"]), 2)} ₽
🇺🇸Американский доллар $: {round((1 / currency["rates"]["USD"]), 2)} ₽
🏴󠁧󠁢󠁥󠁮󠁧󠁿Фунт стерлингов £: {round((1 / currency["rates"]["GBP"]), 2)} ₽
🇪🇺Евро €: {round((1 / currency["rates"]["EUR"]), 2)} ₽

📌Курс валют обновляется в режиме онлайн.""",
                                              chat_id=message.chat.id)
        else:
            response = await api.send_message(text="🔹Данные курса валют загружаются, попробуйте снова через 20 минут.",
                                              chat_id=message.chat.id
                                              )
        await save_mess(response.unwrap())

    except Exception:
        executor_currency.traceback = traceback.format_exc()
    finally:
        await executor_currency.logger(cq)
