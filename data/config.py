from typing import Optional

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from pydantic import BaseSettings
from aiogram.types import ParseMode

from aiogram import Dispatcher, Bot, types


class Settings(BaseSettings):
    PROJECT_NAME: str = 'Movement'
    TG_TOKEN: Optional[str]
    ADMINS: Optional[list] = []
    LOGS_BASE_PATH: Optional[str] = ''

    class Config:
        env_prefix = 'MOVEMENT_'
        env_file = '../.env'
        env_file_encoding = 'utf-8'


settings = Settings()

storage = MemoryStorage()
bot = Bot(token=settings.TG_TOKEN, parse_mode=ParseMode.MARKDOWN)
dp = Dispatcher(bot, storage=storage)
