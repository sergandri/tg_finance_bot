from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Курс валют")],
            [KeyboardButton(text="Курс криптовалют")],
            [KeyboardButton(text="Динамика курса")],
            [KeyboardButton(text="Назад")]
        ],
        resize_keyboard=True
    )

def currency_kb():
    currencies = ["USD", "EUR", "RUB", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY",
                  "HKD", "NZD", "SEK", "SGD", "NOK", "MXN"]
    buttons = [KeyboardButton(text=currency) for currency in currencies]
    buttons.append(KeyboardButton(text="Назад"))
    return ReplyKeyboardMarkup(
        keyboard=[buttons[i:i+3] for i in range(0, len(buttons), 3)],
        resize_keyboard=True
    )

def currency_pairs_kb():
    pairs = ["USD/EUR", "USD/RUB", "EUR/GBP", "USD/JPY", "AUD/CAD"]
    buttons = [KeyboardButton(text=pair) for pair in pairs]
    buttons.append(KeyboardButton(text="Назад"))
    return ReplyKeyboardMarkup(
        keyboard=[[btn] for btn in buttons],
        resize_keyboard=True
    )

def period_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="1 день")],
            [KeyboardButton(text="5 дней")],
            [KeyboardButton(text="1 месяц")],
            [KeyboardButton(text="Назад")]
        ],
        resize_keyboard=True
    )


def crypto_kb():
    cryptos = ["Bitcoin", "Ethereum", "Litecoin", "Ripple", "Dogecoin"]
    buttons = [KeyboardButton(text=crypto) for crypto in cryptos]
    buttons.append(KeyboardButton(text="Назад"))
    return ReplyKeyboardMarkup(
        keyboard=[buttons[i:i+2] for i in range(0, len(buttons), 2)],
        resize_keyboard=True
    )
