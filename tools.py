import json

from client import ctx, api

from telegrinder import Message
from typing import Union


def decode(value):
    """Функция декодер жсон.
    Преобрзует строку в dict/list."""
    value = value.replace("\'", "\"")

    result = json.loads(value)
    return result


def digit(number: Union[str, int]) -> str:
    """Функция разделяющая число на разряды"""

    if isinstance(number, str):
        number = int(number)

    return "{:,}".format(number)


async def save_mess(message: Message):

    if message.chat.type == 'private':
        if not ctx.get(f"messages_{message.chat.id}"):
            ctx.set(f"messages_{message.chat.id}", [])

        messages = ctx.get(f"messages_{message.chat.id}")
        messages.append(message.message_id)
        ctx.set(f"messages_{message.chat.id}", messages)


async def delete_mess(chat_id):
    messages = ctx.get(f"messages_{chat_id}")

    if messages:
        for i in range(len(messages)):

            try:
                await api.delete_message(message_id=messages[0], chat_id=chat_id)

            except:
                pass

            if len(messages) != 0:
                messages.remove(messages[0])
            ctx.set(f"messages_{chat_id}", messages)