from aiogram import Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher import FSMContext
from keyboards import delivery_keyboard, action_keyboard, confirm_keyboard, weight_key, promo_keyboard
from states import Form
from utils import get_exchange_rate
from database import save_order, get_promo_code, update_promo_uses, cursor, get_user_orders
from .start import send_menu
import logging

calculation_data = {}

async def start_order(message: Message):
    await Form.delivery_type1.set()
    await message.answer("📍Выберите тип доставки📦", reply_markup=delivery_keyboard)

async def process_delivery_type(message: Message, state: FSMContext):
    if message.text == "◀️В главное меню":
        await state.finish()
        from handlers.start import send_menu
        await send_menu(message)
        return
    prikol1 = ReplyKeyboardMarkup(resize_keyboard=True)
    prikol1.add(KeyboardButton("Введите стоимость в юанях💴"))
    prikol1.add(KeyboardButton("◀️В главное меню"))
    await state.update_data(delivery_type1=message.text)
    await Form.next()
    await message.answer("📍Укажите стоимость товара в юанях💴", reply_markup=prikol1)

async def process_product_cost(message: Message, state: FSMContext):
    if message.text == "◀️В главное меню":
        await state.finish()
        from handlers.start import send_menu
        await send_menu(message)
        return
    try:
        cost = float(message.text)
        if cost >= 0:
            await state.update_data(product_cost_cny=cost)
            await Form.next()
            await message.answer("📍Укажите тип товара📍\n", reply_markup=weight_key)
        else:
            await message.answer("Пожалуйста, введите неотрицательное число!")
    except ValueError:
        await message.answer("Пожалуйста, введите корректную стоимость (например, 100.50)!")

async def process_acses(message: Message, state: FSMContext):
    await message.answer("Для оформления такого типа товара обратитесь к менеджеру: @promoutermuhamad")
    await state.finish()
    from handlers.start import send_menu
    await send_menu(message)

async def process_weight(message: Message, state: FSMContext):
    if message.text == "◀️В главное меню":
        await state.finish()
        from handlers.start import send_menu
        await send_menu(message)
        return
    exchange_rate = await get_exchange_rate()
    if not exchange_rate:
        await message.answer("✖️Не удалось получить курс валют. Попробуйте позже.")
        return

    user_data = await state.get_data()
    delivery_type1 = user_data.get("delivery_type1")

    if message.text == "Обувь":
        if delivery_type1 == "Быстрая Доставка (1-2 недели)":
            cost_per_kg = 340
            service_percentage = 0.135
        elif delivery_type1 == "Самая Дешевая Доставка (3-6 недель)":
            cost_per_kg = 80
            service_percentage = 0.12
        elif delivery_type1 == "Самая Быстрая Доставка (до недели)":
            cost_per_kg = 410
            service_percentage = 0.15
    elif message.text == "Одежда":
        if delivery_type1 == "Быстрая Доставка (1-2 недели)":
            cost_per_kg = 170
            service_percentage = 0.135
        elif delivery_type1 == "Самая Дешевая Доставка (3-6 недель)":
            cost_per_kg = 40
            service_percentage = 0.12
        elif delivery_type1 == "Самая Быстрая Доставка (до недели)":
            cost_per_kg = 205
            service_percentage = 0.15

    delivery_cost_cny = cost_per_kg * exchange_rate
    product_cost_rub = user_data["product_cost_cny"] * exchange_rate
    service_cost = 500
    if product_cost_rub >= 5000:
        service_cost = min(4000, max(500, product_cost_rub * service_percentage))

    total_cost_rub = product_cost_rub + delivery_cost_cny + service_cost

    await state.update_data(
        delivery_cost_cny=delivery_cost_cny,
        product_cost_rub=product_cost_rub,
        service_cost=service_cost,
        total_cost_rub_before_discount=total_cost_rub,
        weight=message.text
    )

    calculation_data[message.from_user.id] = {
        "product_cost_cny": user_data["product_cost_cny"],
        "total_cost_rub": total_cost_rub,
        "delivery_type1": delivery_type1,
        "service_cost": service_cost,
        "discount_percentage": 0.0,
        "promo_code": None,
        "weight": message.text
    }

    await Form.promo_code.set()
    await message.answer("📍Введите промокод (или нажмите 'Пропустить'):", reply_markup=promo_keyboard)

async def process_promo_code(message: Message, state: FSMContext):
    if message.text == "◀️В главное меню":
        await state.finish()
        from handlers.start import send_menu
        await send_menu(message)
        return

    user_data = await state.get_data()
    promo_code = None
    discount_percentage = 0.0
    service_cost = user_data["service_cost"]
    final_total_cost_rub = user_data["total_cost_rub_before_discount"]
    delivery_cost_cny = user_data["delivery_cost_cny"]
    user_id = message.from_user.id

    if message.text != "Пропустить":
        promo_code = message.text.strip()
        result = get_promo_code(promo_code)

        if result and result[1] > 0:
            discount_percentage = result[0]
            if discount_percentage == 0.0:
                cursor.execute("SELECT COUNT(*) FROM orders WHERE user_id = ? AND promo_code = ?",
                               (user_id, promo_code))
                promo_used_count = cursor.fetchone()[0]

                if promo_used_count == 0:
                    service_cost = 0.0
                    final_total_cost_rub = user_data["product_cost_rub"] + user_data["delivery_cost_cny"]
                    await message.answer(
                        f"✅ Промокод '{promo_code}' применен! Стоимость услуги и страхования (={user_data['service_cost']:.2f} RUB) убрана.")
                else:
                    await message.answer(
                        f"⚠️ Вы уже использовали промокод '{promo_code}'. Он доступен только один раз.")
                    promo_code = None
            else:
                discount_amount = (service_cost + delivery_cost_cny) * (discount_percentage / 100)
                final_total_cost_rub -= discount_amount
                await message.answer(f"✅ Промокод '{promo_code}' применен! Скидка на услугу: {discount_percentage}%")

            update_promo_uses(promo_code)
        else:
            await message.answer("⚠️ Промокод недействителен или исчерпан. Расчет без скидки.")
    else:
        await message.answer("📍Промокод не применен.")

    calculation_data[message.from_user.id].update({
        "total_cost_rub": final_total_cost_rub,
        "service_cost": service_cost,
        "discount_percentage": discount_percentage,
        "promo_code": promo_code
    })

    await message.answer(
        f"📍Стоимость товара: {user_data['product_cost_cny']:.2f} CNY (~{user_data['product_cost_rub']:.2f} RUB)\n"
        f"📍Стоимость доставки: {user_data['delivery_cost_cny']:.2f} RUB\n"
        f"📍Стоимость услуги и страхования: {service_cost:.2f} RUB\n"
        f"📍Промокод: {promo_code if promo_code else 'Не применен'}\n"
        f"📍Скидка: {discount_percentage:.1f}% ({(user_data['total_cost_rub_before_discount'] - final_total_cost_rub):.2f} RUB)\n"
        f"📍Общая стоимость: {final_total_cost_rub:.2f} RUB\n\n"
        f"Хотите оформить заказ❓",
        reply_markup=action_keyboard
    )
    await state.finish()

async def start_application(message: Message):
    await Form.contact_user.set()
    await message.answer("📒Укажите как с вами связаться:")

async def process_contact_user(message: Message, state: FSMContext):
    key_mes = ReplyKeyboardMarkup(resize_keyboard=True)
    key_mes.add(KeyboardButton("-"))
    input_text = message.text.strip()
    is_telegram = input_text.startswith('@') and len(input_text) > 1 and input_text[1:].isalnum()
    is_phone = input_text.startswith('+') and input_text[1:].isdigit() and len(input_text) >= 7

    if is_telegram or is_phone:
        await state.update_data(contact_user=input_text)
        await Form.next()
        await message.answer(
            "🗄Опишите детали вашего заказа!\n"
            "Укажите размер, как отправить вам в дальнейшем из Томска и т.д.",
            reply_markup=key_mes
        )
    else:
        await message.answer(
            "❗️Пожалуйста, укажите Telegram-юзернейм (например, @username) или номер телефона (например, +7**********)❗️"
        )

async def process_product1(message: Message, state: FSMContext):
    user_data = await state.get_data()
    product = message.text

    user_calculation_data = calculation_data.get(message.from_user.id, {})
    if not user_calculation_data.get("product_cost_cny") or not user_calculation_data.get("delivery_type1"):
        await message.answer("Пожалуйста, начните оформление заказа заново через 'К покупкам🛍'.")
        await state.finish()
        from handlers.start import send_menu
        await send_menu(message)
        return

    product_cost_cny = user_calculation_data.get("product_cost_cny")
    weight = user_calculation_data.get("weight")
    total_cost_rub = user_calculation_data.get("total_cost_rub")
    delivery_type1 = user_calculation_data.get("delivery_type1")

    await state.update_data(
        product=product,
        delivery_type1=delivery_type1,
        product_cost_cny=product_cost_cny,
        weight=weight,
        total_cost_rub=total_cost_rub,
        user_id=message.from_user.id
    )

    application_summary = (
        f"Ваша заявка:\n\n"
        f"📍Доставка до Томска: {delivery_type1}\n"
        f"📍Тип товара: {weight}\n"
        f"📘Контактные данные: {user_data['contact_user']}\n"
        f"🗄Описание: {product}\n"
        f"📍Стоимость товара: {product_cost_cny} CNY\n"
        f"📍Общая стоимость: {total_cost_rub} RUB\n\n"
        f"Вы согласны с этой заявкой❓"
    )

    await Form.confirm_application.set()
    await message.answer(application_summary, reply_markup=confirm_keyboard)

async def confirm_application(message: Message, state: FSMContext):
    from config import MANAGER_CHAT_ID
    if message.text == "Да, отправить✅":
        user_data = await state.get_data()
        user_calculation_data = calculation_data.get(message.from_user.id, {})
        service_cost = user_calculation_data.get("service_cost", 500)
        promo_code = user_calculation_data.get("promo_code", None)
        discount_percentage = user_calculation_data.get("discount_percentage", 0.0)

        order_id, error = save_order(
            message.from_user.id,
            user_data.get("delivery_type1"),
            user_data["product"],
            user_data["contact_user"],
            user_data.get("product_cost_cny"),
            user_data.get("weight"),
            user_data.get("total_cost_rub"),
            promo_code,
            discount_percentage
        )

        if order_id is not None:
            manager_message = (
                f"Новая заявка!\n"
                f"User ID: {message.from_user.id}\n\n"
                f"ID: {order_id}\n"
                f"Доставка1: {user_data.get('delivery_type1')}\n"
                f"Контактные данные: {user_data['contact_user']}\n"
                f"Товар: {user_data['product']}\n"
                f"Стоимость товара: {user_data.get('product_cost_cny')} CNY\n"
                f"Стоимость услуги: {service_cost:.2f} RUB\n"
                f"Промокод: {promo_code if promo_code else 'Не применен'}\n"
                f"Скидка: {discount_percentage:.1f}%\n"
                f"Общая стоимость: {user_data.get('total_cost_rub')} RUB"
            )

            try:
                await message.bot.send_message(MANAGER_CHAT_ID, manager_message)
            except Exception as e:
                logging.error(f"Ошибка при отправке сообщения менеджеру: {e}")
                await message.answer("Заявка сохранена, но не удалось уведомить менеджера.")

            main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            main_keyboard.add(KeyboardButton("◀️В главное меню"))
            main_keyboard.add(KeyboardButton("Написать менеджеру✏️"))
            await message.answer("Ваша заявка отправлена менеджеру✅ ", reply_markup=main_keyboard)
            calculation_data.pop(message.from_user.id, None)
        else:
            logging.error(f"Ошибка при сохранении заявки: {error}")
            await message.answer("Произошла ошибка при сохранении заявки. Пожалуйста, свяжитесь с техподдержкой: @odjdd0")
    elif message.text == "Нет, вернуться в меню❌":
        from handlers.start import send_menu
        await send_menu(message)

    await state.finish()

async def show_applications(message: Message):
    orders = get_user_orders(message.from_user.id)
    if not orders:
        await message.answer("У вас пока нет заявок✖️")
        return

    applications_text = "Ваши заявки🖊:\n\n"
    for app in orders:
        applications_text += (
            f"📍ID: {app[0]}\n"
            f"📍Доставка до Томска: {app[2]}\n"
            f"📍Товар: {app[3]}\n"
            f"📍Контактные данные: {app[4]}\n"
            f"📍Стоимость товара: {app[5]} CNY\n"
            f"📍Общая стоимость: {app[7]} RUB\n\n"
        )

    await message.answer(applications_text)

def register_order_handlers(dp: Dispatcher):
    dp.register_message_handler(start_order, lambda message: message.text == 'К покупкам🛍')
    dp.register_message_handler(process_delivery_type, lambda message: message.text in ["Самая Быстрая Доставка (до недели)", "Быстрая Доставка (1-2 недели)", "Самая Дешевая Доставка (3-6 недель)", "◀️В главное меню"], state=Form.delivery_type1)
    dp.register_message_handler(process_product_cost, state=Form.product_cost)
    dp.register_message_handler(process_acses, lambda message: message.text == "Аксессуары и техника", state=Form.weight)
    dp.register_message_handler(process_weight, lambda message: message.text in ["Обувь", "Одежда", "◀️В главное меню"], state=Form.weight)
    dp.register_message_handler(process_promo_code, state=Form.promo_code)
    dp.register_message_handler(start_application, lambda message: message.text == "Составить заявку🖊")
    dp.register_message_handler(process_contact_user, state=Form.contact_user)
    dp.register_message_handler(process_product1, state=Form.product_user)
    dp.register_message_handler(confirm_application, lambda message: message.text in ["Да, отправить✅", "Нет, вернуться в меню❌"], state=Form.confirm_application)
    dp.register_message_handler(show_applications, lambda message: message.text == "Мои заявки📔")