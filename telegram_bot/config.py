import os
from dataclasses import dataclass
from typing import List
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from data.config import settings


@dataclass
class DbConfig:
    host: str
    password: str
    user: str
    database: str

    def __init__(self, host: str, password: str, user: str, database: str):
        self.host = host
        self.password = password
        self.user = user
        self.database = database

        from sqlalchemy.engine.create import create_engine
        from sqlalchemy.ext.asyncio.engine import create_async_engine
        from sqlalchemy.sql.expression import text

        self.sync_engine = create_engine(self.get_sync_url())
        self.async_engine = create_async_engine(self.get_url())

        with open('services/initial_db.sql') as f:
            query = text(f.read())
            self.sync_engine.execute(query)

    def get_sync_url(self) -> str:
        return f'postgresql://{self.user}:{self.password}@{self.host}/{self.database}'

    def get_url(self) -> str:
        return f'postgresql+asyncpg://{self.user}:{self.password}@{self.host}/{self.database}'


@dataclass
class TgBot:
    token: str
    chat_id: int
    admin_ids: List[int]
    use_redis: bool

    def __init__(self, token, admin_ids, use_redis):
        self.token = token
        self.chat_id = int(token.split(':')[0])
        self.admin_ids = admin_ids
        self.use_redis = use_redis


@dataclass
class SheetConfig:
    credentials_path: str
    credentials: Credentials
    token_path: str
    spreadsheet_id: str


@dataclass
class Miscellaneous:
    other_params: str = None


@dataclass
class WebhookConfig:
    path: str
    url: str
    host: str
    port: int


@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig
    misc: Miscellaneous
    sheet: SheetConfig
    webhook: WebhookConfig


def get_creds(creds_file_name: str, token_file_name: str) -> Credentials:
    SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly',
              'https://www.googleapis.com/auth/drive']

    creds = None
    if os.path.exists(token_file_name):
        creds = Credentials.from_authorized_user_file(token_file_name, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_file_name, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_file_name, 'w') as token:
            token.write(creds.to_json())

    return creds


def load_config():
    return Config(
        tg_bot=TgBot(
            token=settings.TG_TOKEN,
            admin_ids=list(map(int, settings.ADMINS.split(','))),
            use_redis=settings.USE_REDIS
        ),
        db=DbConfig(
            host=settings.DB_HOST,
            password=settings.DB_PASS,
            user=settings.DB_USER,
            database=settings.DB_NAME
        ),
        misc=Miscellaneous(),
        sheet=SheetConfig(
            credentials_path=settings.CREDENTIALS_PATH,
            token_path=settings.TOKEN_PATH,
            credentials=get_creds(settings.CREDENTIALS_PATH, settings.TOKEN_PATH),
            spreadsheet_id=settings.SPREADSHEET_ID
        ),
        webhook=WebhookConfig(
            path=settings.WEBHOOK_PATH,
            url=settings.WEBHOOK_URL,
            host=settings.WEBAPP_HOST,
            port=settings.WEBAPP_PORT
        )
    )
