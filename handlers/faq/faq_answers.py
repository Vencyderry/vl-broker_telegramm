import traceback

from telegrinder import CallbackQuery, Dispatch, InlineKeyboard, InlineButton
from telegrinder.types import LinkPreviewOptions

from client import api, fmt
from tools import save_mess, delete_mess
from rules import CallbackDataStartsWith
from handlers.executor import ExecutorType, DispatchExecutor
from .faq_patterns import FAQ_ANSWERS
from operations import get_system

dp = Dispatch()

BACK_KEYBOARD = (
    InlineKeyboard()
    .add(InlineButton("Вернуться назад", callback_data="faq_menu")).row()
).get_markup()

executor_faq_answers = DispatchExecutor(title="faq_answers",
                                        type_executor=ExecutorType.KEYBOARD
                                        )


@dp.callback_query(CallbackDataStartsWith("faq_#"))
async def svh_info(cq: CallbackQuery) -> None:
    try:
        message = cq.message.unwrap().v

        faq_answer = FAQ_ANSWERS[cq.data.unwrap()]

        # 4 question (file includes)
        document = None
        if "PDF_PRICE" in faq_answer:
            faq_answer = faq_answer.replace(" PDF_PRICE", "")
            system = get_system()
            document = system.price_pdf

        await delete_mess(message.chat.id)
        response = await api.send_message(text=faq_answer,
                                          chat_id=message.chat.id,
                                          reply_markup=BACK_KEYBOARD,
                                          parse_mode=fmt.PARSE_MODE,
                                          link_preview_options=LinkPreviewOptions(is_disabled=True))
        await save_mess(response.unwrap())

        if document:
            await api.send_document(chat_id=message.chat.id,
                                    caption="📌Открыть/скачать прайс-лист в формате PDF.",
                                    document=document)
            response.unwrap().message_id += 1
            await save_mess(response.unwrap())

    except Exception:
        executor_faq_answers.traceback = traceback.format_exc()
    finally:
        await executor_faq_answers.logger(cq)
