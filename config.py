from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from decouple import config

TOKEN = config("TOKEN")
ADMIN = config("ADMIN", cast=int)

bot = Bot(TOKEN)
dp = Dispatcher(bot=bot, storage=MemoryStorage())
