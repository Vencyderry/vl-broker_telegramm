import datetime
import pytz
import config
import telegrinder

from ctx_storage import CtxStorage
from telegrinder.client.aiohttp import AiohttpClient

wm = telegrinder.WaiterMachine()
api = telegrinder.API(token=telegrinder.Token(config.TOKEN))
bot = telegrinder.Telegrinder(api)
fmt = telegrinder.tools.HTMLFormatter
telegrinder.logger.set_level("INFO")
tz = pytz.timezone('Europe/Moscow')
client = AiohttpClient()
ctx = CtxStorage()

STARTED = datetime.datetime.now()
