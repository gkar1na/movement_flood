import asyncio
from sqlalchemy.ext.asyncio.engine import create_async_engine
import requests
from sqlalchemy.sql.expression import text
from datetime import datetime
import pytz
from data.config import settings


async def congratulation():
    db_url = f'''
    postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}/{settings.DB_NAME}
    '''

    engine = create_async_engine(db_url)
    async with engine.connect() as connection:
        month, day = datetime.now(tz=pytz.timezone('Europe/Moscow')).strftime('%m %d').split()
        query = f'''SELECT * FROM user_data WHERE extract(month from b_date)={month} 
                    AND extract(day from b_date)={day} AND congratulated=false'''
        b_dates = (await connection.execute(text(query))).fetchall()
        query = f'''
        SELECT chat_id FROM group_chat WHERE is_verified
        '''
        chats_id = (await connection.execute(text(query))).fetchall()

        for b_date in b_dates:
            for chat_id in chats_id:
                r = requests.post(settings.WEBHOOK_URL, json={
                    "message": {
                        "from": {
                            "username": b_date[2],
                        },
                        "chat": {
                            "id": int(chat_id[0]),
                            "type": "crontab"
                        },
                        "text": "/check_b_dates",
                    }
                })


if __name__ == '__main__':
    try:
        asyncio.run(congratulation())

    except Exception as e:
        print(e)
