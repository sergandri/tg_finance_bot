# database/database.py
import aiosqlite
import logging

logger = logging.getLogger(__name__)

DB_PATH = 'database/conversions.db'

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS conversions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                currency_from TEXT,
                currency_to TEXT,
                amount REAL,
                result_yahoo REAL,
                result_openapi REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.commit()
        logger.info("База данных инициализирована")

async def save_conversion(user_id, currency_from, currency_to, amount, result_yahoo, result_openapi):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT INTO conversions (user_id, currency_from, currency_to, amount, result_yahoo, result_openapi)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, currency_from, currency_to, amount, result_yahoo, result_openapi))
        await db.commit()
        logger.info("Конвертация сохранена в базе данных")

async def get_previous_requests(user_id, period):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(f'''
            SELECT currency_from, currency_to, amount, result_yahoo, result_openapi, created_at 
            FROM conversions 
            WHERE user_id = ? AND created_at >= datetime('now', ?) 
            ORDER BY created_at DESC
        ''', (user_id, period))
        rows = await cursor.fetchall()
    return [{
        'currency_from': row[0],
        'currency_to': row[1],
        'amount': row[2],
        'result_yahoo': row[3],
        'result_openapi': row[4],
        'created_at': row[5]
    } for row in rows]
