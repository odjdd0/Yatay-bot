from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher import FSMContext
from keyboards import get_main_keyboard
from database import add_user, update_user_last_active

async def send_menu(message: Message, state: FSMContext = None):
    if state:
        await state.finish()
    user_id = message.from_user.id
    add_user(user_id)
    update_user_last_active(user_id)
    await message.answer(
        "📫Вас приветствует YATAY POIZON, ваш помощник покупки товаров с маркетплейса Poizon)",
        reply_markup=get_main_keyboard()
    )

async def handle_info(message: Message):
    if message.text == 'О нас📑':
        await message.answer(
            "❤️‍Мы — YATAY INTERNATIONAL, предоставляем оплату и доставку ваших товаров с маркетплейса Poizon и 95!\n"
            "🤖Наш бот поможет вам рассчитать товар с маркетплейса POIZON и 95❗️\n"
            "📉У нас самый низкий курс и самая быстрая доставка♻️\n"
            "🔒Мы предоставляем страхование и гарантии на ваш товар🌱\n"
            "📮У нас удобное оформление и лучшие менеджеры🤝\n"
            "📍Мы находимся в Томске, но отправляем по всей России❗️\n"
            "❤️Мы всегда рады покупателям🌹"
            "✅Наш канал: https://t.me/YATAYPOIZON\n"
            #"📱Основной менеджер: @ttt777788\n"
            "📞Менеджер: @promoutermuhamad\n"
            "☎️Техподдержка: @Episthema",
            reply_markup=get_main_keyboard()
        )
    elif message.text == 'Доставка📦':
        await message.answer(
            "Мы предоставляем три вида доставки:\n"
            "1) Самая Дешёвая Доставка\n"
            "Доставка путём карго. Мы возим пулом, из-за чего цены минимализируются, но уменьшает скорость\n"
            "Цена: 40 юаней за кг (подсчёт в боте по актуальному курсу)\n"
            "Сроки: 3-6 недель\n\n"
            "2) Быстрая Доставка\n"
            "Доставка на самолёте. Цена значительно выше, но скорость доставки увеличивается\n"
            "Цена: 170 юаней за кг (подсчёт в боте по актуальному курсу)\n"
            "Сроки: 1-2 недели\n\n"
            "3) Самая Быстрая Доставка\n"
            "Мы передаём ваш заказ в руки нашего доставщика, который напрямую в самые короткие сроки добирается до Москвы. Дальше посылка отправится к вам по России\n"
            "Цена: 205 юаней за кг (подсчёт в боте по актуальному курсу) + доставка по России\n"
            "Сроки: до одной недели\n\n"
            "Доставка производится до Томска, откуда дальше мы вам передадим любым удобным способом (оплачивается за ваш счёт)\n"
            "О доставке аксессуаров и техники договаривайтесь с нашим менеджером напрямую.\n"
            "Мы предоставляем страхование (условие во время выполнения самого заказа. За содержание товара и оригинальность мы не несём ответственность).\n"
            "Минимальная стоимость услуги и страхования 500 рублей.\n\n"
            "Если у вас остались вопросы, обратитесь к старшему менеджеру: @promoutermuhamad",
            reply_markup=get_main_keyboard()
        )

# async def handle_reviews(message: Message):
#     await message.answer(
#         "https://t.me/yatayreviews\n"
#         "Отзывы отправляйте нашему менеджеру: @ttt777788"
#     )

def register_start_handlers(dp: Dispatcher):
    dp.register_message_handler(send_menu, commands=['start'], state='*')
    dp.register_message_handler(handle_info, lambda message: message.text in ["О нас📑", "Доставка📦"])
    #dp.register_message_handler(handle_reviews, lambda message: message.text == 'Отзывы и выкупы📓')