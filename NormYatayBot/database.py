import sqlite3
from config import DATABASE_PATH

conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
cursor = conn.cursor()

def init_db():
    cursor.execute("DROP TABLE IF EXISTS orders")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            delivery_type1 TEXT NOT NULL,
            product TEXT NOT NULL,
            contact_user TEXT NOT NULL,
            product_cost_cny REAL,
            weight TEXT,
            total_cost_rub REAL,
            promo_code TEXT,
            discount_percentage REAL DEFAULT 0.0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS promo_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL UNIQUE,
            discount_percentage REAL NOT NULL,
            max_uses INTEGER NOT NULL,
            uses_left INTEGER NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()

def close_db():
    conn.close()

def save_order(user_id, delivery_type1, product, contact_user, product_cost_cny, weight, total_cost_rub, promo_code, discount_percentage):
    try:
        cursor.execute('''
            INSERT INTO orders (user_id, delivery_type1, product, contact_user, product_cost_cny, weight, total_cost_rub, promo_code, discount_percentage)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, delivery_type1, product, contact_user, product_cost_cny, weight, total_cost_rub, promo_code, discount_percentage))
        conn.commit()
        return cursor.lastrowid, None  # Возвращаем order_id и None в случае успеха
    except sqlite3.Error as e:
        return None, str(e)  # Возвращаем None и текст ошибки в случае неудачи

def get_user_orders(user_id):
    cursor.execute('SELECT * FROM orders WHERE user_id = ?', (user_id,))
    return cursor.fetchall()

def get_promo_code(code):
    cursor.execute("SELECT discount_percentage, uses_left FROM promo_codes WHERE code = ?", (code,))
    return cursor.fetchone()

def update_promo_uses(code):
    cursor.execute("UPDATE promo_codes SET uses_left = uses_left - 1 WHERE code = ?", (code,))
    conn.commit()

def get_all_promo_codes():
    cursor.execute("SELECT code, discount_percentage, max_uses, uses_left FROM promo_codes")
    return cursor.fetchall()

def add_promo_code(code, discount_percentage, max_uses):
    cursor.execute('''
        INSERT INTO promo_codes (code, discount_percentage, max_uses, uses_left)
        VALUES (?, ?, ?, ?)
    ''', (code, discount_percentage, max_uses, max_uses))
    conn.commit()

def delete_promo_code(code):
    cursor.execute("DELETE FROM promo_codes WHERE code = ?", (code,))
    conn.commit()

def get_user_info(user_id):
    cursor.execute("SELECT user_id, first_seen, last_active FROM users WHERE user_id = ?", (user_id,))
    return cursor.fetchone()

def get_all_users(offset=0, limit=5):
    cursor.execute("SELECT user_id, first_seen, last_active FROM users LIMIT ? OFFSET ?", (limit, offset))
    return cursor.fetchall()

def get_total_users():
    cursor.execute("SELECT COUNT(*) FROM users")
    return cursor.fetchone()[0]

def update_user_last_active(user_id):
    cursor.execute("UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE user_id = ?", (user_id,))
    conn.commit()

def add_user(user_id):
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

def clear_database():
    cursor.execute("DELETE FROM orders")
    cursor.execute("DELETE FROM promo_codes")
    cursor.execute("DELETE FROM users")
    conn.commit()