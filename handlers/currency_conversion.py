# handlers/currency_conversion.py
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from states.states import CurrencyConversionStates
from keyboards.keyboards import main_menu_kb, currency_kb, period_kb
from services.currency_service import convert_currency, convert_currency_from_openapi
from database.database import save_conversion, get_previous_requests
import logging

logger = logging.getLogger(__name__)

router = Router()

@router.message(Command("start"))
async def command_start_handler(message: types.Message, state: FSMContext):
    await message.answer(
        "Привет! Я помогу тебе с валютными операциями. Чтобы начать, выбери действие:",
        reply_markup=main_menu_kb()
    )
    await state.set_state(CurrencyConversionStates.main_menu)

@router.message(F.text == "Конвертировать валюту")
async def button_convert_handler(message: types.Message, state: FSMContext):
    await message.answer(
        "Пожалуйста, выберите валюту, которую вы хотите конвертировать:",
        reply_markup=currency_kb()
    )
    await state.set_state(CurrencyConversionStates.waiting_for_currency_from)

@router.message(CurrencyConversionStates.waiting_for_currency_from, F.text != "Назад")
async def currency_from_choice_handler(message: types.Message, state: FSMContext):
    selected_currency_from = message.text.strip().upper()
    valid_currencies = [btn.text for row in currency_kb().keyboard for btn in row]

    if selected_currency_from not in valid_currencies:
        await message.answer("Пожалуйста, выберите корректную валюту для конвертации.")
        return

    await state.update_data(currency_from=selected_currency_from)
    await message.answer(
        f"Вы выбрали {selected_currency_from}. Теперь выберите валюту, в которую вы хотите конвертировать:",
        reply_markup=currency_kb()
    )
    await state.set_state(CurrencyConversionStates.waiting_for_currency_to)

@router.message(CurrencyConversionStates.waiting_for_currency_to, F.text != "Назад")
async def currency_to_choice_handler(message: types.Message, state: FSMContext):
    selected_currency_to = message.text.strip().upper()
    valid_currencies = [btn.text for row in currency_kb().keyboard for btn in row]

    if selected_currency_to not in valid_currencies:
        await message.answer("Пожалуйста, выберите корректную валюту для конвертации.")
        return

    data = await state.get_data()
    if selected_currency_to == data.get('currency_from'):
        await message.answer("Валюта конвертации не может совпадать с исходной валютой.")
        return

    await state.update_data(currency_to=selected_currency_to)
    await message.answer(f"Вы выбрали {selected_currency_to}. Введите сумму для конвертации:")
    await state.set_state(CurrencyConversionStates.waiting_for_amount)

@router.message(CurrencyConversionStates.waiting_for_amount)
async def amount_input_handler(message: types.Message, state: FSMContext):
    input_text = message.text.strip().replace(',', '.')
    if not input_text.replace('.', '', 1).isdigit():
        await message.answer("Пожалуйста, введите корректное число для конвертации.")
        return

    amount = float(input_text)
    data = await state.get_data()
    currency_from = data.get('currency_from')
    currency_to = data.get('currency_to')

    try:
        result_yahoo_finance = await convert_currency(amount, currency_from, currency_to)
        result_free_api = await convert_currency_from_openapi(amount, currency_from, currency_to)

        user_id = message.from_user.id
        await save_conversion(user_id, currency_from, currency_to, amount, result_yahoo_finance, result_free_api)

        await message.answer(
            f"Результаты конвертации:\n"
            f"Yahoo Finance: {amount} {currency_from} = {result_yahoo_finance} {currency_to}\n"
            f"Open API: {amount} {currency_from} = {result_free_api} {currency_to}"
        )
    except Exception as e:
        logger.error(f"Ошибка при конвертации: {e}")
        await message.answer("Произошла ошибка при конвертации валюты. Пожалуйста, попробуйте позже.")
    finally:
        await state.clear()
        await command_start_handler(message, state)

@router.message(F.text == "История конвертаций")
async def history_button_handler(message: types.Message, state: FSMContext):
    await message.answer("Выберите период для просмотра истории конвертаций:", reply_markup=period_kb())
    await state.set_state(CurrencyConversionStates.waiting_for_history_period)

@router.message(CurrencyConversionStates.waiting_for_history_period, F.text != "Назад")
async def history_period_choice_handler(message: types.Message, state: FSMContext):
    period = message.text.strip()
    days_mapping = {
        "1 день": "-1 day",
        "1 неделя": "-7 days",
        "1 месяц": "-30 days"
    }

    if period not in days_mapping:
        await message.answer("Пожалуйста, выберите корректный период.")
        return

    user_id = message.from_user.id
    conversions = await get_previous_requests(user_id, days_mapping[period])

    if conversions:
        history_message = "\n\n".join(
            [f"{row['created_at']}: {row['amount']} {row['currency_from']} = {row['result_yahoo']} {row['currency_to']} (Yahoo Finance)\n"
             f"{row['amount']} {row['currency_from']} = {row['result_openapi']} {row['currency_to']} (Open API)" for row in conversions]
        )
        await message.answer(f"История конвертаций за {period}:\n{history_message}")
    else:
        await message.answer(f"У вас нет конвертаций за {period}.")

    await state.clear()
    await command_start_handler(message, state)

# Обработчик для кнопки "Назад"
@router.message(F.text == "Назад")
async def back_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await command_start_handler(message, state)
