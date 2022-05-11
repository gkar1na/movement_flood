from pydantic import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = 'Movement'
    TG_TOKEN: str
    ADMINS: str = ''
    LOGS_BASE_PATH: str = ''
    USE_REDIS: bool = False
    DB_HOST: str = '127.0.0.1'
    DB_PASS: str
    DB_USER: str
    DB_NAME: str
    CREDENTIALS_PATH: str = '../data/credentials.json'
    TOKEN_PATH: str = '../data/token.json'
    SPREADSHEET_ID: str

    WEBHOOK_PATH: str = ''
    WEBHOOK_URL: str
    WEBAPP_HOST: str = '127.0.0.1'
    WEBAPP_PORT: int = 8080

    class Config:
        env_prefix = 'MOVEMENT_'
        env_file = '../.env'
        env_file_encoding = 'utf-8'


settings = Settings()
