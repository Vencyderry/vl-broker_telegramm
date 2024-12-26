import traceback

from client import api, fmt
from operations import get_user
from models import User
from tools import save_mess, delete_mess
from rules import CallbackDataStartsWith
from telegrinder.tools import bold, escape, italic, HTMLFormatter

from telegrinder.rules import CallbackDataEq, Command
from telegrinder import CallbackQuery, Dispatch, Message
from telegrinder import InlineKeyboard, InlineButton, Dispatch, Message
from telegrinder.rules import Text, IsPrivate
from handlers.executor import ExecutorType, DispatchExecutor

dp = Dispatch()

PROMOS = [
    f"""
{HTMLFormatter(bold(escape("Новогоднее предложение для клиентов и бизнес-партнеров от VL-BROKER")))}

{HTMLFormatter(bold("🔹7 000 ₽"))}{HTMLFormatter(escape("— таможенное оформление транспортного средства на "))}{HTMLFormatter(bold("физическое лицо."))}
{HTMLFormatter(bold("🔹5 000 ₽"))}{HTMLFormatter(escape("— таможенное оформление каждого транспортного средства "))}{HTMLFormatter(bold("при подаче от 3-х заявок в один день."))}{HTMLFormatter(escape(" Выгодное предложение для "))}{HTMLFormatter(bold("бизнес-партнеров!"))}

{HTMLFormatter(escape("📌Новогоднее предложение актуально "))}{HTMLFormatter(bold("до 31-го декабря включительно."))}
{HTMLFormatter(escape("📌Действует "))}{HTMLFormatter(bold("независимо от даты прихода судна"))}{HTMLFormatter(escape("с Вашим транспортным средством."))}
{HTMLFormatter(escape("📌Скидки, при проведении нескольких акций, не суммируются. Применяться будут наиболее выгодные условия акций."))}

{HTMLFormatter(bold("Благодарим, что выбираете нас!"))}
""",

    f"""
{HTMLFormatter(bold(escape("Подарок от VL-BROKER к Вашему дню рождения")))}

{HTMLFormatter(bold(escape("🔹Дарим скидку 10%")))}{HTMLFormatter(escape(" на услугу таможенного оформления каждому клиенту в преддверии его дня рождения!"))}

{HTMLFormatter(escape("Скидка действует на заявку, "))}{HTMLFormatter(bold("поданную в течении недели до или после дня рождения"))}{HTMLFormatter(escape(", то есть 14 дней."))}
{HTMLFormatter(escape("📌Чтобы воспользоваться скидкой, покажите нашему менеджеру данное письмо-уведомление и свой паспорт."))}
{HTMLFormatter(escape("📌Скидки, при проведении нескольких акций, не суммируются. Применяться будут наиболее выгодные условия акций."))}

{HTMLFormatter(bold("Благодарим, что выбираете нас!"))}"""
]

BACK_KEYBOARD = (
    InlineKeyboard()
    .add(InlineButton("Вернуться назад", callback_data="promotions")).row()
).get_markup()

executor_videos = DispatchExecutor(title="promo_patterns",
                                   type_executor=ExecutorType.KEYBOARD
                                   )


@dp.callback_query(CallbackDataStartsWith("promo_"))
async def promo_patterns(cq: CallbackQuery) -> None:
    try:
        message = cq.message.unwrap().v

        msg = PROMOS[int(cq.data.unwrap().replace("promo_", ""))]

        await delete_mess(message.chat.id)
        response = await api.send_message(text=msg,
                                          chat_id=message.chat.id,
                                          parse_mode=fmt.PARSE_MODE,
                                          reply_markup=BACK_KEYBOARD)
        await save_mess(response.unwrap())

    except Exception:
        executor_videos.traceback = traceback.format_exc()
    finally:
        await executor_videos.logger(cq)