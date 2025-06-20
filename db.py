import os
import mysql.connector
from dotenv import load_dotenv

# .env fayldan sozlamalarni yuklash
load_dotenv()

# Bazaga ulanish
def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", 3306)),
    )

# Pasport raqami mavjudmi? (True/False)
def passport_exists(pasport: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE pasport = %s", (pasport,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result is not None

# Foydalanuvchining barcha ma'lumotlarini olish
def get_user_by_passport(pasport: str):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE pasport = %s", (pasport,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

# Ma'lumotlarni saqlash
def save_user(data: dict):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (chat_id, phone, fio, pasport, jshshir, tugulgan_sana, jinsi, manzili, talim_muassasasi, rasm_path)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        data['chat_id'],
        data['phone'],
        data['fio'],
        data['pasport'],
        data['jshshir'],
        data['tugulgan_sana'],
        data['jinsi'],
        data['manzili'],
        data['talim_muassasasi'],
        data['rasm_path']
    ))
    conn.commit()
    cursor.close()
    conn.close()
