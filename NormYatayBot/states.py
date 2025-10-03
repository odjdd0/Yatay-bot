from aiogram.dispatcher.filters.state import State, StatesGroup

class Form(StatesGroup):
    delivery_type1 = State()
    product_cost = State()
    weight = State()
    promo_code = State()
    contact_user = State()
    product_user = State()
    confirm_application = State()
    admin = State()
    admin_panel = State()

class AdminActions(StatesGroup):
    waiting_for_delete_code = State()

class PromoCodeStates(StatesGroup):
    waiting_for_new_promo = State()
    waiting_for_promo_type = State()
    waiting_for_promo_details = State()
    waiting_for_service_promo_uses = State()
    waiting_for_delete_promo = State()

class SearchStates(StatesGroup):
    waiting_for_id = State()

class reklama(StatesGroup):
    text_reklama = State()
    url_reklama = State()
    pic_reklama = State()
    broadcast_confirmation = State()