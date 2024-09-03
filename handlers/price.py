import traceback
import pathlib

from telegrinder.rules import CallbackDataEq, Command
from telegrinder import CallbackQuery, Dispatch, Message
from telegrinder.types import InputFile, Nothing
from telegrinder.tools import bold, escape, italic, HTMLFormatter

from client import api, fmt
from tools import save_mess, delete_mess
from handlers.executor import ExecutorType, DispatchExecutor
from operations import get_system
from patterns import ERROR_PERMISSION
from permissions_store import is_admin, is_sr_admin

dp = Dispatch()

PRICE = f"""
{HTMLFormatter(bold("🔹Прайс-лист VL-BROKER"))}

{HTMLFormatter(bold("Комплексное решение для автомобилей:"))}
{HTMLFormatter(escape("*️⃣таможенное оформление автомобиля на физическое лицо — "))}{HTMLFormatter(bold("37 000 ₽"))}
{HTMLFormatter(escape("*️⃣таможенное оформление автомобиля на юридическое лицо — "))}{HTMLFormatter(bold("84 000 ₽"))}
{HTMLFormatter(italic(escape("ВАЖНО! Стоимость размещения автомобиля на складе временного хранения зависит от тарифов СВХ, сторонней организации; от 32 000 ₽")))}
{HTMLFormatter(italic(escape("ВАЖНО! Вывоз автомобиля с СВХ в лабораторию в услугу по оформлению документов СБКТС и ЭПТС не входит. Данную услугу предоставляем дополнительно, цена: 5 000 ₽")))}

{HTMLFormatter(bold("Комплексное решение для мотоциклов:"))}
{HTMLFormatter(escape("*️⃣таможенное оформление мотоцикла — "))}{HTMLFormatter(bold("27 000 ₽"))}
{HTMLFormatter(italic(escape("ВАЖНО! Стоимость размещения мотоцикла на складе временного хранения зависит от тарифов СВХ, сторонней организации; от 15 000 ₽")))}

{HTMLFormatter(bold("Услуги по таможенному оформлению:"))}
{HTMLFormatter(escape("*️⃣таможенное оформление автомобиля на физическое лицо — "))}{HTMLFormatter(bold("12 000 ₽"))}
{HTMLFormatter(escape("*️⃣таможенное оформление автомобиля на юридическое лицо — "))}{HTMLFormatter(bold("18 000 ₽"))}
{HTMLFormatter(escape("*️⃣таможенное оформление мотоцикла — "))}{HTMLFormatter(bold("12 000 ₽"))}
{HTMLFormatter(escape("*️⃣таможенное оформление спецтехники — "))}{HTMLFormatter(bold("рассчитывается индивидуально"))}
{HTMLFormatter(escape("*️⃣таможенное оформление прочих грузов — "))}{HTMLFormatter(bold("рассчитывается индивидуально"))}
{HTMLFormatter(escape("*️⃣таможенное оформление декларации на товары — "))}{HTMLFormatter(bold("от 15 000 ₽"))}
{HTMLFormatter(escape("*️⃣таможенное оформление декларации на автомобили, спецтехнику и грузовики  — "))}{HTMLFormatter(bold("от 18 000 ₽"))}
{HTMLFormatter(escape("*️⃣таможенное оформление декларации на запчасти и оборудование — "))}{HTMLFormatter(bold("от 15 000 ₽"))}

{HTMLFormatter(bold("Дополнительные услуги к основному договору:"))}
{HTMLFormatter(escape("*️⃣экспедирование контейнера с автомобилем — "))}{HTMLFormatter(bold("10 000 ₽"))}
{HTMLFormatter(escape("*️⃣корректировка коносамента — "))}{HTMLFormatter(bold("3 000 ₽"))}
{HTMLFormatter(escape("*️⃣оформление СБКТС и ЭПТС автомобиля — "))}{HTMLFormatter(bold("20 000 ₽"))}
{HTMLFormatter(escape("*️⃣оформление СБКТС и ЭПТС мотоцикла — "))}{HTMLFormatter(bold("15 000 ₽"))}
{HTMLFormatter(escape("*️⃣ЗОЕТС и ЭПТС "))}{HTMLFormatter(italic(escape("(только для юрлиц; ТС до 3 лет) — ")))}{HTMLFormatter(bold("индивидуально"))}
{HTMLFormatter(escape("*️⃣устройство ЭРА-ГЛОНАСС "))}{HTMLFormatter(italic(escape("(только для юрлиц)")))}{HTMLFormatter(escape(" — "))}{HTMLFormatter(bold("35 000 ₽"))}
{HTMLFormatter(escape("*️⃣установка ЭРА-ГЛОНАСС — "))}{HTMLFormatter(bold("1 500 ₽"))}
{HTMLFormatter(escape("*️⃣активация ЭРА-ГЛОНАСС — "))}{HTMLFormatter(bold("4 500 ₽"))}
{HTMLFormatter(escape("*️⃣стандартная экспертиза — "))}{HTMLFormatter(bold("от 1 000 до 1 500 ₽"))}
{HTMLFormatter(escape("*️⃣снятие тонировки — "))}{HTMLFormatter(bold("от 1000 ₽"))}
{HTMLFormatter(escape("*️⃣вывоз легкового автомобиля с СВХ в лабораторию — "))}{HTMLFormatter(bold("5 000 ₽"))}
{HTMLFormatter(escape("*️⃣вывоз мотоцикла с СВХ в лабораторию — "))}{HTMLFormatter(bold("8 000 ₽"))}
{HTMLFormatter(escape("*️⃣постановка транспортного средства на учёт в ГАИ — "))}{HTMLFormatter(bold("15 000 ₽"))}
{HTMLFormatter(escape("*️⃣отправка автомобиля в сухогрузном контейнере 20-ти футов до Москвы — "))}{HTMLFormatter(bold("от 265 000 ₽"))}
{HTMLFormatter(escape("*️⃣вывоз в транспортную компанию для отправки — "))}{HTMLFormatter(bold("4 500 ₽"))}
{HTMLFormatter(escape("*️⃣сопровождение технического обслуживания — "))}{HTMLFormatter(bold("6 000 ₽"))}
{HTMLFormatter(escape("*️⃣замена запчастей, колёс и расходников — "))}{HTMLFormatter(bold("индивидуально"))}
{HTMLFormatter(escape("*️⃣установка автосигнализации — "))}{HTMLFormatter(bold("индивидуально"))}
{HTMLFormatter(escape("*️⃣стоянка для легкового автомобиля — "))}{HTMLFormatter(bold("200 ₽"))}{HTMLFormatter(escape(" / сутки"))}
{HTMLFormatter(escape("*️⃣стоянка для мотоцикла — "))}{HTMLFormatter(bold("100 ₽"))}{HTMLFormatter(escape(" / сутки"))}
{HTMLFormatter(escape("*️⃣расходы на бензин — "))}{HTMLFormatter(bold("от 500 ₽"))}
{HTMLFormatter(escape("*️⃣и прочее сопровождение — "))}{HTMLFormatter(bold("рассчитывается индивидуально"))}

{HTMLFormatter(escape("📌Если у Вас возникли сложности, не обозначенные выше, то мы готовы оказать индивидуальный подход — наши специалисты сориентируют и посодействуют Вам."))}
"""

executor_get_price = DispatchExecutor(title="get_price",
                                      type_executor=ExecutorType.KEYBOARD
                                      )


@dp.callback_query(CallbackDataEq("get_price"))
async def get_price(cq: CallbackQuery) -> None:
    try:
        message = cq.message.unwrap().v

        await delete_mess(message.chat.id)
        response = await api.send_message(text=PRICE,
                                          chat_id=message.chat.id,
                                          parse_mode=fmt.PARSE_MODE)

        await save_mess(response.unwrap())
        system = get_system()
        price_pdf = system.price_pdf
        if price_pdf:
            await api.send_document(chat_id=message.chat.id,
                                    caption="📌Открыть/скачать прайс-лист в формате PDF.",
                                    document=price_pdf)
            response.unwrap().message_id += 1
            await save_mess(response.unwrap())

    except Exception:
        executor_get_price.traceback = traceback.format_exc()
    finally:
        await executor_get_price.logger(cq)


executor_set_price = DispatchExecutor(title="set_price",
                                      permission="operation.admin",
                                      type_executor=ExecutorType.COMMAND
                                      )


@dp.message(Command(["setprice"]))
async def set_price(message: Message) -> None:
    try:

        if not is_admin(message.from_.unwrap().id) and not is_sr_admin(message.from_.unwrap().id):
            await message.answer(ERROR_PERMISSION)
            return

        system = get_system()
        if message.reply_to_message is Nothing or message.reply_to_message.unwrap().document is Nothing:
            await message.answer("⚠️ Ответьте командой на сообщение в котором есть PDF документ.")
            return

        system.price_pdf = message.reply_to_message.unwrap().document.unwrap().file_id
        system.save()
        await message.answer("✅ Price PDF обновлён.")

    except Exception:
        executor_set_price.traceback = traceback.format_exc()
    finally:
        await executor_set_price.logger(message)

