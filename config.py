import logging
import os
from dotenv import load_dotenv

from pathlib import Path
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

BOT_API_TOKEN = os.getenv("BOT_API_TOKEN")
CURRENCY_TOKEN = os.getenv("CURRENCY_TOKEN")

logger = logging.getLogger(__name__)

# Проверка наличия API_TOKEN
if not BOT_API_TOKEN:
    err_msg = "BOT_API_TOKEN не установлен в переменных окружения"
    logger.error(err_msg)
    raise ValueError(err_msg)
else:
    logger.info("BOT_API_TOKEN успешно загружен.")


