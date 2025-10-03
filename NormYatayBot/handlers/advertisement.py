from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from states import reklama
from keyboards import re_reklama, skip_link_keyboard, skip_image_keyboard, broadcast_keyboard, create_ad_keyboard
from database import get_all_users
import asyncio
import logging

async def process_text(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.bot.answer_callback_query(callback_query.id)
    await callback_query.message.bot.edit_message_text(
        text="Введите текст рекламного поста:",
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id
    )
    await reklama.text_reklama.set()
    await state.update_data(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        messages_to_delete=[callback_query.message.message_id]
    )

async def process_ad_text(message: Message, state: FSMContext):
    user_data = await state.get_data()
    chat_id = user_data['chat_id']
    message_id = user_data['message_id']
    ad_text = message.text.strip()
    await state.update_data(ad_text=ad_text)
    await reklama.url_reklama.set()
    await message.bot.edit_message_text(
        text="Введите ссылку для рекламы (или выберите 'Пропустить ссылку'):",
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=skip_link_keyboard
    )

async def process_ad_url(message: Message, state: FSMContext):
    user_data = await state.get_data()
    chat_id = user_data['chat_id']
    message_id = user_data['message_id']
    link = message.text.strip()

    try:
        await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except Exception as e:
        logging.error(f"Ошибка при удалении сообщения: {e}")

    if not link:
        link = None

    await state.update_data(ad_link=link)
    await reklama.pic_reklama.set()
    await message.bot.edit_message_text(
        text="Прикрепите изображение для рекламы (или выберите 'Пропустить изображение'):",
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=skip_image_keyboard
    )

async def process_skip_link(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.bot.answer_callback_query(callback_query.id)
    user_data = await state.get_data()
    chat_id = user_data['chat_id']
    message_id = user_data['message_id']

    await state.update_data(ad_link=None)
    await reklama.pic_reklama.set()
    await callback_query.message.bot.edit_message_text(
        text="Прикрепите изображение для рекламы (или выберите 'Пропустить изображение'):",
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=skip_image_keyboard
    )

async def process_ad_image(message: Message, state: FSMContext):
    user_data = await state.get_data()
    chat_id = user_data['chat_id']
    message_id = user_data['message_id']
    ad_text = user_data['ad_text']
    ad_link = user_data.get('ad_link', None)
    photo = message.photo[-1]
    photo_id = photo.file_id
    await state.update_data(ad_image=photo_id)
    await reklama.broadcast_confirmation.set()

    preview_text = f"📢 Превью рекламы:\n\n{ad_text}\n\n"
    preview_text += f"Ссылка: {ad_link if ad_link else 'Не указана'}"

    sent_message = await message.bot.send_photo(
        chat_id=chat_id,
        photo=photo_id,
        caption=preview_text + "\n\nОтправить рассылку всем пользователям?",
        reply_markup=broadcast_keyboard
    )
    await state.update_data(messages_to_delete=user_data['messages_to_delete'] + [sent_message.message_id])
    try:
        await message.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        logging.error(f"Ошибка при удалении старого сообщения: {e}")

async def process_skip_image(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.bot.answer_callback_query(callback_query.id)
    user_data = await state.get_data()
    chat_id = user_data['chat_id']
    message_id = user_data['message_id']
    ad_text = user_data['ad_text']
    ad_link = user_data.get('ad_link', None)

    await reklama.broadcast_confirmation.set()
    await callback_query.message.bot.edit_message_text(
        text=f"📢 Превью рекламы:\n\n{ad_text}\n\nСсылка: {ad_link if ad_link else 'Не указана'}\n\nОтправить рассылку всем пользователям?",
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=broadcast_keyboard
    )

async def process_broadcast_confirmation(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.bot.answer_callback_query(callback_query.id)
    user_data = await state.get_data()
    chat_id = user_data['chat_id']
    messages_to_delete = user_data.get('messages_to_delete', [])
    ad_text = user_data['ad_text']
    ad_link = user_data.get('ad_link', None)
    ad_image = user_data.get('ad_image', None)

    messages_to_delete.append(callback_query.message.message_id)

    if callback_query.data == 'confirm_broadcast':
        users = get_all_users()
        success_count = 0
        fail_count = 0

        for user in users:
            user_id = user[0]
            try:
                ad_keyboard = create_ad_keyboard(ad_link)
                if ad_image:
                    await callback_query.message.bot.send_photo(
                        chat_id=user_id,
                        photo=ad_image,
                        caption=ad_text,
                        reply_markup=ad_keyboard
                    )
                else:
                    await callback_query.message.bot.send_message(
                        chat_id=user_id,
                        text=ad_text,
                        reply_markup=ad_keyboard
                    )
                success_count += 1
                await asyncio.sleep(0.1)
            except Exception as e:
                logging.error(f"Ошибка при отправке рекламы пользователю {user_id}: {e}")
                fail_count += 1

        for msg_id in messages_to_delete:
            try:
                await callback_query.message.bot.delete_message(chat_id=chat_id, message_id=msg_id)
            except Exception as e:
                logging.error(f"Ошибка при удалении сообщения {msg_id}: {e}")

        await callback_query.message.bot.send_message(
            chat_id=chat_id,
            text=f"✅ Рассылка завершена!\nУспешно отправлено: {success_count}\nНе удалось отправить: {fail_count}",
            reply_markup=re_reklama
        )
    elif callback_query.data == 'cancel_ad':
        for msg_id in messages_to_delete:
            try:
                await callback_query.message.bot.delete_message(chat_id=chat_id, message_id=msg_id)
            except Exception as e:
                logging.error(f"Ошибка при удалении сообщения {msg_id}: {e}")

        await callback_query.message.bot.send_message(
            chat_id=chat_id,
            text="Создание рекламы отменено",
            reply_markup=re_reklama
        )
    await state.finish()

async def process_delete_ad_message(callback_query: CallbackQuery):
    await callback_query.message.bot.answer_callback_query(callback_query.id)
    try:
        await callback_query.message.bot.delete_message(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id
        )
    except Exception as e:
        logging.error(f"Ошибка при удалении рекламного сообщения: {e}")
        await callback_query.message.bot.answer_callback_query(
            callback_query.id,
            text="Не удалось удалить сообщение",
            show_alert=True
        )

def register_advertisement_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(process_text, lambda c: c.data == 'dobavka')
    dp.register_message_handler(process_ad_text, state=reklama.text_reklama)
    dp.register_message_handler(process_ad_url, state=reklama.url_reklama)
    dp.register_callback_query_handler(process_skip_link, lambda c: c.data == 'skip_link', state=reklama.url_reklama)
    dp.register_message_handler(process_ad_image, content_types=['photo'], state=reklama.pic_reklama)
    dp.register_callback_query_handler(process_skip_image, lambda c: c.data == 'skip_image', state=reklama.pic_reklama)
    dp.register_callback_query_handler(process_broadcast_confirmation, lambda c: c.data in ['confirm_broadcast', 'cancel_ad'], state=reklama.broadcast_confirmation)
    dp.register_callback_query_handler(process_delete_ad_message, lambda c: c.data == 'delete_ad_message')