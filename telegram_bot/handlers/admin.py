from aiogram import Dispatcher
from aiogram.types import Message
from loguru import logger
from sqlalchemy.sql.expression import text
from aiogram.dispatcher.webhook import SendMessage


async def admin_start(message: Message):
    async with message.bot['config'].db.async_engine.connect() as connection:
        query = f'''
        INSERT INTO user_data (tg_chat_id, tg_username, is_admin) VALUES 
        ({message.from_user.id}, '{message.from_user.username}', true) 
        ON CONFLICT (tg_username) DO UPDATE SET is_admin=true, tg_chat_id={message.from_user.id}
        '''
        await connection.execute(text(query))
        await connection.commit()

    return SendMessage(message.from_user.id, 'Привет, новый админ!')


async def read_sheet(message: Message) -> dict:
    from googleapiclient.discovery import build

    tables = dict()
    creds = message.bot['config'].sheet.credentials
    service = build('sheets', 'v4', credentials=creds, cache_discovery=False)
    request = service.spreadsheets().get(
        spreadsheetId=message.bot['config'].sheet.spreadsheet_id,
        includeGridData=True
    )
    response = request.execute()
    sheets = response['sheets']
    for sheet in sheets:
        sheet_title = sheet['properties']['title']
        tables[sheet_title] = []
        rowData = sheet['data']
        for k, data in enumerate(rowData):
            if 'rowData' not in data.keys():
                continue
            rowData[k] = rowData[k]['rowData']
            for i, row in enumerate(rowData[k]):
                if 'values' in row.keys():
                    for j, value in enumerate(row['values']):
                        if value and 'formattedValue' in value.keys():
                            row['values'][j] = value['formattedValue']
                        else:
                            row['values'][j] = None
                    tables[sheet_title].append(row['values'])
                else:
                    tables[sheet_title].append(None)

    return tables


async def load_b_dates(message: Message):
    tables = await read_sheet(message)

    engine = message.bot['config'].db.async_engine
    async with engine.connect() as connection:
        for table_name in tables.keys():
            if not tables[table_name]:
                continue
            rows = tables[table_name][1:]
            columns = list(tables[table_name][0])
            try:
                b_date_column = columns.index('Когда у тебя день рождения? (dd.mm.yyyy)')
                tg_username_column = columns.index('Твой ник в телеге (без @)')
            except ValueError as e:
                continue
            for row in rows:
                b_date = row[b_date_column]
                tg_username = row[tg_username_column]
                if b_date is None or tg_username is None:
                    continue

                query = f'''
                INSERT INTO user_data (tg_username, b_date) VALUES ('{tg_username}', '{b_date}') 
                ON CONFLICT (tg_username) DO UPDATE SET b_date='{b_date}'
                '''
                try:
                    await connection.execute(text(query))
                except Exception as e:
                    logger.error(f'Update table={table_name}: {e}')
                    break
        await connection.commit()

    await message.reply("Завершено.")


from aiogram.types import ChatMemberUpdated


async def new_group_chat(chat_updated: ChatMemberUpdated):
    member_id = chat_updated.new_chat_member.user.id
    from_id = chat_updated.from_user.id
    if (member_id != chat_updated.bot['config'].tg_bot.chat_id or
            from_id not in chat_updated.bot['config'].tg_bot.admin_ids):
        return

    chat_id = chat_updated.chat.id
    chat_name = chat_updated.chat.title

    status = chat_updated.new_chat_member.status

    engine = chat_updated.bot['config'].db.async_engine
    async with engine.connect() as connection:
        if status == 'left':
            query = f"DELETE FROM group_chat WHERE chat_id={chat_id}"
        elif status == 'member':
            query = f"INSERT INTO group_chat (chat_id, chat_name) VALUES ({chat_id}, '{chat_name}')"

        await connection.execute(text(query))
        await connection.commit()


async def verify_group_chat(message: Message):
    chat_id = message.chat.id
    query = f"UPDATE group_chat SET is_verified=true WHERE chat_id={chat_id}"
    engine = message.bot['config'].db.async_engine
    async with engine.connect() as connection:
        await connection.execute(text(query))
        await connection.commit()
    await message.reply('Теперь здесь будут поздравления.')


async def deverify_froup_chat(message: Message):
    chat_id = message.chat.id
    query = f"UPDATE group_chat SET is_verified=false WHERE chat_id={chat_id}"
    engine = message.bot['config'].db.async_engine
    async with engine.connect() as connection:
        await connection.execute(text(query))
        await connection.commit()
    await message.reply('Больше поздравлений не будет.')


def register_admin(dp: Dispatcher):
    dp.register_message_handler(admin_start, commands=["start"], state="*", is_admin=True)
    dp.register_message_handler(load_b_dates, commands=["b_dates"], state="*", is_admin=True)
    dp.register_message_handler(verify_group_chat, commands=["verify"], state="*", is_admin=True)
    dp.register_message_handler(deverify_froup_chat, commands=["deverify"], is_admin=True)
    dp.register_my_chat_member_handler(new_group_chat)
