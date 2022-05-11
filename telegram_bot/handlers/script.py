from aiogram import Dispatcher
from aiogram.types import Message
from sqlalchemy.sql.expression import text as query_text


async def check_b_dates(message: Message):
    from random import randint
    async with message.bot['config'].db.async_engine.connect() as connection:
        query = f"SELECT * FROM congratulation WHERE NOT used"
        texts = (await connection.execute(query_text(query))).fetchall()

        dont_update = False
        if not texts:
            dont_update = True
            texts.append([
                '',
                'Даже не знаю, что написать, готовых текстов нет, так что просто с ДР, @{}!!!',
                'false'
            ])

        i = randint(0, len(texts) - 1)
        text = str(texts[i][1])

        await message.bot.send_message(
            chat_id=message.chat.id,
            text=text.format(message.from_user.username)
        )

        query = f'''
        UPDATE user_data SET congratulated=true WHERE tg_username='{message.from_user.username}'
        '''
        await connection.execute(query_text(query))
        await connection.commit()

        if not dont_update:
            query = f"UPDATE congratulation SET used=true WHERE uid='{texts[i][0]}'"
            await connection.execute(query_text(query))
            await connection.commit()


def register_script(dp: Dispatcher):
    dp.register_message_handler(check_b_dates, chat_type=["crontab"])
