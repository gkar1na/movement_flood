import asyncio
from loguru import logger

# TODO idk how install own module by "pip install -Ue ." – it doesn't work
import sys
sys.path.append('..')

from aiogram import Bot, Dispatcher
from aiogram.types import ParseMode
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from telegram_bot.config import load_config
from telegram_bot.filters.admin import AdminFilter
from telegram_bot.handlers.admin import register_admin
from telegram_bot.handlers.echo import register_echo
from telegram_bot.handlers.user import register_user
from telegram_bot.middlewares.db import DbMiddleware


def register_all_middlewares(dp):
    dp.setup_middleware(DbMiddleware())


def register_all_filters(dp):
    dp.filters_factory.bind(AdminFilter)


def register_all_handlers(dp):
    register_admin(dp)
    register_user(dp)

    register_echo(dp)


async def main():
    bot['config'] = config

    register_all_middlewares(dp)
    register_all_filters(dp)
    register_all_handlers(dp)

    # start
    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


async def congratulation(bot: Bot):
    from sqlalchemy.sql.expression import text
    from time import sleep
    from datetime import datetime

    while True:
        async with bot['config'].db.async_engine.connect() as connection:
            month, day = datetime.now().strftime('%M %d').split()
            query = f'''SELECT * FROM user_data WHERE extract(month from b_date)={month} 
                        AND extract(day from b_date)={day} AND congratulated=false'''
            b_dates = (await connection.execute(text(query))).fetchall()
            for b_date in b_dates:
                await bot.send_message(
                    chat_id=b_date[1],
                    text=f'C др, @{b_date[2]}.'
                )
                query = f"UPDATE user_data SET congratulated=true WHERE tg_chat_id={b_date[1]}"
                await connection.execute(text(query))
            await connection.commit()
        sleep(3)


if __name__ == '__main__':
    from telegram_bot.misc import logging
    logging.setup()

    config = load_config()

    storage = RedisStorage2() if config.tg_bot.use_redis else MemoryStorage()
    bot = Bot(token=config.tg_bot.token, parse_mode=ParseMode.MARKDOWN)
    dp = Dispatcher(bot, storage=storage)
    try:
        run_bot = asyncio.ensure_future(main())
        birthday = asyncio.ensure_future(congratulation(bot))
        loop = asyncio.get_event_loop()
        loop.run_forever()

    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
