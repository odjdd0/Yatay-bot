from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("О нас📑"), KeyboardButton("К покупкам🛍"))
    keyboard.add(KeyboardButton("Курс💴"), KeyboardButton("Доставка📦"))
    keyboard.add(KeyboardButton("Мои заявки📔"))
    return keyboard

delivery_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
delivery_keyboard.add(KeyboardButton("Самая Быстрая Доставка (до недели)"))
delivery_keyboard.add(KeyboardButton("Быстрая Доставка (1-2 недели)"))
delivery_keyboard.add(KeyboardButton("Самая Дешевая Доставка (3-6 недель)"))
delivery_keyboard.add(KeyboardButton("◀️В главное меню"))

action_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
action_keyboard.add(KeyboardButton("Составить заявку🖊"))
action_keyboard.add(KeyboardButton("Написать менеджеру✏️"))
action_keyboard.add(KeyboardButton("◀️В главное меню"))

confirm_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
confirm_keyboard.add(KeyboardButton("Да, отправить✅"))
confirm_keyboard.add(KeyboardButton("Нет, вернуться в меню❌"))

weight_key = ReplyKeyboardMarkup(resize_keyboard=True)
weight_key.add(KeyboardButton("Обувь"), KeyboardButton("Одежда"), KeyboardButton("Аксессуары и техника"))
weight_key.add(KeyboardButton("◀️В главное меню"))

promo_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
promo_keyboard.add(KeyboardButton("Пропустить"))
promo_keyboard.add(KeyboardButton("◀️В главное меню"))

re_keyboard = InlineKeyboardMarkup()
re_keyboard.add(InlineKeyboardButton("Статистика", callback_data='opt1'))
re_keyboard.add(InlineKeyboardButton("Управление промокодами", callback_data='opt2'))
re_keyboard.add(InlineKeyboardButton("Поиск аккаунта по ID", callback_data='opt3'))
re_keyboard.add(InlineKeyboardButton("Управление базой данных", callback_data='opt4'))
re_keyboard.add(InlineKeyboardButton("Управление рекламой", callback_data='opt5'))
re_keyboard.add(InlineKeyboardButton("ВЫХОД ИЗ РЕЖИМА", callback_data='exit'))

inline_back = InlineKeyboardMarkup()
inline_back.add(InlineKeyboardButton("Назад", callback_data='back'))

re_opt4 = InlineKeyboardMarkup()
re_opt4.add(InlineKeyboardButton("Очистить базу данных", callback_data='deleteall'))
re_opt4.add(InlineKeyboardButton("Назад", callback_data='back'))

re_opt2 = InlineKeyboardMarkup()
re_opt2.add(InlineKeyboardButton("Список промокодов", callback_data='allpromo'))
re_opt2.add(InlineKeyboardButton("Добавить промокод", callback_data='addpromo'))
re_opt2.add(InlineKeyboardButton("Удалить промокод", callback_data='deletepromo'))
re_opt2.add(InlineKeyboardButton("Назад", callback_data='back'))

re_opt3 = InlineKeyboardMarkup()
re_opt3.add(InlineKeyboardButton("Добавленные ID", callback_data='allid'))
re_opt3.add(InlineKeyboardButton("Найти по ID", callback_data='search'))
re_opt3.add(InlineKeyboardButton("Назад", callback_data='back'))

re_delall = InlineKeyboardMarkup()
re_delall.add(InlineKeyboardButton("Да, выбрать удаление", callback_data='yesss'))
re_delall.add(InlineKeyboardButton("Нет, отмена", callback_data='back'))

re_reklama = InlineKeyboardMarkup()
re_reklama.add(InlineKeyboardButton("Создать новый пост", callback_data='dobavka'))
re_reklama.add(InlineKeyboardButton("Назад", callback_data='back'))

promo_type_keyboard = InlineKeyboardMarkup()
promo_type_keyboard.add(InlineKeyboardButton("Процентная скидка", callback_data='percent_promo'))
promo_type_keyboard.add(InlineKeyboardButton("Скидка на услугу (0 RUB)", callback_data='service_promo'))
promo_type_keyboard.add(InlineKeyboardButton("Отмена", callback_data='cancel_promo'))

skip_link_keyboard = InlineKeyboardMarkup()
skip_link_keyboard.add(InlineKeyboardButton("Пропустить ссылку", callback_data='skip_link'))

skip_image_keyboard = InlineKeyboardMarkup()
skip_image_keyboard.add(InlineKeyboardButton("Пропустить изображение", callback_data='skip_image'))

broadcast_keyboard = InlineKeyboardMarkup()
broadcast_keyboard.add(InlineKeyboardButton("Отправить рассылку", callback_data='confirm_broadcast'))
broadcast_keyboard.add(InlineKeyboardButton("Отменить", callback_data='cancel_ad'))

def create_ad_keyboard(ad_link=None):
    keyboard = InlineKeyboardMarkup()
    if ad_link:
        if not ad_link.startswith(('http://', 'https://')):
            ad_link = f"https://{ad_link}"
        keyboard.add(InlineKeyboardButton("Ссылка", url=ad_link))
    keyboard.add(InlineKeyboardButton("❌Удалить сообщение❌", callback_data='delete_ad_message'))
    return keyboard

def create_pagination_keyboard(current_page, total_pages):
    keyboard = InlineKeyboardMarkup()
    if current_page > 0:
        keyboard.add(InlineKeyboardButton("⬅️ Назад", callback_data=f'prev_page_{current_page}'))
    if current_page < total_pages - 1:
        keyboard.add(InlineKeyboardButton("Вперед ➡️", callback_data=f'next_page_{current_page}'))
    keyboard.add(InlineKeyboardButton("На главную", callback_data='back'))
    return keyboard