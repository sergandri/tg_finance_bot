import aiohttp
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

BASE_URL = 'https://api.coingecko.com/api/v3'

async def get_crypto_price(crypto_id, vs_currency='usd'):
    url = f'{BASE_URL}/simple/price'
    params = {
        'ids': crypto_id,
        'vs_currencies': vs_currency
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    logger.error(f"Ошибка при запросе к CoinGecko API: {response.status}")
                    raise ValueError("Не удалось получить курс криптовалюты.")
                data = await response.json()
                if crypto_id in data and vs_currency in data[crypto_id]:
                    price = data[crypto_id][vs_currency]
                    return price
                else:
                    logger.error("Некорректный ответ от CoinGecko API")
                    raise ValueError("Не удалось получить курс криптовалюты.")
        except Exception as e:
            logger.exception(f"Ошибка при обращении к CoinGecko API: {e}")
            raise ValueError("Произошла ошибка при получении курса криптовалюты.")

async def get_crypto_price_history(crypto_id, period, vs_currency='usd'):
    period_mapping = {
        "1 день": 1,
        "5 дней": 5,
        "1 месяц": 30
    }
    days = period_mapping.get(period)
    if not days:
        raise ValueError("Некорректный период.")
    url = f'{BASE_URL}/coins/{crypto_id}/market_chart'
    params = {
        'vs_currency': vs_currency,
        'days': days,
        'interval': 'daily'
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    logger.error(f"Ошибка при запросе к CoinGecko API: {response.status}")
                    raise ValueError("Не удалось получить исторические данные криптовалюты.")
                data = await response.json()
                if 'prices' in data:
                    history = []
                    for price_entry in data['prices']:
                        timestamp = price_entry[0] / 1000
                        date_str = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d')
                        price = price_entry[1]
                        history.append(f"{date_str}: {price:.2f} USD")
                    return "\n".join(history)
                else:
                    logger.error("Некорректный ответ от CoinGecko API")
                    raise ValueError("Не удалось получить исторические данные криптовалюты.")
        except Exception as e:
            logger.exception(f"Ошибка при обращении к CoinGecko API: {e}")
            raise ValueError("Произошла ошибка при получении исторических данных криптовалюты.")
