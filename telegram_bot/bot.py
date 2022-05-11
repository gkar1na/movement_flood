from aiogram import Bot, Dispatcher
from aiogram.types import ParseMode
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.dispatcher.webhook import get_new_configured_app

from telegram_bot.config import load_config
from telegram_bot.filters.admin import AdminFilter
from telegram_bot.handlers.admin import register_admin
from telegram_bot.handlers.echo import register_echo
from telegram_bot.handlers.user import register_user
from telegram_bot.handlers.script import register_script
from telegram_bot.middlewares.db import DbMiddleware

from aiohttp import web
from aiohttp.web import Application

# TODO idk how install own module by "pip install -Ue ." – it doesn't work
import sys
sys.path.append('..')


def register_all_middlewares(dp: Dispatcher):
    dp.setup_middleware(DbMiddleware())


def register_all_filters(dp: Dispatcher):
    dp.filters_factory.bind(AdminFilter)


def register_all_handlers(dp: Dispatcher):
    register_script(dp)

    register_admin(dp)
    register_user(dp)

    register_echo(dp)


async def on_startup(app: Application):
    register_all_middlewares(dp)
    register_all_filters(dp)
    register_all_handlers(dp)

    webhook = await bot.get_webhook_info()
    if webhook.url != config.webhook.url:
        if not webhook.url:
            await bot.delete_webhook()
        await bot.set_webhook(config.webhook.url)


async def on_shutdown(app: Application):
    await bot.delete_webhook()
    await dp.storage.close()
    await dp.storage.wait_closed()


if __name__ == '__main__':
    from telegram_bot.misc import logging
    logging.setup()

    config = load_config()

    storage = RedisStorage2() if config.tg_bot.use_redis else MemoryStorage()
    bot = Bot(token=config.tg_bot.token, parse_mode=ParseMode.HTML)
    bot['config'] = config
    dp = Dispatcher(bot, storage=storage)

    app = get_new_configured_app(dispatcher=dp, path=config.webhook.path)

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    web.run_app(
        app,
        host=config.webhook.host,
        port=config.webhook.port,
    )
