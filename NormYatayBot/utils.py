import aiohttp
import logging
import time

# Кэш для хранения курса и времени последнего запроса
_exchange_rate_cache = None
_cache_timestamp = 0
_CACHE_DURATION = 3600

async def get_exchange_rate():
    global _exchange_rate_cache, _cache_timestamp
    current_time = time.time()

    # Проверяем, есть ли актуальный курс в кэше
    if _exchange_rate_cache and (current_time - _cache_timestamp) < _CACHE_DURATION:
        logging.info("Используется кэшированный курс валют")
        return _exchange_rate_cache

    try:
        # Устанавливаем таймаут на 5 секунд
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.exchangerate-api.com/v4/latest/CNY",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    exchange_rate = data["rates"]["RUB"] + 0.5
                    _exchange_rate_cache = exchange_rate
                    _cache_timestamp = current_time
                    logging.info(f"Получен курс валют: {exchange_rate:.2f}")
                    return exchange_rate
                else:
                    logging.error(f"Ошибка API: статус {response.status}")
                    return None
    except aiohttp.ClientError as e:
        logging.error(f"Ошибка при получении курса: {e}")
        return None
    except Exception as e:
        logging.error(f"Неизвестная ошибка при получении курса: {e}")
        return None