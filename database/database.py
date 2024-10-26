# database/database.py

import aiosqlite
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

DB_PATH = 'database/finance_bot.db'

async def init_db(db_path=DB_PATH):
    async with aiosqlite.connect(db_path) as db:
        await db.execute('PRAGMA foreign_keys = ON;')
        # Создание таблицы пользователей
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT
            )
        ''')
        # Создание таблицы истории тикеров
        await db.execute('''
            CREATE TABLE IF NOT EXISTS user_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                ticker_type TEXT,
                ticker TEXT,
                timestamp TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        await db.commit()
        logger.info("База данных инициализирована")

async def save_user(user_id, username, db_path=DB_PATH):
    async with aiosqlite.connect(db_path) as db:
        await db.execute('PRAGMA foreign_keys = ON;')
        await db.execute('''
            INSERT OR IGNORE INTO users (user_id, username)
            VALUES (?, ?)
        ''', (user_id, username))
        await db.commit()

async def save_user_history(user_id, ticker_type, ticker, db_path=DB_PATH):
    async with aiosqlite.connect(db_path) as db:
        await db.execute('PRAGMA foreign_keys = ON;')
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        await db.execute('''
            INSERT INTO user_history (user_id, ticker_type, ticker, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (user_id, ticker_type, ticker, timestamp))
        await db.commit()

async def get_user_history(user_id, db_path=DB_PATH):
    async with aiosqlite.connect(db_path) as db:
        await db.execute('PRAGMA foreign_keys = ON;')
        cursor = await db.execute('''
            SELECT ticker_type, ticker, timestamp FROM user_history
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT 20
        ''', (user_id,))
        rows = await cursor.fetchall()
        await cursor.close()
        history = [{'ticker_type': row[0], 'ticker': row[1], 'timestamp': row[2]} for row in rows]
        return history
