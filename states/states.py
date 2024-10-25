
from aiogram.fsm.state import StatesGroup, State

class CurrencyConversionStates(StatesGroup):
    main_menu = State()
    waiting_for_currency_from = State()
    waiting_for_currency_to = State()
    waiting_for_amount = State()
    waiting_for_history_period = State()
