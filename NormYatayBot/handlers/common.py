from aiogram import Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher import FSMContext
from utils import get_exchange_rate
from keyboards import get_main_keyboard
from .start import send_menu  # Относительный импорт из handlers/start.py

async def show_exchange_rate(message: Message):
    exchange_rate = await get_exchange_rate()
    if exchange_rate:
        await message.answer(f"Актуальный курс CNY → RUB: {exchange_rate:.2f}")
    else:
        await message.answer(
            "✖️ Не удалось получить курс валют. Попробуйте позже или обратитесь в техподдержку: @Episthema",
            reply_markup=get_main_keyboard()
        )


async def handle_manager(message: Message):
    key_key = ReplyKeyboardMarkup(resize_keyboard=True)
    key_key.add(KeyboardButton("◶В главное меню"))
    await message.answer(
        "📮 Свяжитесь с менеджером: @promoutermuhamad",
        reply_markup=key_key
    )

async def handle_back(message: Message):
    await send_menu(message)

async def handle_back_state(message: Message, state: FSMContext):
    await state.finish()
    await send_menu(message)

async def handle_help(message: Message):
    await message.answer(
        "☎️ Наша поддержка: @Episthema\nСообщайте об ошибках❗️ Предлагайте новое❗️"
    )

def register_common_handlers(dp: Dispatcher):
    dp.register_message_handler(show_exchange_rate, lambda message: message.text == "Курс💴")
    dp.register_message_handler(handle_manager, lambda message: message.text == 'Написать менеджеру✏️')
    dp.register_message_handler(handle_back, lambda message: message.text == '◶В главное меню')
    dp.register_message_handler(handle_back_state, lambda message: message.text == "/back", state='*')
    dp.register_message_handler(handle_help, lambda message: message.text == '/help_tech')
