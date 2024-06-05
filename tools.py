import json
import re
import string

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


class Swear:

    standart_dirt = [1093, 1091, 1081, 124, 1073, 1083, 1103, 124, 1077, 1073, 124,
                     1087, 1080, 1079, 1076, 124, 1105, 1073]  # censored

    standart_dirt = ''.join(chr(n) for n in standart_dirt)

    words_exceptions = ["оскорблять", "парикмахер", "мандат", "подштрихуй", "подстрахуй"]

    @staticmethod
    def _get_search(pattern: str):
        """
        return function to search words with the pattern
        """

        def hide_search(word: str) -> bool:
            return bool(re.search(pattern, word)) and (word not in Swear.exceptions)

        return hide_search

    @staticmethod
    def is_dirt(pattern: str = standart_dirt):
        """
        return function to search pattern in text
        """
        funk = Swear._get_search(pattern)

        def hide_search(text: str) -> bool:
            for word in re.findall(r'\w+', text):
                if funk(word.lower()):
                    return True

            return False

        return hide_search


words_swear = [
    "блядь",
    "ебать",
    "пизда",
    "хуй",
    "хуи",
    "хуе",
    "мудак",
    "манда",
    "гандон",
    "пидор",
    "педик",
    "залупа",
    "дрочить",
    "сука",
    "сучки",
    "сученок",
    "ебаный",
    "уебан",
    "пиздец",
    "бля"
]

words_only_warn = [
    "хрен",
    "нахрен",
    "похрен",
    "нахер",
    "похер",
    "хер"
]

words_exceptions = [
    "оскорблять",
    "парикмахер",
    "мандат",
    "подштрихуй",
    "подстрахуй",
    "закупа",
    "закуп"
]


def detector_swear(phrase: str) -> dict:

    search = False
    word_ = None
    fragment_ = None
    only_warn = False

    for exception in words_exceptions:
        if exception in phrase:
            phrase = phrase.replace(exception, "EXCEPT")

    phrase_split = phrase.split()
    for word in words_only_warn:
        if word in phrase_split:
            search = False
            word_ = word
            fragment_ = word
            only_warn = True

    def distance(a, b):
        # Calculates the Levenshtein distance between a and b.
        n, m = len(a), len(b)
        if n > m:
            # Make sure n <= m, to use O(min(n, m)) space
            a, b = b, a
            n, m = m, n

        current_row = range(n + 1)  # Keep current and previous row, not entire matrix
        for i in range(1, m + 1):
            previous_row, current_row = current_row, [i] + [0] * n
            for j in range(1, n + 1):
                add, delete, change = previous_row[j] + 1, current_row[j - 1] + 1, previous_row[j - 1]
                if a[j - 1] != b[i - 1]:
                    change += 1
                current_row[j] = min(add, delete, change)

        return current_row[n]

    d = {
        'а': ['а', 'a', '@'],
        'б': ['б', '6', 'b'],
        'в': ['в', 'b', 'v'],
        'г': ['г', 'r', 'g'],
        'д': ['д', 'd'],
        'е': ['е', 'e'],
        'ё': ['ё', 'e'],
        'ж': ['ж', 'zh', '*'],
        'з': ['з', '3', 'z'],
        'и': ['и', 'u', 'i'],
        'й': ['й', 'u', 'i'],
        'к': ['к', 'k', 'i{', '|{'],
        'л': ['л', 'l', 'ji'],
        'м': ['м', 'm'],
        'н': ['н', 'h', 'n'],
        'о': ['о', 'o', '0'],
        'п': ['п', 'n', 'p'],
        'р': ['р', 'r', 'p'],
        'с': ['с', 'c', 's', '$'],
        'т': ['т', 'm', 't'],
        'у': ['у', 'y', 'u'],
        'ф': ['ф', 'f'],
        'х': ['х', 'x', 'h', '}{'],
        'ц': ['ц', 'c', 'u,'],
        'ч': ['ч', 'ch'],
        'ш': ['ш', 'sh'],
        'щ': ['щ', 'sch'],
        'ь': ['ь', 'b'],
        'ы': ['ы', 'bi'],
        'ъ': ['ъ'],
        'э': ['э', 'e'],
        'ю': ['ю', 'io'],
        'я': ['я', 'ya']
    }

    for key, value in d.items():
        # Проходимся по каждой букве в значении словаря. То есть по вот этим спискам ['а', 'a', '@'].
        for letter in value:
            # Проходимся по каждой букве в нашей фразе.
            for phr in phrase:
                # Если буква совпадает с буквой в нашем списке.
                if letter == phr:
                    # Заменяем эту букву на ключ словаря.
                    phrase = phrase.replace(phr, key)

    # Проходимся по всем словам.
    for word in words_swear:
        # Разбиваем слово на части, и проходимся по ним.
        for part in range(len(phrase)):
            # Вот сам наш фрагмент.
            fragment = phrase[part: part+len(word)]
            # Если отличие этого фрагмента меньше или равно 16% этого слова, то считаем, что они равны.
            if distance(fragment, word) <= len(word)*0.166666667:
                # Если они равны, выводим надпись о их нахождении.

                word_ = word
                fragment_ = fragment
                search = True
                only_warn = False

    return {
        "result": search,
        "word": word_,
        "fragment": fragment_,
        "only_warn": only_warn
    }
