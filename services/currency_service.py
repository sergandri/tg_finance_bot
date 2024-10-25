# services/currency_service.py
import yfinance as yf
import logging
import aiohttp
from config import CURRENCY_TOKEN

logger = logging.getLogger(__name__)

async def convert_currency(amount, currency_from, currency_to):
    ticker = f"{currency_from}{currency_to}=X"
    data = yf.download(tickers=ticker, period='1d', interval='1d')
    if data.empty or 'Close' not in data.columns:
        logger.error(f"Не удалось получить курс для {ticker}")
        raise ValueError("Не удалось получить курс обмена.")
    try:
        rate = data['Close'].iloc[0]
    except IndexError:
        logger.error(f"Нет данных 'Close' для {ticker}")
        raise ValueError("Нет данных для расчета курса.")
    return round(amount * rate, 2)

async def convert_currency_from_openapi(amount, currency_from, currency_to):
    url = 'https://api.freecurrencyapi.com/v1/latest'
    params = {
        'apikey': CURRENCY_TOKEN,
        'base_currency': currency_from,
        'currencies': currency_to
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    logger.error(f"Ошибка при запросе к FreeCurrencyAPI: {response.status}")
                    raise ValueError("Не удалось получить курс обмена.")
                data = await response.json()
                # Проверяем наличие необходимых данных
                if 'data' in data and currency_to in data['data']:
                    rate = data['data'][currency_to]
                    result = round(amount * rate, 2)
                    return result
                else:
                    logger.error("Некорректный ответ от FreeCurrencyAPI")
                    raise ValueError("Не удалось получить курс обмена.")
        except Exception as e:
            logger.exception(f"Ошибка при обращении к FreeCurrencyAPI: {e}")
            raise ValueError("Произошла ошибка при конвертации валюты.")
