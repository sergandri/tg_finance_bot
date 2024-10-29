from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from states.states import CurrencyConversionStates
from keyboards.keyboards import main_menu_kb, currency_kb, period_kb, crypto_kb, currency_pairs_kb
from services.currency_service import get_exchange_rate, get_exchange_rate_history
from services.crypto_service import get_crypto_price, get_crypto_price_history
from database.database import save_user, save_user_history
import logging

logger = logging.getLogger(__name__)

router = Router()

@router.message(Command("start"))
async def command_start_handler(message: types.Message, state: FSMContext):
    await save_user(message.from_user.id, message.from_user.username)
    await message.answer(
        "Привет! Я помогу тебе с получением курсов валют и криптовалют. Чтобы начать, выбери действие:",
        reply_markup=main_menu_kb()
    )
    await state.set_state(CurrencyConversionStates.main_menu)

@router.message(F.text == "Курс валют")
async def button_exchange_rate_handler(message: types.Message, state: FSMContext):
    await message.answer(
        "Пожалуйста, выберите валюту, из которой вы хотите узнать курс:",
        reply_markup=currency_kb()
    )
    await state.set_state(CurrencyConversionStates.waiting_for_currency_from)

@router.message(CurrencyConversionStates.waiting_for_currency_from, F.text != "Назад")
async def currency_from_choice_handler(message: types.Message, state: FSMContext):
    selected_currency_from = message.text.strip().upper()
    valid_currencies = [btn.text for row in currency_kb().keyboard for btn in row if btn.text != "Назад"]
    if selected_currency_from not in valid_currencies:
        await message.answer("Пожалуйста, выберите корректную валюту.")
        return
    await state.update_data(currency_from=selected_currency_from)
    await message.answer(
        f"Вы выбрали {selected_currency_from}. Теперь выберите валюту, к которой вы хотите узнать курс:",
        reply_markup=currency_kb()
    )
    await state.set_state(CurrencyConversionStates.waiting_for_currency_to)

@router.message(CurrencyConversionStates.waiting_for_currency_to, F.text != "Назад")
async def currency_to_choice_handler(message: types.Message, state: FSMContext):
    selected_currency_to = message.text.strip().upper()
    valid_currencies = [btn.text for row in currency_kb().keyboard for btn in row if btn.text != "Назад"]
    if selected_currency_to not in valid_currencies:
        await message.answer("Пожалуйста, выберите корректную валюту.")
        return
    data = await state.get_data()
    currency_from = data.get('currency_from')
    if selected_currency_to == currency_from:
        await message.answer("Валюты не должны совпадать. Пожалуйста, выберите другую валюту.")
        return
    try:
        rate = await get_exchange_rate(currency_from, selected_currency_to)
        rate_str = f"{rate:.6f}"
        await message.answer(f"Текущий курс {currency_from}/{selected_currency_to}: {rate_str}")

        ticker = f"{currency_from}/{selected_currency_to}"
        await save_user_history(message.from_user.id, 'currency', ticker)

    except Exception as e:
        logger.error(f"Ошибка при получении курса: {e}")
        await message.answer("Произошла ошибка при получении курса. Пожалуйста, попробуйте позже.")
    finally:
        await state.clear()
        await command_start_handler(message, state)

@router.message(F.text == "Курс криптовалют")
async def crypto_price_start(message: types.Message, state: FSMContext):
    await message.answer(
        "Пожалуйста, выберите криптовалюту для получения текущего курса:",
        reply_markup=crypto_kb()
    )
    await state.set_state(CurrencyConversionStates.waiting_for_crypto_choice)

@router.message(CurrencyConversionStates.waiting_for_crypto_choice, F.text != "Назад")
async def crypto_choice_handler(message: types.Message, state: FSMContext):
    selected_crypto = message.text.strip().lower()
    valid_cryptos = [btn.text.lower() for row in crypto_kb().keyboard for btn in row if btn.text != "Назад"]
    if selected_crypto not in valid_cryptos:
        await message.answer("Пожалуйста, выберите корректную криптовалюту.")
        return
    crypto_ids = {
        'bitcoin': 'bitcoin',
        'ethereum': 'ethereum',
        'litecoin': 'litecoin',
        'ripple': 'ripple',
        'dogecoin': 'dogecoin'
    }
    crypto_id = crypto_ids.get(selected_crypto)
    try:
        price = await get_crypto_price(crypto_id)
        price_str = f"{price:.2f}"
        await message.answer(f"Текущая цена {selected_crypto.capitalize()}: {price_str} USD")
        await save_user_history(message.from_user.id, 'crypto', selected_crypto.capitalize())
    except Exception as e:
        logger.error(f"Ошибка при получении курса криптовалюты: {e}")
        await message.answer("Произошла ошибка при получении курса криптовалюты. Пожалуйста, попробуйте позже.")
    finally:
        await state.clear()
        await command_start_handler(message, state)

@router.message(F.text == "Динамика курса")
async def rate_dynamics_start(message: types.Message, state: FSMContext):
    await message.answer(
        "Пожалуйста, выберите тип курса:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Валюта"), KeyboardButton(text="Криптовалюта")],
                [KeyboardButton(text="Назад")]
            ],
            resize_keyboard=True
        )
    )
    await state.set_state(CurrencyConversionStates.waiting_for_rate_type)

@router.message(CurrencyConversionStates.waiting_for_rate_type)
async def rate_type_choice_handler(message: types.Message, state: FSMContext):
    selected_type = message.text.strip().lower()
    if selected_type == "валюта":
        await message.answer(
            "Пожалуйста, выберите валютную пару:",
            reply_markup=currency_pairs_kb()
        )
        await state.set_state(CurrencyConversionStates.waiting_for_currency_pair)
    elif selected_type == "криптовалюта":
        await message.answer(
            "Пожалуйста, выберите криптовалюту:",
            reply_markup=crypto_kb()
        )
        await state.set_state(CurrencyConversionStates.waiting_for_rate_crypto_choice)
    elif selected_type == "Назад":
        await back_handler(message, state)
    else:
        await message.answer("Пожалуйста, выберите 'Валюта' или 'Криптовалюта'.")

@router.message(CurrencyConversionStates.waiting_for_currency_pair, F.text != "Назад")
async def currency_pair_handler(message: types.Message, state: FSMContext):
    selected_pair = message.text.strip().upper()
    valid_pairs = [btn.text for row in currency_pairs_kb().keyboard for btn in row if btn.text != "Назад"]
    if selected_pair not in valid_pairs:
        await message.answer("Пожалуйста, выберите корректную валютную пару.")
        return
    await state.update_data(currency_pair=selected_pair)
    await message.answer(
        "Выберите период для получения динамики курса:",
        reply_markup=period_kb()
    )
    await state.set_state(CurrencyConversionStates.waiting_for_rate_period)


@router.message(CurrencyConversionStates.waiting_for_rate_period, F.text != "Назад")
async def rate_period_choice_handler(message: types.Message, state: FSMContext):
    period = message.text.strip()
    valid_periods = ["1 день", "5 дней", "1 месяц"]
    if period not in valid_periods:
        await message.answer("Пожалуйста, выберите корректный период.")
        return
    data = await state.get_data()
    currency_pair = data.get('currency_pair')
    currency_from, currency_to = currency_pair.split('/')
    try:
        rate_history = await get_exchange_rate_history(currency_from, currency_to, period)
        history_message = f"Динамика курса {currency_pair} за {period}:\n\n{rate_history}"
        await message.answer(history_message)

        await save_user_history(message.from_user.id, 'currency', currency_pair)
    except Exception as e:
        logger.error(f"Ошибка при получении динамики курса валют: {e}")
        await message.answer("Произошла ошибка при получении динамики курса валют. Пожалуйста, попробуйте позже.")
    finally:
        await state.clear()
        await command_start_handler(message, state)


@router.message(CurrencyConversionStates.waiting_for_rate_crypto_choice, F.text != "Назад")
async def rate_crypto_choice_handler(message: types.Message, state: FSMContext):
    selected_crypto = message.text.strip().lower()
    valid_cryptos = [btn.text.lower() for row in crypto_kb().keyboard for btn in row if btn.text != "Назад"]
    if selected_crypto not in valid_cryptos:
        await message.answer("Пожалуйста, выберите корректную криптовалюту.")
        return
    crypto_ids = {
        'bitcoin': 'bitcoin',
        'ethereum': 'ethereum',
        'litecoin': 'litecoin',
        'ripple': 'ripple',
        'dogecoin': 'dogecoin'
    }
    crypto_id = crypto_ids.get(selected_crypto)
    await state.update_data(crypto_id=crypto_id, selected_crypto=selected_crypto.capitalize())
    await message.answer(
        "Пожалуйста, выберите период для получения динамики курса:",
        reply_markup=period_kb()
    )
    await state.set_state(CurrencyConversionStates.waiting_for_rate_period_crypto)


@router.message(CurrencyConversionStates.waiting_for_rate_period_crypto, F.text != "Назад")
async def rate_crypto_period_choice_handler(message: types.Message, state: FSMContext):
    period = message.text.strip()
    valid_periods = ["1 день", "5 дней", "1 месяц"]
    if period not in valid_periods:
        await message.answer("Пожалуйста, выберите корректный период.")
        return
    data = await state.get_data()
    crypto_id = data.get('crypto_id')
    selected_crypto = data.get('selected_crypto')
    try:
        rate_history = await get_crypto_price_history(crypto_id, period)
        history_message = f"Динамика курса {selected_crypto} за {period}:\n\n{rate_history}"
        await message.answer(history_message)

        await save_user_history(message.from_user.id, 'crypto', selected_crypto)
    except Exception as e:
        logger.error(f"Ошибка при получении динамики курса криптовалюты: {e}")
        await message.answer("Произошла ошибка при получении динамики курса криптовалюты. Пожалуйста, попробуйте позже.")
    finally:
        await state.clear()
        await command_start_handler(message, state)


@router.message(F.text == "Назад")
async def back_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await command_start_handler(message, state)
