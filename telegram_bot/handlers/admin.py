from aiogram import Dispatcher
from aiogram.types import Message
from loguru import logger
from sqlalchemy.sql.expression import text


async def admin_start(message: Message):
    async with message.bot['config'].db.async_engine.connect() as connection:
        query = f"INSERT INTO user_data (tg_chat_id, tg_username, is_admin) VALUES " \
                f"({message.from_user.id}, '{message.from_user.username}', true) ON CONFLICT " \
                f"(tg_chat_id) DO NOTHING"
        await connection.execute(text(query))
        await connection.commit()
    await message.reply('Привет, новый админ!')


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

                query = f"UPDATE user_data set b_date='{b_date}' where tg_username='{tg_username}'"
                try:
                    await connection.execute(text(query))
                except Exception as e:
                    logger.error(f'Update table={table_name}: {e}')
                    break
        await connection.commit()

    await message.reply("Завершено.")


def register_admin(dp: Dispatcher):
    dp.register_message_handler(admin_start, commands=["start"], state="*", is_admin=True)
    dp.register_message_handler(load_b_dates, commands=["b_dates"], state="*", is_admin=True)
