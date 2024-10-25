import os
import logging
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv('API_TOKEN')
CURRENCY_API = os.getenv('CURRENCY_API')

if not API_TOKEN:
    raise ValueError("No API_TOKEN provided")

if not CURRENCY_API:
    raise ValueError("No CURRENCY_API key provided")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
