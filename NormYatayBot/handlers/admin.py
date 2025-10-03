import sqlite3

from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from config import PASSWORD, CODE
from keyboards import re_keyboard, inline_back, re_opt4, re_opt2, re_opt3, re_delall, promo_type_keyboard, \
    create_pagination_keyboard, re_reklama
from states import Form, AdminActions, PromoCodeStates, SearchStates
from database import get_all_promo_codes, add_promo_code, delete_promo_code, get_user_info, get_all_users, \
    get_total_users, clear_database, get_user_orders, cursor
from datetime import datetime
import logging

admin_pagination = {}

async def cmd_admin(message: Message, state: FSMContext):
    msg = await message.reply("Введите пароль для активации:")
    await state.update_data(last_message_id=msg.message_id)
    await Form.admin.set()

async def process_password(message: Message, state: FSMContext):
    user_data = await state.get_data()
    last_message_id = user_data.get('last_message_id')

    if message.text == PASSWORD:
        await message.answer('Добро пожаловать в админ панель!', reply_markup=re_keyboard)
        if last_message_id:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=last_message_id)
            except Exception as e:
                logging.error(f"Ошибка при удалении сообщения с запросом пароля: {e}")
        try:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения с паролем: {e}")
    else:
        await message.answer("Неверный пароль. Снова выберите /admin или /start")
        if last_message_id:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=last_message_id)
            except Exception as e:
                logging.error(f"Ошибка при удалении сообщения с запросом пароля: {e}")
    await state.finish()

async def process_exit(callback_query: CallbackQuery):
    await callback_query.message.bot.edit_message_text(
        text="Вы вышли из меню. Используйте /start",
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=None
    )

async def process_back(callback_query: CallbackQuery):
    await callback_query.message.bot.edit_message_text(
        text="Добро пожаловать в админ панель!",
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=re_keyboard
    )

async def process_admin_menu(callback_query: CallbackQuery):
    await callback_query.message.bot.answer_callback_query(callback_query.id)
    button_data = callback_query.data
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id

    if button_data == 'opt1':
        today = datetime.now().date()
        cursor.execute("SELECT COUNT(*) FROM users WHERE DATE(first_seen) = ?", (today,))
        new_today = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM users WHERE first_seen >= DATE('now', '-30 days')")
        new_month = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM users WHERE DATE(last_active) = ?", (today,))
        active_today = cursor.fetchone()[0]

        stats_text = (
            "📊 Статистика по пользователям:\n"
            f"👥 Новых пользователей за день: {new_today}\n"
            f"👥 Новых пользователей за месяц: {new_month}\n"
            f"👥 Всего пользователей: {total_users}\n\n"
            f"👥 Активных сегодня: {active_today}"
        )

        await callback_query.message.bot.edit_message_text(
            text=stats_text,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=inline_back
        )
    elif button_data == 'opt2':
        await callback_query.message.bot.edit_message_text(
            text="Меню управления промокодами:",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=re_opt2
        )
    elif button_data == 'opt3':
        await callback_query.message.bot.edit_message_text(
            text="Пробей пользователя по ID:",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=re_opt3
        )
    elif button_data == 'opt4':
        await callback_query.message.bot.edit_message_text(
            text="Управление базой данных:",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=re_opt4
        )
    elif button_data == 'opt5':
        await callback_query.message.bot.edit_message_text(
            text="Управление рекламой в боте:",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=re_reklama
        )

async def process_delete_all(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.bot.answer_callback_query(callback_query.id)
    await callback_query.message.bot.edit_message_text(
        text="⚠️ Введите код доступа для очистки базы данных:",
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id
    )
    await AdminActions.waiting_for_delete_code.set()
    await state.update_data(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id
    )

async def process_delete_code(message: Message, state: FSMContext):
    user_data = await state.get_data()
    chat_id = user_data['chat_id']
    message_id = user_data['message_id']
    try:
        await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except Exception as e:
        logging.error(f"Ошибка при удалении сообщения с кодом: {e}")

    if message.text == CODE:
        clear_database()
        await message.bot.edit_message_text(
            text="✅ База данных успешно очищена!",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=inline_back
        )
    else:
        await message.bot.edit_message_text(
            text="❌ Неверный код доступа! Очистка отменена.",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=inline_back
        )
    await state.finish()

async def process_promo_menu(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id

    if callback_query.data == 'allpromo':
        promo_codes = get_all_promo_codes()
        if not promo_codes:
            text = "📋 Список промокодов пуст"
        else:
            text = "📋 Список промокодов:\n\n"
            for code, discount, max_uses, uses_left in promo_codes:
                text += f"Код: {code}\nСкидка: {discount if discount > 0 else 'Услуга 0 RUB'}%\nМакс. использований: {max_uses}\nОсталось: {uses_left}\n\n"

        await callback_query.message.bot.edit_message_text(
            text=text,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=inline_back
        )
    elif callback_query.data == 'addpromo':
        await callback_query.message.bot.edit_message_text(
            text="Введите новый промокод (например, SAVE20):",
            chat_id=chat_id,
            message_id=message_id
        )
        await PromoCodeStates.waiting_for_new_promo.set()
        await state.update_data(chat_id=chat_id, message_id=message_id)
    elif callback_query.data == 'deletepromo':
        await callback_query.message.bot.edit_message_text(
            text="Введите промокод для удаления:",
            chat_id=chat_id,
            message_id=message_id
        )
        await PromoCodeStates.waiting_for_delete_promo.set()
        await state.update_data(chat_id=chat_id, message_id=message_id)

async def process_new_promo_code(message: Message, state: FSMContext):
    user_data = await state.get_data()
    chat_id = user_data['chat_id']
    message_id = user_data['message_id']
    promo_code = message.text.strip()

    try:
        await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except Exception as e:
        logging.error(f"Ошибка при удалении сообщения: {e}")

    if not promo_code.isalnum() or len(promo_code) < 3:
        await message.bot.edit_message_text(
            text="Промокод должен содержать только буквы и цифры и быть длиной не менее 3 символов!",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=inline_back
        )
        await state.finish()
        return

    cursor.execute("SELECT code FROM promo_codes WHERE code = ?", (promo_code,))
    if cursor.fetchone():
        await message.bot.edit_message_text(
            text=f"❌ Промокод '{promo_code}' уже существует!",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=inline_back
        )
        await state.finish()
        return

    await state.update_data(promo_code=promo_code)
    await PromoCodeStates.waiting_for_promo_type.set()
    await message.bot.edit_message_text(
        text="Выберите тип промокода:",
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=promo_type_keyboard
    )

async def process_promo_type(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.bot.answer_callback_query(callback_query.id)
    user_data = await state.get_data()
    chat_id = user_data['chat_id']
    message_id = user_data['message_id']
    promo_code = user_data['promo_code']

    if callback_query.data == 'percent_promo':
        await PromoCodeStates.waiting_for_promo_details.set()
        await callback_query.message.bot.edit_message_text(
            text="Введите детали промокода в формате:\n<процент скидки> <макс. использований>\nНапример: 10 50",
            chat_id=chat_id,
            message_id=message_id
        )
    elif callback_query.data == 'service_promo':
        await PromoCodeStates.waiting_for_service_promo_uses.set()
        await callback_query.message.bot.edit_message_text(
            text="Введите максимальное количество использований для промокода со скидкой на услугу:",
            chat_id=chat_id,
            message_id=message_id
        )
    elif callback_query.data == 'cancel_promo':
        await callback_query.message.bot.edit_message_text(
            text="Добавление промокода отменено",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=inline_back
        )
        await state.finish()

async def process_promo_details(message: Message, state: FSMContext):
    user_data = await state.get_data()
    chat_id = user_data['chat_id']
    message_id = user_data['message_id']
    promo_code = user_data['promo_code']

    try:
        await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except Exception as e:
        logging.error(f"Ошибка при удалении сообщения: {e}")

    try:
        discount, max_uses = map(float, message.text.split())
        if discount < 0 or max_uses < 0:
            raise ValueError

        add_promo_code(promo_code, discount, int(max_uses))
        await message.bot.edit_message_text(
            text=f"✅ Промокод '{promo_code}' успешно добавлен!\nСкидка: {discount}%\nИспользований: {int(max_uses)}",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=inline_back
        )
    except (ValueError, sqlite3.Error) as e:
        logging.error(f"Ошибка при добавлении промокода: {e}")
        await message.bot.edit_message_text(
            text="❌ Ошибка! Введите корректные данные в формате: <процент> <количество>",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=inline_back
        )
    await state.finish()

async def process_service_promo_uses(message: Message, state: FSMContext):
    user_data = await state.get_data()
    chat_id = user_data['chat_id']
    message_id = user_data['message_id']
    promo_code = user_data['promo_code']

    try:
        await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except Exception as e:
        logging.error(f"Ошибка при удалении сообщения: {e}")

    try:
        max_uses = int(message.text.strip())
        if max_uses <= 0:
            raise ValueError
        add_promo_code(promo_code, 0.0, max_uses)
        await message.bot.edit_message_text(
            text=f"✅ Промокод '{promo_code}' успешно добавлен!\nСкидка: Услуга 0 RUB\nИспользований: {max_uses}",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=inline_back
        )
    except (ValueError, sqlite3.Error) as e:
        logging.error(f"Ошибка при добавлении сервисного промокода: {e}")
        await message.bot.edit_message_text(
            text="❌ Ошибка! Введите корректное положительное число использований",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=inline_back
        )
    await state.finish()

async def process_delete_promo(message: Message, state: FSMContext):
    user_data = await state.get_data()
    chat_id = user_data['chat_id']
    message_id = user_data['message_id']
    promo_code = message.text.strip()

    try:
        await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except Exception as e:
        logging.error(f"Ошибка при удалении сообщения: {e}")

    cursor.execute("SELECT code FROM promo_codes WHERE code = ?", (promo_code,))
    if cursor.fetchone():
        delete_promo_code(promo_code)
        await message.bot.edit_message_text(
            text=f"✅ Промокод '{promo_code}' успешно удален!",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=inline_back
        )
    else:
        await message.bot.edit_message_text(
            text=f"❌ Промокод '{promo_code}' не найден!",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=inline_back
        )
    await state.finish()

async def process_id_menu(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id
    admin_id = callback_query.from_user.id

    if callback_query.data == 'allid' or callback_query.data.startswith('prev_page_') or callback_query.data.startswith('next_page_'):
        if callback_query.data == 'allid':
            current_page = 0
        elif callback_query.data.startswith('prev_page_'):
            current_page = int(callback_query.data.split('_')[2]) - 1
        elif callback_query.data.startswith('next_page_'):
            current_page = int(callback_query.data.split('_')[2]) + 1
        else:
            current_page = admin_pagination.get(admin_id, 0)

        admin_pagination[admin_id] = current_page
        total_users = get_total_users()
        total_pages = (total_users + 4) // 5
        offset = current_page * 5
        users = get_all_users(offset=offset, limit=5)

        if not users:
            text = "📋 Список пользователей пуст"
        else:
            text = f"📋 Список зарегистрированных ID (Страница {current_page + 1} из {total_pages}):\n\n"
            for user_id, first_seen, last_active in users:
                text += f"ID: {user_id}\nПервый вход: {first_seen}\nПоследняя активность: {last_active}\n\n"

        await callback_query.message.bot.edit_message_text(
            text=text,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=create_pagination_keyboard(current_page, total_pages)
        )
    elif callback_query.data == 'search':
        await callback_query.message.bot.edit_message_text(
            text="Введите ID пользователя для поиска:",
            chat_id=chat_id,
            message_id=message_id
        )
        await SearchStates.waiting_for_id.set()
        await state.update_data(chat_id=chat_id, message_id=message_id)

async def process_id_search(message: Message, state: FSMContext):
    user_data = await state.get_data()
    chat_id = user_data['chat_id']
    message_id = user_data['message_id']

    try:
        await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except Exception as e:
        logging.error(f"Ошибка при удалении сообщения: {e}")

    try:
        search_id = int(message.text.strip())
        user = get_user_info(search_id)

        if user:
            orders = get_user_orders(search_id)
            text = (
                f"ℹ️ Информация о пользователе {search_id}:\n"
                f"Первый вход: {user[1]}\n"
                f"Последняя активность: {user[2]}\n\n"
                f"Заявки ({len(orders)}):\n"
            )

            if orders:
                for order in orders:
                    text += (
                        f"📍 ID заявки: {order[0]}\n"
                        f"📍 Тип доставки: {order[1]}\n"
                        f"📍 Товар: {order[2]}\n"
                        f"📍 Контактные данные: {order[3]}\n"
                        f"📍 Стоимость товара: {order[4]} CNY\n"
                        f"📍 Вес: {order[5] if order[5] else 'Не указан'}\n"
                        f"📍 Общая стоимость: {order[6]} RUB\n"
                        f"📍 Промокод: {order[7] if order[7] else 'Не использован'}\n"
                        f"📍 Скидка: {order[8]}%\n\n"
                    )
            else:
                text += "Заявок пока нет\n"
        else:
            text = f"❌ Пользователь с ID {search_id} не найден!"

        await message.bot.edit_message_text(
            text=text,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=inline_back
        )
    except ValueError:
        await message.bot.edit_message_text(
            text="❌ Введите корректный числовой ID!",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=inline_back
        )
    except sqlite3.Error as e:
        logging.error(f"Ошибка при поиске пользователя: {e}")
        await message.bot.edit_message_text(
            text="❌ Ошибка при поиске пользователя!",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=inline_back
        )
    await state.finish()

def register_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_admin, lambda message: message.text == '/admin')
    dp.register_message_handler(process_password, state=Form.admin)
    dp.register_callback_query_handler(process_exit, lambda c: c.data == 'exit')
    dp.register_callback_query_handler(process_back, lambda c: c.data == 'back')
    dp.register_callback_query_handler(process_admin_menu, lambda c: c.data in ['opt1', 'opt2', 'opt3', 'opt4', 'opt5'])
    dp.register_callback_query_handler(process_delete_all, lambda c: c.data == 'deleteall')
    dp.register_message_handler(process_delete_code, state=AdminActions.waiting_for_delete_code)
    dp.register_callback_query_handler(process_promo_menu, lambda c: c.data in ['allpromo', 'addpromo', 'deletepromo'])
    dp.register_message_handler(process_new_promo_code, state=PromoCodeStates.waiting_for_new_promo)
    dp.register_callback_query_handler(process_promo_type, lambda c: c.data in ['percent_promo', 'service_promo', 'cancel_promo'], state=PromoCodeStates.waiting_for_promo_type)
    dp.register_message_handler(process_promo_details, state=PromoCodeStates.waiting_for_promo_details)
    dp.register_message_handler(process_service_promo_uses, state=PromoCodeStates.waiting_for_service_promo_uses)
    dp.register_message_handler(process_delete_promo, state=PromoCodeStates.waiting_for_delete_promo)
    dp.register_callback_query_handler(process_id_menu, lambda c: c.data in ['allid', 'search'] or c.data.startswith('prev_page_') or c.data.startswith('next_page_'))
    dp.register_message_handler(process_id_search, state=SearchStates.waiting_for_id)