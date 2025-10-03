import logging
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import API_TOKEN
from database import init_db, close_db
from handlers.start import register_start_handlers
from handlers.order import register_order_handlers
from handlers.admin import register_admin_handlers
from handlers.advertisement import register_advertisement_handlers
from handlers.common import register_common_handlers

logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)

def register_all_handlers(dp):
    register_start_handlers(dp)
    register_order_handlers(dp)
    register_admin_handlers(dp)
    register_advertisement_handlers(dp)
    register_common_handlers(dp)

if __name__ == '__main__':
    init_db()
    register_all_handlers(dp)
    try:
        executor.start_polling(dp, skip_updates=True)
    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}")
    finally:
        close_db()