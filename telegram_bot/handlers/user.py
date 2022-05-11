from aiogram import Dispatcher
from aiogram.types import Message
from sqlalchemy.sql.expression import text


async def user_start(message: Message):
    async with message.bot['config'].db.async_engine.connect() as connection:
        query = f"INSERT INTO user_data (tg_chat_id, tg_username) VALUES " \
                f"({message.from_user.id}, '{message.from_user.username}') ON CONFLICT " \
                f"(tg_chat_id) DO NOTHING"
        await connection.execute(text(query))
        await connection.commit()
    await message.reply("Привет, пользователь!")


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start"], state="*", is_admin=False)
