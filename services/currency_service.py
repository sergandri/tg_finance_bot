import yfinance as yf
import logging

logger = logging.getLogger(__name__)


async def get_exchange_rate(currency_from: str, currency_to: str) -> float:
    invert_rate = False
    ticker = f"{currency_from}{currency_to}=X"
    data = yf.download(tickers=ticker, period='1d', interval='1d')
    if data.empty or 'Close' not in data.columns:
        # Попробуем обратную пару
        ticker = f"{currency_to}{currency_from}=X"
        data = yf.download(tickers=ticker, period='1d', interval='1d')
        if data.empty or 'Close' not in data.columns:
            logger.error(f"Не удалось получить курс для {currency_from}/{currency_to}")
            raise ValueError("Не удалось получить курс обмена.")
        invert_rate = True
    try:
        rate = data['Close'].iloc[0]
        rate = float(rate)
        if invert_rate:
            rate = 1 / rate
    except (IndexError, ValueError) as e:
        logger.error(f"Ошибка при получении курса: {e}")
        raise ValueError("Нет данных для расчета курса.")
    return round(rate, 6)


async def get_exchange_rate_history(currency_from: str, currency_to: str, period: str) -> str:
    period_mapping = {
        "1 день": "1d",
        "5 дней": "5d",
        "1 месяц": "1mo"
    }
    yf_period = period_mapping.get(period)
    if not yf_period:
        raise ValueError("Некорректный период.")
    ticker = f"{currency_from}{currency_to}=X"
    data = yf.download(tickers=ticker, period=yf_period, interval='1d')
    if data.empty or 'Close' not in data.columns:
        logger.error(f"Не удалось получить исторические данные для {ticker}")
        raise ValueError("Не удалось получить исторические данные курса.")
    history = []
    for date, row in data.iterrows():
        date_str = date.strftime('%Y-%m-%d')
        close_price = float(row['Close'])
        history.append(f"{date_str}: {close_price:.6f}")
    return "\n".join(history)
