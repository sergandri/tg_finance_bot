# keyboards/keyboards.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Конвертировать валюту")],
            [KeyboardButton(text="История конвертаций")]
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

def period_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="1 день")],
            [KeyboardButton(text="1 неделя")],
            [KeyboardButton(text="1 месяц")],
            [KeyboardButton(text="Назад")]
        ],
        resize_keyboard=True
    )
