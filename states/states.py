from aiogram.fsm.state import StatesGroup, State


class CurrencyConversionStates(StatesGroup):
    main_menu = State()
    waiting_for_currency_from = State()
    waiting_for_currency_to = State()
    waiting_for_crypto_choice = State()
    waiting_for_rate_type = State()
    waiting_for_currency_pair = State()
    waiting_for_rate_period = State()
    waiting_for_rate_crypto_choice = State()
    waiting_for_rate_period_crypto = State()
