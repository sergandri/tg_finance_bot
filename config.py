import os
import logging
from dotenv import load_dotenv

#load_dotenv()
load_dotenv('/app_data/.env')

API_TOKEN = os.getenv('API_TOKEN')
CURRENCY_API = os.getenv('CURRENCY_API')
DATABASE_PATH = os.getenv('DATABASE_PATH', '/app_data/database.sqlite')

if not API_TOKEN:
    raise ValueError("No API_TOKEN provided")

if not CURRENCY_API:
    raise ValueError("No CURRENCY_API key provided")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
