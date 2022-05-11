from typing import Optional

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from pydantic import BaseSettings
from aiogram.types import ParseMode

from aiogram import Dispatcher, Bot, types


class Settings(BaseSettings):
    PROJECT_NAME: str = 'Movement'
    TG_TOKEN: Optional[str]
    ADMINS: Optional[str] = ''
    LOGS_BASE_PATH: Optional[str] = ''
    USE_REDIS: Optional[bool] = False
    DB_HOST: Optional[str] = '127.0.0.1'
    DB_PASS: str
    DB_USER: str
    DB_NAME: str
    CREDENTIALS_PATH: Optional[str] = '../data/credentials.json'
    TOKEN_PATH: Optional[str] = '../data/token.json'
    SPREADSHEET_ID: str

    class Config:
        env_prefix = 'MOVEMENT_'
        env_file = '../.env'
        env_file_encoding = 'utf-8'


settings = Settings()
