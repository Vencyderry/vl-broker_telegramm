import pandas as pd
import re
import requests
from bs4 import BeautifulSoup

from telegrinder.bot.dispatch.context import Context
from telegrinder import Message, MessageRule, CallbackQuery
from telegrinder.rules import CallbackQueryDataRule, CallbackQueryRule
from telegrinder.types.enums import ChatType
from telegrinder.modules import logger
from telegrinder.types import Nothing
from telegrinder.tools import italic, escape, HTMLFormatter

from typing import List, Any, Coroutine, Tuple, Optional
from client import ctx, client
from tools import decode, digit


class CallbackDataEqs(CallbackQueryDataRule):
    def __init__(self, values: List[str]):
        self.values = values

    async def check(self, event: CallbackQuery, ctx: Context) -> bool:
        for value in self.values:
            if event.data.unwrap() == value:
                return True
        return False


class CallbackDataStartsWith(CallbackQueryDataRule):
    def __init__(self, value: str):
        self.value = value

    async def check(self, event: CallbackQuery, ctx: Context) -> bool:
        return event.data.unwrap().startswith(self.value)


class Application(MessageRule):
    def __init__(self, state: str):
        self.state = state

    async def check(self, message: Message, ctx_: Context) -> bool:
        ctx_state = ctx.get(f"application_state:{message.chat.id}")

        if message.chat.type == ChatType.PRIVATE:
            if ctx_state:
                if message.text != Nothing:
                    if ctx_state == self.state:
                        return True

        return False

    @staticmethod
    async def get(target: int) -> dict | None:
        state = ctx.get(f"application_state:{target}")
        if state:
            return state
        return None

    @staticmethod
    async def set(target: int, state: str) -> None:
        ctx.set(f"application_state:{target}", state)

    @staticmethod
    async def delete(target: int) -> None:
        ctx.delete(f"application_state:{target}")

    NAME = "name"
    COUNTRY = "country"
    CARGO = "cargo"
    NUMBER = "number"

    STAGES = [
        NAME,
        COUNTRY,
        CARGO,
        NUMBER
    ]


class Calculator:

    class Message(MessageRule):
        def __init__(self, state: str, strategy: str):
            self.state = state
            self.strategy = strategy

        async def check(self, message: Message, ctx_: Context) -> bool:
            ctx_state_data = ctx.get(f"calculator_state:{message.chat.id}")

            if ctx_state_data:
                ctx_data = ctx_state_data["state"]
                ctx_strategy = ctx_state_data["strategy"]

                if message.chat.type == ChatType.PRIVATE:
                    if message.text != Nothing:
                        if ctx_data == self.state:
                            if ctx_strategy:
                                if ctx_strategy == self.strategy:
                                    return True
                                return False
                            return True

            return False

    class CallbackQuery(CallbackQueryRule):
        def __init__(self, state: str, strategy: str):
            self.state = state
            self.strategy = strategy

        async def check(self, cq: CallbackQuery, ctx_: Context) -> bool:

            ctx_state_data = ctx.get(f"calculator_state:{cq.message.unwrap().v.chat.id}")

            if ctx_state_data:
                ctx_data = ctx_state_data["state"]
                ctx_strategy = ctx_state_data["strategy"]

                if cq.message.unwrap().v.chat.type == ChatType.PRIVATE:
                    if ctx_data == self.state:
                        if ctx_strategy:
                            if ctx_strategy == self.strategy:
                                return True
                            return False
                        return True

            return False

    @staticmethod
    async def get(target: int) -> dict | None:
        state = ctx.get(f"calculator_state:{target}")
        if state:
            return state["state"]
        return None

    @staticmethod
    async def set(target: int, state: str, strategy: str = None) -> None:
        ctx.set(f"calculator_state:{target}", {"state": state, "strategy": strategy})

    @staticmethod
    async def delete(target: int) -> None:
        ctx.delete(f"calculator_state:{target}")

    @staticmethod
    async def result(target: int, data: dict) -> str:
        calculator = ctx.get(f"calculator_{target}")
        text = (
            f"Расчёт таможенных платежей:\n"
            f"🔹Сборы за таможенное оформление: {digit(data['fees'])} ₽\n"
            f"🔹Пошлина: {digit(data['duty'])} ₽\n"
            f"🔹НДС: {digit(data['nds'])} ₽\n"
            f"REPLACE_EXCISE\n"
            f"🔹Итог: {digit(data['custom'])} ₽\n\n"
            f"🔹Утилизационный сбор: {digit(data['util'])} ₽\n"
            f"🔹Итог с утильсбором: {digit(round(data['custom'] + data['util']))} ₽\n\n"
            f"📌 Расчёты являются предварительными и необходимы для того, чтобы "
            f"сориентировать Вас. За более достоверным расчётом оставьте заявку или обратитесь к нашему менеджеру.\n\n"
            f"Наши специалисты проконсультируют Вас!"
        )

        if calculator["fiz"] == 0 or (calculator["fiz"] == 1 and (calculator['hybrid'] == 0 or calculator['engine'] == "e")):
            replace_excise = f"🔹Акциз: {digit(data['excise'])} ₽\n"
        else:
            replace_excise = ""

        text = text.replace("REPLACE_EXCISE\n", replace_excise)
        return text

    STRATEGY = "strategy"
    MOTO = "moto"
    AUTO = "auto"
    FIZ = "fiz"
    CURRENCY = "currency"
    PRICE = "price"
    YEAR = "year"
    YEAR_ADDITION = "year_addition"
    VOLUME = "volume"
    POWER = "power"
    POWER_SUM = "power_sum"
    ENGINE = "engine"
    HYBRID = "hybrid"

    MOTO_STAGES = [
        STRATEGY,
        FIZ,
        CURRENCY,
        PRICE,
        YEAR,
        VOLUME,
        POWER
    ]

    AUTO_STAGES = [
        STRATEGY,
        FIZ,
        CURRENCY,
        PRICE,
        ENGINE,
        YEAR,
        VOLUME,
        POWER
    ]

    MSG_PRICE = (f"{HTMLFormatter(escape('🔹Укажите стоимость:'))}\n"
                 f"{HTMLFormatter(italic(escape('В формате, например: 1000000')))}")

    MSG_YEAR = (f"{HTMLFormatter(escape('🔹Укажите год выпуска:'))}\n"
                f"{HTMLFormatter(italic(escape('В формате, например: 2020')))}")

    MSG_VOLUME = (f"{HTMLFormatter(escape('🔹Укажите объем двигателя:'))}\n"
                  f"{HTMLFormatter(italic(escape('В формате, например: 1500')))}")

    MSG_POWER = (f"{HTMLFormatter(escape('🔹Укажите мощность ДВС в л.с.:'))}\n"
                 f"{HTMLFormatter(italic(escape('В формате, например: 144')))}")

    MSG_POWER_SUM = (f"{HTMLFormatter(escape('🔹Укажите cуммарную 30 минутную полезные мощности всех электромоторов'))}\n"
                     f"{HTMLFormatter(italic(escape('В формате, например: 144')))}")


class DateProduction:

    class Message(MessageRule):
        def __init__(self, state: str):
            self.state = state

        async def check(self, message: Message, ctx_: Context) -> bool:
            ctx_state_data = ctx.get(f"date_production_state:{message.chat.id}")

            if ctx_state_data:
                ctx_data = ctx_state_data["state"]

                if message.chat.type == ChatType.PRIVATE:
                    if message.text != Nothing:
                        if ctx_data == self.state:
                            return True

            return False

    class CallbackQuery(CallbackQueryRule):
        def __init__(self, state: str):
            self.state = state

        async def check(self, cq: CallbackQuery, ctx_: Context) -> bool:

            ctx_state_data = ctx.get(f"date_production_state:{cq.message.unwrap().v.chat.id}")

            if ctx_state_data:
                ctx_data = ctx_state_data["state"]

                if cq.message.unwrap().v.chat.type == ChatType.PRIVATE:
                    if ctx_data == self.state:
                        return True

            return False

    @staticmethod
    async def get(target: int) -> dict | None:
        state = ctx.get(f"date_production_state:{target}")
        if state:
            return state["state"]
        return None

    @staticmethod
    async def set(target: int, state: str) -> None:
        ctx.set(f"date_production_state:{target}", {"state": state})

    @staticmethod
    async def delete(target: int) -> None:
        ctx.delete(f"date_production_state:{target}")

    BRAND = "brand"
    VIN_NUMBER = "vin_number"

    STAGES = [
        BRAND,
        VIN_NUMBER
    ]

    TOYOTA = "date_production_brand_4"
    NISSAN = "date_production_brand_1"
    MAZDA = "date_production_brand_8"
    MITSUBISHI = "date_production_brand_2"
    HONDA = "date_production_brand_9"
    SUZUKI = "date_production_brand_5"
    SUBARU = "date_production_brand_6"
    ISUZU = "date_production_brand_3"
    DAIHATSU = "date_production_brand_7"

    BRANDS = [
        TOYOTA,
        NISSAN,
        MAZDA,
        MITSUBISHI,
        HONDA,
        SUZUKI,
        SUBARU,
        ISUZU,
        DAIHATSU
    ]

    ID_BRANDS = {
        "date_production_brand_1": "NISSAN",
        "date_production_brand_2": "MITSUBISHI",
        "date_production_brand_3": "ISUZU",
        "date_production_brand_4": "TOYOTA",
        "date_production_brand_5": "SUZUKI",
        "date_production_brand_6": "SUBARU",
        "date_production_brand_7": "DAIHATSU",
        "date_production_brand_8": "MAZDA",
        "date_production_brand_9": "HONDA",
    }

    @staticmethod
    def format_date(date: str) -> str:

        if "январь" in date:
            date = date.replace("январь ", "01.")
        elif "февраль" in date:
            date = date.replace("февраль ", "02.")
        elif "март" in date:
            date = date.replace("март ", "03.")
        elif "апрель" in date:
            date = date.replace("апрель ", "04.")
        elif "май" in date:
            date = date.replace("май ", "05.")
        elif "июнь" in date:
            date = date.replace("июнь ", "06.")
        elif "июль" in date:
            date = date.replace("июль ", "07.")
        elif "август" in date:
            date = date.replace("август ", "08.")
        elif "сентябрь" in date:
            date = date.replace("сентябрь ", "09.")
        elif "октябрь" in date:
            date = date.replace("октябрь ", "10.")
        elif "ноябрь" in date:
            date = date.replace("ноябрь ", "11.")
        elif "декабрь" in date:
            date = date.replace("декабрь ", "12.")
        return date


    @staticmethod
    def extract_date(text: str) -> str:

        text = DateProduction.format_date(text)

        patterns = [
            r'(\d{2})[ .](\d{2})[ .](\d{4})',  # DD.MM.YYYY or DD MM.YYYY
            r'(\d{2})[ .](\d{4})',  # MM.YYYY or MM YYYY
            r'(\d{4})'  # YYYY
        ]
        year = None
        month = None
        day = None
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                if len(match.groups()) == 3:  # DD.MM.YYYY or DD MM.YYYY
                    day, month, year = map(int, match.groups())
                    break
                elif len(match.groups()) == 2:  # MM.YYYY or MM YYYY
                    month, year = map(int, match.groups())
                    break
                elif len(match.groups()) == 1:  # YYYY
                    year = int(match.group(1))
                    break

        result = (f"{0 if day and day < 10 else ''}"
                  f"{day if day else ''}"
                  f"{'.' if day and month else ''}"
                  f"{0 if month and month < 10 else ''}"
                  f"{month if month else ''}"
                  f"{'.' if month and year else ''}"
                  f"{year if year else ''}")

        return result

    @classmethod
    async def request(cls, vin: str, brand: str = None) -> tuple[Any, Any] | None:

        if brand:
            brand = int(brand.replace('date_production_brand_', ''))

        links = {
            "toydiy": {
                "url": f"https://www.toyodiy.com/parts/q?vin={vin}",
                "data": None
             },
            "emex": {
                "url": "https://emex.ru/api/parts/vin",
                "data": {"vin": vin}
             },
            "local_api": {
                "url": f"http://82.147.71.242:3000/api?company={brand}&vincode={vin}",
                "data": None,
                "brand": brand
            }
        }

        date = await cls.request_to_local_api(links['local_api'])

        return date

    @classmethod
    async def request_to_local_api(cls, link: dict = None) -> Any | None:
        try:
            response_api = await client.request_text(url=link['url'])
            print(response_api)
            date = decode(response_api)
            if len(date) == 0:
                return
            elif "message" in date or "message" in date[0]:
                return
            elif date[0]["description"] == "information not found":
                return
            else:
                date = date[0]["description"]

            return cls.extract_date(date), cls.ID_BRANDS[f"date_production_brand_{link['brand']}"]
        except:
            return

    @classmethod
    async def request_to_toydiy(cls, link: dict = None) -> tuple[Any, Any] | None:
        try:
            response_api = await client.request_text(url=link['url'])
            list_frame = pd.read_html(response_api)

            for frame in list_frame:
                search = frame.get(1, None)
                search = re.search(r"Year.*?\n", str(search))
                if search is not None:
                    date = search.group().replace("Year", "").replace("\n", "").replace("\\", "")
                    return date, 'TOYOTA'
        except:
            return

    @classmethod
    async def request_to_emex(cls, link: dict = None) -> tuple[Any, Any] | None:
        try:
            response_api = await client.request_json(url=link['url'],
                                                     method="POST",
                                                     json=link['data'])
            return response_api[0]["date"], response_api[0]["brand"]
        except:
            return


class Distribution(MessageRule):
    def __init__(self, state: str):
        self.state = state

    async def check(self, message: Message, ctx_: Context) -> bool:
        ctx_state = ctx.get(f"distribution_state:{message.chat.id}")

        if message.chat.type == ChatType.PRIVATE:
            if ctx_state:
                if ctx_state == self.state:
                    return True

        return False

    @staticmethod
    async def get(target: int) -> dict | None:
        state = ctx.get(f"distribution_state:{target}")
        if state:
            return state
        return None

    @staticmethod
    async def set(target: int, state: str) -> None:
        ctx.set(f"distribution_state:{target}", state)

    @staticmethod
    async def delete(target: int) -> None:
        ctx.delete(f"distribution_state:{target}")

    TEXT = "text"
    ADD_MESSAGE = "add_message"

    STAGES = [
        TEXT,
        ADD_MESSAGE
    ]
