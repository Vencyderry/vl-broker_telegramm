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

from typing import List, Any, Coroutine, Tuple
from client import ctx, client


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
    ENGINE = "engine"

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
        YEAR_ADDITION,
        VOLUME,
        POWER
    ]

    MSG_PRICE = (f"{HTMLFormatter(escape('🔹Укажите стоимость:'))}\n"
                 f"{HTMLFormatter(italic(escape('В формате, например: 1000000')))}")

    MSG_YEAR = (f"{HTMLFormatter(escape('🔹Укажите год выпуска:'))}\n"
                f"{HTMLFormatter(italic(escape('В формате, например: 2020')))}")

    MSG_VOLUME = (f"{HTMLFormatter(escape('🔹Укажите объем двигателя:'))}\n"
                  f"{HTMLFormatter(italic(escape('В формате, например: 1500')))}")

    MSG_POWER = (f"{HTMLFormatter(escape('🔹Укажите мощность в л.с.:'))}\n"
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

    TOYOTA_NISSAN = "date_production_brand_1"
    HONDA = "date_production_brand_2"

    BRANDS = [
        TOYOTA_NISSAN,
        HONDA
    ]

    @classmethod
    async def request(cls, vin: str) -> tuple[Any, Any] | None:

        links = {
            "toydiy": {
                "url": f"https://www.toyodiy.com/parts/q?vin={vin}",
                "data": None
             },
            "emex": {
                "url": "https://emex.ru/api/parts/vin",
                "data": {"vin": vin}
             }
        }

        date = await cls.request_to_emex(links['emex'])

        if date is None:
            date = await cls.request_to_toydiy(links['toydiy'])

        return date

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
